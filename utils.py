import re
from datetime import date
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

def get_available_spots_for_hour(booking_date, hour):
    """Calculate available parking spots for a specific date and hour"""
    settings = ParkingSettings.query.first()
    if not settings:
        return 0
    # Count all bookings for this date and hour (учитываем диапазон)
    booked_spots = Booking.query.filter(
        Booking.booking_date == booking_date,
        Booking.booking_start_hour <= hour,
        Booking.booking_end_hour >= hour
    ).count()
    available = settings.total_spots - settings.reserve_spots - booked_spots
    return max(0, available)

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


