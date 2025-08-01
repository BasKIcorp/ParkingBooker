import re
from datetime import date, timedelta
from models import Booking, ParkingSettings

def validate_russian_phone(phone):
    """Validate Russian phone number formats"""
    # Remove all non-digit characters
    phone_digits = re.sub(r'\D', '', phone)
    
    # Russian phone patterns
    patterns = [
        r'^7\d{10}$',     # +7XXXXXXXXXX
        r'^8\d{10}$',     # 8XXXXXXXXXX
        r'^\d{10}$'       # XXXXXXXXXX (assume Russian)
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone_digits):
            return True
    
    return False

def get_available_spots_for_date(booking_date):
    """Calculate available parking spots for a specific date"""
    settings = ParkingSettings.query.first()
    if not settings:
        return 0
    
    # Count all bookings for this date
    booked_spots = Booking.query.filter(
        Booking.start_date <= booking_date,
        Booking.end_date >= booking_date
    ).count()
    
    available = settings.total_spots - settings.reserve_spots - booked_spots
    return max(0, available)

def calculate_daily_price(total_days, vehicle_type='car'):
    """Calculate price based on new tariff system"""
    settings = ParkingSettings.query.first()
    if not settings:
        return 0
    
    if vehicle_type == 'minibus':
        return settings.minibus_price * total_days
    
    # For cars: 1-25 days = 350р, 26+ days = 150р
    if total_days <= 25:
        return settings.daily_price_1_25 * total_days
    else:
        # First 25 days at 350р, remaining days at 150р
        first_25_days = settings.daily_price_1_25 * 25
        remaining_days = settings.daily_price_26_plus * (total_days - 25)
        return first_25_days + remaining_days

def format_phone_display(phone):
    """Format phone number for display"""
    phone_digits = re.sub(r'\D', '', phone)
    
    if len(phone_digits) == 11 and phone_digits.startswith('7'):
        return f"+7 ({phone_digits[1:4]}) {phone_digits[4:7]}-{phone_digits[7:9]}-{phone_digits[9:11]}"
    elif len(phone_digits) == 11 and phone_digits.startswith('8'):
        return f"+7 ({phone_digits[1:4]}) {phone_digits[4:7]}-{phone_digits[7:9]}-{phone_digits[9:11]}"
    elif len(phone_digits) == 10:
        return f"+7 ({phone_digits[0:3]}) {phone_digits[3:6]}-{phone_digits[6:8]}-{phone_digits[8:10]}"
    
    return phone


