from django.db import models
from django.contrib.auth.models import User

class PricingConfig(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class DistanceBasePrice(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='distance_base_prices')
    days_of_week = models.JSONField(help_text="List of days (0-6) this price applies to")
    base_distance = models.DecimalField(max_digits=5, decimal_places=2, help_text="Distance in kilometers")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.base_price} INR up to {self.base_distance}KM"

    def get_day_names(self):
        day_dict = dict(self.DAYS_OF_WEEK)
        return [day_dict[int(day)] for day in self.days_of_week]

class DistanceAdditionalPrice(models.Model):
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='distance_additional_prices')
    price_per_km = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.price_per_km} INR/KM"

class TimeMultiplierFactor(models.Model):
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='time_multipliers')
    time_threshold = models.IntegerField(help_text="Time threshold in minutes")
    multiplier = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"{self.multiplier}x after {self.time_threshold} minutes"

class WaitingCharge(models.Model):
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE, related_name='waiting_charges')
    initial_wait_time = models.IntegerField(help_text="Initial free waiting time in minutes")
    charge_per_interval = models.DecimalField(max_digits=10, decimal_places=2)
    interval_minutes = models.IntegerField(help_text="Interval in minutes for charging")

    def __str__(self):
        return f"{self.charge_per_interval} INR per {self.interval_minutes} minutes after {self.initial_wait_time} minutes"

class PricingConfigLog(models.Model):
    pricing_config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField()

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}" 