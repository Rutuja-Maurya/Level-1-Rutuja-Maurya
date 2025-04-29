from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import (
    PricingConfig,
    DistanceBasePrice,
    DistanceAdditionalPrice,
    TimeMultiplierFactor,
    WaitingCharge
)

class PricingConfigForm(forms.ModelForm):
    class Meta:
        model = PricingConfig
        fields = ['name', 'is_active']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError('Name must be at least 3 characters long')
        return name

class DistanceBasePriceForm(forms.ModelForm):
    days_of_week = forms.MultipleChoiceField(
        choices=DistanceBasePrice.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = DistanceBasePrice
        fields = ['days_of_week', 'base_distance', 'base_price']

    def clean_days_of_week(self):
        days = self.cleaned_data.get('days_of_week')
        if not days:
            raise ValidationError('Please select at least one day')
        try:
            days = [int(day) for day in days]
            if not all(0 <= day <= 6 for day in days):
                raise ValidationError('Invalid day value. Days must be between 0 and 6')
        except ValueError:
            raise ValidationError('Invalid day value. Days must be integers between 0 and 6')
        return days

    def clean_base_distance(self):
        distance = self.cleaned_data.get('base_distance')
        if distance <= 0:
            raise ValidationError('Base distance must be greater than 0')
        return distance

    def clean_base_price(self):
        price = self.cleaned_data.get('base_price')
        if price <= 0:
            raise ValidationError('Base price must be greater than 0')
        return price

class DistanceAdditionalPriceForm(forms.ModelForm):
    class Meta:
        model = DistanceAdditionalPrice
        fields = ['price_per_km']

    def clean_price_per_km(self):
        price = self.cleaned_data.get('price_per_km')
        if price <= 0:
            raise ValidationError('Price per km must be greater than 0')
        return price

class TimeMultiplierFactorForm(forms.ModelForm):
    class Meta:
        model = TimeMultiplierFactor
        fields = ['time_threshold', 'multiplier']

    def clean_time_threshold(self):
        threshold = self.cleaned_data.get('time_threshold')
        if threshold <= 0:
            raise ValidationError('Time threshold must be greater than 0')
        return threshold

    def clean_multiplier(self):
        multiplier = self.cleaned_data.get('multiplier')
        if multiplier <= 0:
            raise ValidationError('Multiplier must be greater than 0')
        return multiplier

class WaitingChargeForm(forms.ModelForm):
    class Meta:
        model = WaitingCharge
        fields = ['initial_wait_time', 'charge_per_interval', 'interval_minutes']

    def clean_initial_wait_time(self):
        time = self.cleaned_data.get('initial_wait_time')
        if time < 0:
            raise ValidationError('Initial wait time cannot be negative')
        return time

    def clean_charge_per_interval(self):
        charge = self.cleaned_data.get('charge_per_interval')
        if charge <= 0:
            raise ValidationError('Charge per interval must be greater than 0')
        return charge

    def clean_interval_minutes(self):
        interval = self.cleaned_data.get('interval_minutes')
        if interval <= 0:
            raise ValidationError('Interval minutes must be greater than 0')
        return interval

# Create formsets for inline editing
DistanceBasePriceFormSet = inlineformset_factory(
    PricingConfig,
    DistanceBasePrice,
    form=DistanceBasePriceForm,
    extra=1,
    can_delete=True
)

DistanceAdditionalPriceFormSet = inlineformset_factory(
    PricingConfig,
    DistanceAdditionalPrice,
    form=DistanceAdditionalPriceForm,
    extra=1,
    can_delete=True
)

TimeMultiplierFactorFormSet = inlineformset_factory(
    PricingConfig,
    TimeMultiplierFactor,
    form=TimeMultiplierFactorForm,
    extra=1,
    can_delete=True
)

WaitingChargeFormSet = inlineformset_factory(
    PricingConfig,
    WaitingCharge,
    form=WaitingChargeForm,
    extra=1,
    can_delete=True
) 