from django.contrib import admin
from .models import (
    PricingConfig,
    DistanceBasePrice,
    DistanceAdditionalPrice,
    TimeMultiplierFactor,
    WaitingCharge,
    PricingConfigLog
)

class DistanceBasePriceInline(admin.TabularInline):
    model = DistanceBasePrice
    extra = 1

class DistanceAdditionalPriceInline(admin.TabularInline):
    model = DistanceAdditionalPrice
    extra = 1

class TimeMultiplierFactorInline(admin.TabularInline):
    model = TimeMultiplierFactor
    extra = 1

class WaitingChargeInline(admin.TabularInline):
    model = WaitingCharge
    extra = 1

@admin.register(PricingConfig)
class PricingConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    inlines = [
        DistanceBasePriceInline,
        DistanceAdditionalPriceInline,
        TimeMultiplierFactorInline,
        WaitingChargeInline,
    ]

@admin.register(PricingConfigLog)
class PricingConfigLogAdmin(admin.ModelAdmin):
    list_display = ('pricing_config', 'user', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('pricing_config__name', 'user__username')
    readonly_fields = ('pricing_config', 'user', 'action', 'timestamp', 'details') 