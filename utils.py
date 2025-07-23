import re
import qrcode
import uuid
from datetime import date
from io import BytesIO
import base64
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

def generate_sbp_qr_code(amount, order_id, description="Оплата парковки"):
    """
    Генерирует QR-код для оплаты через СБП
    Возвращает base64 изображение QR-кода
    """
    # Формируем ссылку СБП (упрощенная версия)
    # В реальном проекте здесь должна быть интеграция с банковским API
    sbp_data = f"https://qr.nspk.ru/proxyapp?type=02&bank=100000000004&sum={amount}&cur=RUB&crc=71A3"
    
    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    
    qr.add_data(sbp_data)
    qr.make(fit=True)
    
    # Создаем изображение
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Конвертируем в base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def create_payment_data(booking, amount):
    """
    Создает данные для оплаты СБП
    """
    time_range = f"{booking.booking_start_hour:02d}:00 - {booking.booking_end_hour+1:02d}:00"
    payment_data = {
        'booking_id': booking.id,
        'amount': amount,
        'description': f'Парковка {booking.booking_date.strftime("%d.%m.%Y")} {time_range}',
        'order_id': booking.stripe_session_id,  # Используем существующее поле как payment_id
        'customer_name': f'{booking.first_name} {booking.last_name}',
        'customer_phone': booking.phone
    }
    return payment_data
