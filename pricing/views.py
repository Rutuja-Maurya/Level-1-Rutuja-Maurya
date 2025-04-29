from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal
from .models import (
    PricingConfig,
    DistanceBasePrice,
    DistanceAdditionalPrice,
    TimeMultiplierFactor,
    WaitingCharge,
    PricingConfigLog
)
from .forms import (
    PricingConfigForm,
    DistanceBasePriceFormSet,
    DistanceAdditionalPriceFormSet,
    TimeMultiplierFactorFormSet,
    WaitingChargeFormSet
)

@login_required
def pricing_config_list(request):
    configs = PricingConfig.objects.all()
    return render(request, 'pricing/config_list.html', {'configs': configs})

@login_required
def pricing_config_create(request):
    if request.method == 'POST':
        form = PricingConfigForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                config = form.save()
                PricingConfigLog.objects.create(
                    pricing_config=config,
                    user=request.user,
                    action='created',
                    details={'name': config.name}
                )
                messages.success(request, 'Pricing configuration created successfully.')
                return redirect('pricing_config_detail', pk=config.pk)
    else:
        form = PricingConfigForm()
    return render(request, 'pricing/config_form.html', {'form': form})

@login_required
def pricing_config_edit(request, pk):
    config = get_object_or_404(PricingConfig, pk=pk)
    if request.method == 'POST':
        form = PricingConfigForm(request.POST, instance=config)
        base_price_formset = DistanceBasePriceFormSet(request.POST, instance=config)
        additional_price_formset = DistanceAdditionalPriceFormSet(request.POST, instance=config)
        time_multiplier_formset = TimeMultiplierFactorFormSet(request.POST, instance=config)
        waiting_charge_formset = WaitingChargeFormSet(request.POST, instance=config)

        if (form.is_valid() and base_price_formset.is_valid() and
            additional_price_formset.is_valid() and time_multiplier_formset.is_valid() and
            waiting_charge_formset.is_valid()):
            
            with transaction.atomic():
                config = form.save()
                base_price_formset.save()
                additional_price_formset.save()
                time_multiplier_formset.save()
                waiting_charge_formset.save()

                # Log the changes
                PricingConfigLog.objects.create(
                    pricing_config=config,
                    user=request.user,
                    action='updated',
                    details={
                        'name': config.name,
                        'is_active': config.is_active,
                        'base_prices_modified': base_price_formset.has_changed(),
                        'additional_prices_modified': additional_price_formset.has_changed(),
                        'time_multipliers_modified': time_multiplier_formset.has_changed(),
                        'waiting_charges_modified': waiting_charge_formset.has_changed(),
                    }
                )

                messages.success(request, 'Pricing configuration updated successfully.')
                return redirect('pricing_config_detail', pk=config.pk)
    else:
        form = PricingConfigForm(instance=config)
        base_price_formset = DistanceBasePriceFormSet(instance=config)
        additional_price_formset = DistanceAdditionalPriceFormSet(instance=config)
        time_multiplier_formset = TimeMultiplierFactorFormSet(instance=config)
        waiting_charge_formset = WaitingChargeFormSet(instance=config)

    return render(request, 'pricing/config_edit.html', {
        'form': form,
        'config': config,
        'base_price_formset': base_price_formset,
        'additional_price_formset': additional_price_formset,
        'time_multiplier_formset': time_multiplier_formset,
        'waiting_charge_formset': waiting_charge_formset,
    })

@login_required
def pricing_config_detail(request, pk):
    config = get_object_or_404(PricingConfig, pk=pk)
    base_prices = config.distance_base_prices.all()
    additional_prices = config.distance_additional_prices.all()
    time_multipliers = config.time_multipliers.all()
    waiting_charges = config.waiting_charges.all()
    change_logs = config.pricingconfiglog_set.all().order_by('-timestamp')[:10]
    
    return render(request, 'pricing/config_detail.html', {
        'config': config,
        'base_prices': base_prices,
        'additional_prices': additional_prices,
        'time_multipliers': time_multipliers,
        'waiting_charges': waiting_charges,
        'change_logs': change_logs,
    })

@api_view(['POST'])
def calculate_price(request):
    try:
        # Get input parameters
        distance = Decimal(request.data.get('distance', 0))  # Total distance in KM
        duration = int(request.data.get('duration', 0))      # Total duration in minutes
        waiting_time = int(request.data.get('waiting_time', 0))  # Total waiting time in minutes
        day_of_week = int(request.data.get('day_of_week', 0))   # Day of week (0-6, Monday-Sunday)

        # Get active pricing config
        config = PricingConfig.objects.filter(is_active=True).first()
        if not config:
            return Response({'error': 'No active pricing configuration found'}, status=400)

        # 1. Calculate Distance Base Price (DBP)
        base_price_config = config.distance_base_prices.filter(
            days_of_week__contains=[day_of_week]
        ).first()
        
        if not base_price_config:
            return Response({'error': f'No base price configuration found for day {day_of_week}'}, status=400)

        dbp = base_price_config.base_price
        
        # 2. Calculate Additional Distance Price (Dn * DAP)
        additional_distance = Decimal('0')
        additional_price = Decimal('0')
        
        if distance > base_price_config.base_distance:
            additional_distance = distance - base_price_config.base_distance
            additional_price_config = config.distance_additional_prices.first()
            if additional_price_config:
                additional_price = additional_distance * additional_price_config.price_per_km

        # Calculate base fare with distance components
        base_fare = dbp + additional_price

        # 3. Calculate Time Multiplier Factor (TMF)
        time_multiplier = Decimal('1.0')
        for multiplier in config.time_multipliers.all().order_by('-time_threshold'):
            if duration >= multiplier.time_threshold:
                time_multiplier = multiplier.multiplier
                break

        # Apply time multiplier to the base fare
        time_adjusted_fare = base_fare * time_multiplier

        # 4. Calculate Waiting Charges (WC)
        waiting_charge = Decimal('0')
        waiting_config = config.waiting_charges.first()
        if waiting_config and waiting_time > waiting_config.initial_wait_time:
            chargeable_waiting_time = waiting_time - waiting_config.initial_wait_time
            # Calculate full intervals, rounding up
            intervals = (chargeable_waiting_time + waiting_config.interval_minutes - 1) // waiting_config.interval_minutes
            waiting_charge = intervals * waiting_config.charge_per_interval

        # Calculate final price: (DBP + (Dn * DAP)) * TMF + WC
        final_price = time_adjusted_fare + waiting_charge

        return Response({
            'breakdown': {
                'distance_base_price': float(dbp),
                'additional_distance': float(additional_distance),
                'additional_distance_price': float(additional_price),
                'time_multiplier': float(time_multiplier),
                'waiting_charge': float(waiting_charge),
                'waiting_time_details': {
                    'total_waiting_time': waiting_time,
                    'initial_free_time': waiting_config.initial_wait_time if waiting_config else 0,
                    'chargeable_time': chargeable_waiting_time if waiting_config and waiting_time > waiting_config.initial_wait_time else 0,
                    'charge_per_interval': float(waiting_config.charge_per_interval) if waiting_config else 0,
                    'interval_minutes': waiting_config.interval_minutes if waiting_config else 0,
                    'intervals_charged': int(intervals) if waiting_config and waiting_time > waiting_config.initial_wait_time else 0
                }
            },
            'base_fare': float(base_fare),
            'time_adjusted_fare': float(time_adjusted_fare),
            'final_price': float(final_price)
        })

    except Exception as e:
        return Response({'error': str(e)}, status=400)

def pricing_config_delete(request, pk):
    config = get_object_or_404(PricingConfig, pk=pk)
    if request.method == 'POST':
        # Log the deletion
        PricingConfigLog.objects.create(
            pricing_config=config,
            user=request.user,
            action='DELETE',
            details={'name': config.name}
        )
        config.delete()
        messages.success(request, f'Pricing configuration "{config.name}" has been deleted.')
        return redirect('pricing_config_list')
    return render(request, 'pricing/config_confirm_delete.html', {'config': config})

@login_required
def price_calculator(request):
    return render(request, 'pricing/price_calculator.html') 