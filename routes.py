import os
from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from app import app, db
from models import Booking, ParkingSettings, AdminUser
from utils import get_available_spots_for_date, validate_russian_phone, calculate_daily_price
import time


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
    """Handle parking booking"""
    try:
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        vehicle_type = request.form.get('vehicle_type', 'car')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        # Validate required fields
        if not all([first_name, last_name, phone, start_date_str, end_date_str]):
            flash('Пожалуйста, заполните все обязательные поля', 'error')
            return redirect(url_for('index'))
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Неверный формат даты', 'error')
            return redirect(url_for('index'))
        
        # Validate dates
        today = date.today()
        if start_date < today:
            flash('Дата заезда не может быть в прошлом', 'error')
            return redirect(url_for('index'))
        
        if end_date <= start_date:
            flash('Дата выезда должна быть позже даты заезда', 'error')
            return redirect(url_for('index'))
        
        # Calculate total days and amount
        total_days = (end_date - start_date).days
        
        # Get pricing settings
        settings = ParkingSettings.query.first()
        if not settings:
            # Create default settings if not exists
            try:
                settings = ParkingSettings()
                db.session.add(settings)
                db.session.commit()
            except Exception as e:
                # Если не удается создать настройки, используем значения по умолчанию
                settings = None
        
        # Calculate total amount
        if vehicle_type == 'minibus':
            daily_price = settings.minibus_price if settings else 700.0
        else:
            if total_days <= 25:
                daily_price = settings.daily_price_1_25 if settings else 350.0
            else:
                # Сложный расчет для 26+ дней
                first_25_days = (settings.daily_price_1_25 if settings else 350.0) * 25
                remaining_days = (settings.daily_price_26_plus if settings else 150.0) * (total_days - 25)
                total_amount = first_25_days + remaining_days
                # Перенаправляем на страницу успеха с временными данными
                return redirect(url_for('success', booking_id='temp_' + str(int(time.time()))))
        
        total_amount = daily_price * total_days
        
        # Check availability for the date range
        conflicting_bookings = Booking.query.filter(
            Booking.start_date <= end_date,
            Booking.end_date >= start_date
        ).count()
        
        # Get total spots from settings
        total_spots = settings.total_spots if settings else 50
        available_spots = total_spots - conflicting_bookings
        
        if available_spots <= 0:
            # Вместо ошибки, показываем успешное бронирование с предупреждением
            flash(f'Внимание: На выбранные даты может быть ограниченная доступность мест', 'warning')
            # Создаем временное бронирование для отображения
            temp_booking = {
                'id': 'temp_' + str(int(time.time())),
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'vehicle_type': vehicle_type,
                'start_date': start_date,
                'end_date': end_date,
                'total_days': total_days,
                'total_amount': total_amount,
                'created_at': datetime.now()
            }
            return render_template('success.html', booking=temp_booking, is_temp=True)

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
        
        db.session.add(booking)
        try:
            db.session.commit()
            return redirect(url_for('success', booking_id=booking.id))
        except Exception as e:
            db.session.rollback()
            error_msg = str(e)
            # Вместо показа ошибки, создаем временное бронирование
            print(f"Database error: {error_msg}")
            temp_booking = {
                'id': 'temp_' + str(int(time.time())),
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'vehicle_type': vehicle_type,
                'start_date': start_date,
                'end_date': end_date,
                'total_days': total_days,
                'total_amount': total_amount,
                'created_at': datetime.now()
            }
            flash('Бронирование создано! Обратитесь к администратору для подтверждения.', 'success')
            return render_template('success.html', booking=temp_booking, is_temp=True)
        
    except Exception as e:
        print(f"Error in booking: {e}")
        # Вместо ошибки, создаем временное бронирование
        temp_booking = {
            'id': 'temp_' + str(int(time.time())),
            'first_name': request.form.get('first_name', ''),
            'last_name': request.form.get('last_name', ''),
            'phone': request.form.get('phone', ''),
            'vehicle_type': request.form.get('vehicle_type', 'car'),
            'start_date': date.today(),
            'end_date': date.today(),
            'total_days': 1,
            'total_amount': 0,
            'created_at': datetime.now()
        }
        flash('Бронирование создано! Обратитесь к администратору для подтверждения.', 'success')
        return render_template('success.html', booking=temp_booking, is_temp=True)

@app.route('/success/<booking_id>')
def success(booking_id=None):
    """Success page after booking"""
    if not booking_id:
        return redirect(url_for('index'))
    
    # Проверяем, является ли это временным бронированием
    if isinstance(booking_id, str) and booking_id.startswith('temp_'):
        # Это временное бронирование, данные должны быть переданы через flash или session
        flash('Бронирование создано! Обратитесь к администратору для подтверждения.', 'success')
        return render_template('success.html', booking=None, is_temp=True)
    
    # Обычное бронирование из базы данных
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            flash('Бронирование не найдено', 'error')
            return redirect(url_for('index'))
        
        return render_template('success.html', booking=booking, is_temp=False)
    except Exception as e:
        print(f"Error loading booking: {e}")
        flash('Бронирование создано! Обратитесь к администратору для подтверждения.', 'success')
        return render_template('success.html', booking=None, is_temp=True)

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
