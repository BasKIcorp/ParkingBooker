import os
from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.datastructures import ImmutableMultiDict
from app import app, db
from models import Booking, ParkingSettings, AdminUser
from utils import get_available_spots_for_date, validate_russian_phone, calculate_daily_price
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

print("=== ROUTES.PY LOADED ===")
print(f"App routes: {[str(rule) for rule in app.url_map.iter_rules()]}")

@app.route('/')
def index():
    """Main page with parking availability and booking form"""
    today = date.today()
    
    # Get next 30 days of availability
    days_schedule = []
    for i in range(30):
        current_date = today + timedelta(days=i)
        available_spots = get_available_spots_for_date(current_date)
        
        days_schedule.append({
            'date': current_date,
            'date_str': current_date.strftime('%Y-%m-%d'),
            'date_display': current_date.strftime('%d.%m.%Y'),
            'day_name': current_date.strftime('%A'),
            'available_spots': available_spots,
            'is_available': available_spots > 0
        })
    
    settings = ParkingSettings.query.first()
    
    return render_template('index.html', 
                         days_schedule=days_schedule, 
                         settings=settings,
                         today=today.strftime('%Y-%m-%d'))

@app.route('/book_parking', methods=['POST'])
def book_parking():
    """Handle booking form submission (daily booking)"""
    import sys
    print("=== FUNCTION CALLED ===", file=sys.stderr)
    logger.info("=== FUNCTION CALLED ===")
    
    try:
        logger.info("=== BOOKING REQUEST START ===")
        logger.info(f"Form data: {request.form}")
        logger.info("About to enter try block...")
        
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        is_minibus = request.form.get('is_minibus') == '1'
        vehicle_type = 'minibus' if is_minibus else 'car'
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        data_consent = request.form.get('data_consent')

        logger.info(f"Parsed data: first_name='{first_name}', last_name='{last_name}', phone='{phone}', vehicle_type='{vehicle_type}', start_date='{start_date_str}', end_date='{end_date_str}', data_consent='{data_consent}'")

        # Validation
        errors = []
        logger.info("Starting validation...")
        if not first_name:
            errors.append('Имя обязательно для заполнения')
        if not last_name:
            errors.append('Фамилия обязательна для заполнения')
        if not phone:
            errors.append('Телефон обязателен для заполнения')
        elif not validate_russian_phone(phone):
            errors.append('Неверный формат номера телефона')
        if not start_date_str:
            errors.append('Дата начала обязательна')
        if not end_date_str:
            errors.append('Дата окончания обязательна')
        if not data_consent:
            errors.append('Необходимо согласие на обработку данных')
        
        logger.info(f"Validation errors: {errors}")
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('index'))

        # Parse and validate dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            logger.info(f"Parsed dates: start_date={start_date}, end_date={end_date}")
        except (ValueError, TypeError) as e:
            logger.error(f"Date parsing error: {e}")
            flash('Неверный формат даты', 'error')
            return redirect(url_for('index'))

        now = date.today()
        if start_date < now:
            logger.warning(f"Start date {start_date} is in the past")
            flash('Дата начала не может быть в прошлом', 'error')
            return redirect(url_for('index'))
        if end_date <= start_date:
            logger.warning(f"End date {end_date} is not after start date {start_date}")
            flash('Дата окончания должна быть позже даты начала', 'error')
            return redirect(url_for('index'))

        # Calculate total days
        total_days = (end_date - start_date).days + 1
        logger.info(f"Total days: {total_days}")
        
        # Calculate total amount
        total_amount = calculate_daily_price(total_days, vehicle_type)
        logger.info(f"Total amount: {total_amount}")
        
        # Check availability for all dates
        for i in range(total_days):
            check_date = start_date + timedelta(days=i)
            available_spots = get_available_spots_for_date(check_date)
            logger.info(f"Available spots for {check_date}: {available_spots}")
            if available_spots <= 0:
                logger.warning(f"No available spots for {check_date}")
                flash(f'Нет свободных мест на {check_date.strftime("%d.%m.%Y")}', 'error')
                return redirect(url_for('index'))

        logger.info("Creating booking object...")
        # Create booking
        booking = Booking(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            vehicle_type=vehicle_type,
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            total_amount=total_amount
        )
        
        logger.info("Adding booking to session...")
        db.session.add(booking)
        try:
            logger.info("Committing to database...")
            db.session.commit()
            logger.info(f"Booking created successfully with ID: {booking.id}")
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.session.rollback()
            error_msg = str(e)
            if 'readonly database' in error_msg.lower():
                flash('Ошибка: База данных доступна только для чтения. Обратитесь к администратору. Для исправления запустите: python fix_database_permissions.py', 'error')
            elif 'permission denied' in error_msg.lower():
                flash('Ошибка: Отказано в доступе к базе данных. Обратитесь к администратору. Проверьте права доступа к файлу базы данных.', 'error')
            elif 'database is locked' in error_msg.lower():
                flash('Ошибка: База данных заблокирована. Попробуйте перезапустить приложение.', 'error')
            else:
                flash(f'Ошибка при сохранении бронирования: {error_msg}', 'error')
            return redirect(url_for('index'))
        
        logger.info("Redirecting to success page...")
        return redirect(url_for('success', booking_id=booking.id))
        
    except Exception as e:
        logger.error(f"Unexpected error in booking: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f'Произошла ошибка при бронировании: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/success/<int:booking_id>')
def success(booking_id=None):
    """Success page after booking"""
    if not booking_id:
        return redirect(url_for('index'))
    
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Бронирование не найдено', 'error')
        return redirect(url_for('index'))
    
    return render_template('success.html', booking=booking)

@app.route('/admin')
def admin_panel():
    """Admin panel"""
    # Simple auth check
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    settings = ParkingSettings.query.first()
    if not settings:
        # Create default settings
        try:
            settings = ParkingSettings()
            db.session.add(settings)
            db.session.commit()
        except Exception as e:
            error_msg = str(e)
            if 'readonly database' in error_msg.lower():
                flash('Ошибка: База данных доступна только для чтения. Проверьте права доступа. Запустите: python fix_database_permissions.py', 'error')
            elif 'permission denied' in error_msg.lower():
                flash('Ошибка: Отказано в доступе к базе данных. Проверьте права доступа к файлу базы данных.', 'error')
            elif 'database is locked' in error_msg.lower():
                flash('Ошибка: База данных заблокирована. Попробуйте перезапустить приложение.', 'error')
            else:
                flash(f'Ошибка при создании настроек: {error_msg}', 'error')
            return render_template('admin.html', 
                                settings=None, 
                                today_bookings=[],
                                recent_bookings=[],
                                total_bookings=0,
                                total_revenue=0)
    
    # Get today's bookings for overview
    today = date.today()
    today_bookings = Booking.query.filter(
        Booking.start_date <= today,
        Booking.end_date >= today
    ).order_by(Booking.start_date).all()
    
    # Get recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(20).all()
    
    # Calculate statistics
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.total_amount)).scalar() or 0
    
    return render_template('admin.html', 
                         settings=settings, 
                         today_bookings=today_bookings,
                         recent_bookings=recent_bookings,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple hardcoded admin for demo (in production, use proper user management)
        if username == 'admin' and password == os.environ.get('ADMIN_PASSWORD', 'admin123'):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/update_settings', methods=['POST'])
def update_settings():
    """Update parking settings"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        total_spots = int(request.form.get('total_spots', 0))
        reserve_spots = int(request.form.get('reserve_spots', 0))
        daily_price_1_25 = float(request.form.get('daily_price_1_25', 0))
        daily_price_26_plus = float(request.form.get('daily_price_26_plus', 0))
        minibus_price = float(request.form.get('minibus_price', 0))
        
        if total_spots < 1:
            flash('Общее количество мест должно быть больше 0', 'error')
            return redirect(url_for('admin_panel'))
        
        if reserve_spots < 0:
            flash('Резервные места не могут быть отрицательными', 'error')
            return redirect(url_for('admin_panel'))
        
        if reserve_spots >= total_spots:
            flash('Резервные места должны быть меньше общего количества', 'error')
            return redirect(url_for('admin_panel'))
        
        if daily_price_1_25 < 0 or daily_price_26_plus < 0 or minibus_price < 0:
            flash('Цены не могут быть отрицательными', 'error')
            return redirect(url_for('admin_panel'))
        
        settings = ParkingSettings.query.first()
        if not settings:
            settings = ParkingSettings()
            db.session.add(settings)
        
        settings.total_spots = total_spots
        settings.reserve_spots = reserve_spots
        settings.daily_price_1_25 = daily_price_1_25
        settings.daily_price_26_plus = daily_price_26_plus
        settings.minibus_price = minibus_price
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Настройки успешно обновлены', 'success')
        
    except (ValueError, TypeError):
        flash('Неверный формат данных', 'error')
    except Exception as e:
        error_msg = str(e)
        if 'readonly database' in error_msg.lower():
            flash('Ошибка: База данных доступна только для чтения. Проверьте права доступа к файлу базы данных. Запустите: python fix_database_permissions.py', 'error')
        elif 'permission denied' in error_msg.lower():
            flash('Ошибка: Отказано в доступе к базе данных. Проверьте права доступа.', 'error')
        elif 'database is locked' in error_msg.lower():
            flash('Ошибка: База данных заблокирована. Попробуйте перезапустить приложение.', 'error')
        else:
            flash(f'Ошибка при обновлении настроек: {error_msg}', 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/debug/bookings')
def debug_bookings():
    """Debug route to check all bookings in database"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    result = []
    for booking in bookings:
        result.append({
            'id': booking.id,
            'name': f"{booking.first_name} {booking.last_name}",
            'phone': booking.phone,
            'vehicle_type': booking.vehicle_type,
            'start_date': booking.start_date.strftime('%Y-%m-%d'),
            'end_date': booking.end_date.strftime('%Y-%m-%d'),
            'total_days': booking.total_days,
            'amount': booking.total_amount,
            'created': booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return jsonify({
        'total_bookings': len(bookings),
        'bookings': result
    })

@app.route('/agreement.pdf')
def agreement_pdf():
    """Serve agreement PDF file"""
    return send_from_directory('.', 'agreement.pdf')

@app.route('/policy.pdf')
def policy_pdf():
    """Serve policy PDF file"""
    return send_from_directory('.', 'policy.pdf')

@app.route('/debug/database')
def debug_database():
    """Debug route to check database status"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    try:
        # Проверяем настройки
        settings = ParkingSettings.query.first()
        settings_info = {
            'total_spots': settings.total_spots if settings else 'Not found',
            'reserve_spots': settings.reserve_spots if settings else 'Not found',
            'daily_price_1_25': settings.daily_price_1_25 if settings else 'Not found',
            'daily_price_26_plus': settings.daily_price_26_plus if settings else 'Not found',
            'minibus_price': settings.minibus_price if settings else 'Not found'
        }
        
        # Проверяем бронирования
        total_bookings = Booking.query.count()
        today = date.today()
        today_bookings = Booking.query.filter(
            Booking.start_date <= today,
            Booking.end_date >= today
        ).count()
        
        return jsonify({
            'database_status': 'OK',
            'settings': settings_info,
            'total_bookings': total_bookings,
            'today_bookings': today_bookings
        })
    except Exception as e:
        return jsonify({
            'database_status': 'ERROR',
            'error': str(e)
        })
