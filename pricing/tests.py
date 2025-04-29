from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import (
    PricingConfig,
    DistanceBasePrice,
    DistanceAdditionalPrice,
    TimeMultiplierFactor,
    WaitingCharge
)

class PriceCalculationTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

        # Create test pricing configuration
        self.config = PricingConfig.objects.create(
            name="Standard Pricing",
            is_active=True
        )

        # Create base prices for different days
        # Monday, Saturday (0, 5): 90 INR up to 3.5 KM
        DistanceBasePrice.objects.create(
            pricing_config=self.config,
            days_of_week=[0, 5],
            base_distance=Decimal('3.5'),
            base_price=Decimal('90')
        )

        # Tuesday, Wednesday, Thursday (1, 2, 3): 80 INR up to 3 KM
        DistanceBasePrice.objects.create(
            pricing_config=self.config,
            days_of_week=[1, 2, 3],
            base_distance=Decimal('3'),
            base_price=Decimal('80')
        )

        # Sunday (6): 95 INR up to 3.5 KM
        DistanceBasePrice.objects.create(
            pricing_config=self.config,
            days_of_week=[6],
            base_distance=Decimal('3.5'),
            base_price=Decimal('95')
        )

        # Create additional price per KM
        DistanceAdditionalPrice.objects.create(
            pricing_config=self.config,
            price_per_km=Decimal('30')
        )

        # Create time multiplier factors
        # Under 1 hour (60 minutes) - 1x
        TimeMultiplierFactor.objects.create(
            pricing_config=self.config,
            time_threshold=0,
            multiplier=Decimal('1')
        )
        # 1-2 hours (120 minutes) - 1.25x
        TimeMultiplierFactor.objects.create(
            pricing_config=self.config,
            time_threshold=60,
            multiplier=Decimal('1.25')
        )
        # 2-3 hours (180 minutes) - 2.2x
        TimeMultiplierFactor.objects.create(
            pricing_config=self.config,
            time_threshold=120,
            multiplier=Decimal('2.2')
        )

        # Create waiting charges
        # 5 INR per 3 minutes after initial 3 minutes
        WaitingCharge.objects.create(
            pricing_config=self.config,
            initial_wait_time=3,
            charge_per_interval=Decimal('5'),
            interval_minutes=3
        )

    def test_basic_price_calculation(self):
        """Test basic price calculation for a weekday with no additional charges"""
        response = self.client.post(reverse('calculate_price'), {
            'distance': 3.0,  # Within base distance
            'duration': 30,   # Within first hour
            'waiting_time': 2, # Within free waiting time
            'day_of_week': 2  # Wednesday
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['final_price'], 80.0)  # Base price only
        self.assertEqual(data['breakdown']['waiting_charge'], 0.0)  # No waiting charge

    def test_additional_distance_price(self):
        """Test price calculation with additional distance"""
        response = self.client.post(reverse('calculate_price'), {
            'distance': 5.0,  # 2 KM over base distance
            'duration': 30,   # Within first hour
            'waiting_time': 2, # Within free waiting time
            'day_of_week': 2  # Wednesday
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Base price (80) + Additional 2 KM * 30 = 80 + 60 = 140
        self.assertEqual(data['final_price'], 140.0)

    def test_time_multiplier(self):
        """Test price calculation with time multiplier"""
        response = self.client.post(reverse('calculate_price'), {
            'distance': 5.0,  # 2 KM over base distance
            'duration': 90,   # Between 1-2 hours (1.25x)
            'waiting_time': 2, # Within free waiting time
            'day_of_week': 2  # Wednesday
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # (Base price (80) + Additional 2 KM * 30) * 1.25 = 140 * 1.25 = 175
        self.assertEqual(data['final_price'], 175.0)

    def test_waiting_charges(self):
        """Test price calculation with waiting charges"""
        response = self.client.post(reverse('calculate_price'), {
            'distance': 3.0,  # Within base distance
            'duration': 30,   # Within first hour
            'waiting_time': 10, # 7 minutes chargeable (3 intervals)
            'day_of_week': 2  # Wednesday
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Base price (80) + Waiting charge (3 intervals * 5) = 80 + 15 = 95
        self.assertEqual(data['final_price'], 95.0)
        self.assertEqual(data['breakdown']['waiting_charge'], 15.0)

    def test_complete_calculation(self):
        """Test price calculation with all factors"""
        response = self.client.post(reverse('calculate_price'), {
            'distance': 5.0,  # 2 KM over base distance
            'duration': 90,   # Between 1-2 hours (1.25x)
            'waiting_time': 10, # 7 minutes chargeable (3 intervals)
            'day_of_week': 2  # Wednesday
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # (Base price (80) + Additional 2 KM * 30) * 1.25 + Waiting charge (15)
        # = (80 + 60) * 1.25 + 15 = 140 * 1.25 + 15 = 175 + 15 = 190
        self.assertEqual(data['final_price'], 190.0)

    def test_sunday_pricing(self):
        """Test price calculation for Sunday"""
        response = self.client.post(reverse('calculate_price'), {
            'distance': 5.0,  # 1.5 KM over base distance
            'duration': 30,   # Within first hour
            'waiting_time': 2, # Within free waiting time
            'day_of_week': 6  # Sunday
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Base price (95) + Additional 1.5 KM * 30 = 95 + 45 = 140
        self.assertEqual(data['final_price'], 140.0)

    def test_invalid_day(self):
        """Test price calculation with invalid day"""
        response = self.client.post(reverse('calculate_price'), {
            'distance': 5.0,
            'duration': 30,
            'waiting_time': 2,
            'day_of_week': 7  # Invalid day
        }, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_invalid_days(self):
        """Test price calculation with various invalid days"""
        invalid_days = [-1, 7, 8, 100]  # Test negative, just above valid range, and large numbers
        
        for day in invalid_days:
            response = self.client.post(reverse('calculate_price'), {
                'distance': 5.0,
                'duration': 30,
                'waiting_time': 2,
                'day_of_week': day
            }, content_type='application/json')

            self.assertEqual(response.status_code, 400)
            data = response.json()
            self.assertIn('error', data)
            self.assertIn('No base price configuration found for day', data['error'])

    def test_missing_day(self):
        """Test price calculation with day 4 (Friday) which has no configuration"""
        response = self.client.post(reverse('calculate_price'), {
            'distance': 5.0,
            'duration': 30,
            'waiting_time': 2,
            'day_of_week': 4  # Friday - not configured in setup
        }, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('No base price configuration found for day', data['error'])

    def test_invalid_input_types(self):
        """Test price calculation with invalid input types"""
        test_cases = [
            {
                'distance': 'invalid',
                'duration': 30,
                'waiting_time': 2,
                'day_of_week': 2
            },
            {
                'distance': 5.0,
                'duration': 'invalid',
                'waiting_time': 2,
                'day_of_week': 2
            },
            {
                'distance': 5.0,
                'duration': 30,
                'waiting_time': 'invalid',
                'day_of_week': 2
            },
            {
                'distance': 5.0,
                'duration': 30,
                'waiting_time': 2,
                'day_of_week': 'invalid'
            }
        ]

        for test_case in test_cases:
            response = self.client.post(reverse('calculate_price'), 
                test_case, content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertIn('error', response.json()) 