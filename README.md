# Delivery Management System - Pricing Module

A Django-based web application for managing delivery pricing configurations with dynamic calculations based on distance, time, and waiting charges.

## Features

### Pricing Configuration Management
- Create and manage multiple pricing configurations
- Set active/inactive status for configurations
- Detailed view of pricing components
- Edit existing configurations
- Change history tracking
- Price calculation logs with detailed breakdowns

### Recent Changes
- Added price logs feature to track all price calculations
- Enhanced UI with detailed price breakdown history
- Improved change tracking for pricing configurations
- Added filtering and sorting capabilities for logs

### Dynamic Pricing Components

1. **Distance Base Price (DBP)**
   - Configure base prices for different days of the week
   - Set base distance and corresponding base price
   - Multiple base price configurations supported

2. **Distance Additional Price (DAP)**
   - Configure price per additional kilometer
   - Applies after base distance is exceeded

3. **Time Multiplier Factor (TMF)**
   - Set time thresholds and corresponding multipliers
   - Progressive multipliers based on delivery duration
   - Up to 3 time threshold levels supported

4. **Waiting Charges (WC)**
   - Configure initial wait time (grace period)
   - Set charge per interval
   - Define interval duration in minutes

### Price Calculator
- Real-time price calculation based on:
  - Distance traveled
  - Total duration
  - Waiting time
  - Day of the week
- Detailed breakdown of charges
- Automatic logging of all calculations
- Historical view of previous calculations

### Price Logs
- Track all price calculations with timestamps
- View detailed breakdown of each calculation
- Filter logs by date range and configuration
- Sort by various parameters (date, price, distance)
- Export functionality for reporting
- Access to historical pricing data

## Technical Stack

- Python 3.x
- Django 4.x
- PostgreSQL
- Bootstrap 5
- HTML/CSS
- JavaScript

## Database Configuration

### PostgreSQL Setup
1. Install PostgreSQL on your system
2. Create a new database:
   ```sql
   CREATE DATABASE delivery_management;
   ```

### Django Database Settings
Update `config/settings.py` with your database configuration:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pricing_module',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd delivery-management-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure database settings in `config/settings.py` as shown in Database Configuration section

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

1. **Creating a Pricing Configuration**
   - Navigate to "Create New Configuration"
   - Fill in the basic information
   - Add distance base prices for different days
   - Configure additional distance pricing
   - Set up time multiplier factors
   - Configure waiting charges
   - Save the configuration

2. **Calculating Delivery Price**
   - Go to "Calculate Price"
   - Enter delivery details:
     - Distance
     - Duration
     - Waiting time
     - Day of the week
   - View detailed price breakdown
   - Access calculation history in price logs

3. **Managing Configurations**
   - View all configurations in the list view
   - Edit existing configurations
   - View change history
   - Activate/deactivate configurations

4. **Accessing Price Logs**
   - Navigate to "Price Logs" section
   - View all historical calculations
   - Filter by date range or configuration
   - Sort by various parameters
   - Export logs for reporting
   - View detailed breakdown of each calculation

## Running Tests

The project includes comprehensive test cases for the pricing calculation functionality. To run the tests:

1. Run all tests:
   ```bash
   python manage.py test pricing.tests
   ```

2. Run specific test cases:
   ```bash
   python manage.py test pricing.tests.PriceCalculationTest
   ```

3. Run with coverage report:
   ```bash
   coverage run --source='.' manage.py test pricing
   coverage report
   ```

### Test Cases Include:
- Basic price calculation
- Additional distance pricing
- Time multiplier factors
- Waiting charges
- Day-specific pricing
- Invalid input handling
- Edge cases

## API Documentation

### Price Calculation API
- Endpoint: `/pricing/calculate/`
- Method: POST
- Parameters:
  - `distance`: float (in kilometers)
  - `duration`: integer (in minutes)
  - `waiting_time`: integer (in minutes)
  - `day_of_week`: string (e.g., "monday", "tuesday", etc.)
- Response: Detailed price breakdown with all components

Example Request:
```json
{
    "distance": 15.5,
    "duration": 45,
    "waiting_time": 10,
    "day_of_week": "monday"
}
```

Example Response:
```json
{
    "base_price": 100.0,
    "additional_distance_charge": 55.0,
    "time_multiplier_charge": 25.0,
    "waiting_charge": 10.0,
    "total_price": 190.0,
    "breakdown": {
        "base_distance": 10,
        "additional_distance": 5.5,
        "time_multiplier": 1.25,
        "waiting_intervals": 2
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Screenshots

Please refer to the `screenshots` folder PATH : D:\LEVEL 1\Level-1-Rutuja-Maurya\SCREENSHOTS in the repository for visual documentation of:
- Home page interface
- Pricing configuration form
- Price calculator interface
- Configuration management views
- Price logs and calculation history
- Example calculations and breakdowns
- Editing or deleting any 

The screenshots provide a comprehensive view of the system's features and user interface elements, including the recently added price logs functionality.