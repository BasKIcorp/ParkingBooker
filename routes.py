import os
import re
import requests
import qrcode
from datetime import datetime, date, timedelta
from io import BytesIO
import base64
import uuid
import json
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import Booking, ParkingSettings, AdminUser
from utils import get_available_spots_for_hour, validate_russian_phone, generate_sbp_qr_code, create_payment_data

# Configure domain
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
if not YOUR_DOMAIN.startswith('http'):
    YOUR_DOMAIN = f'https://{YOUR_DOMAIN}' if os.environ.get('REPLIT_DEPLOYMENT') else f'http://{YOUR_DOMAIN}'

@app.route('/')
def index():
    """Main page with parking availability and booking form"""
    today = date.today()
    
    # Get next 7 days of availability
    days_schedule = []
    for i in range(7):
        current_date = today + timedelta(days=i)
        hours_availability = []
        
        for hour in range(24):
            available_spots = get_available_spots_for_hour(current_date, hour)
            hours_availability.append({
                'hour': hour,
                'available_spots': available_spots,
                'is_available': available_spots > 0
            })
        
        days_schedule.append({
            'date': current_date,
            'date_str': current_date.strftime('%Y-%m-%d'),
            'date_display': current_date.strftime('%d.%m.%Y'),
            'day_name': current_date.strftime('%A'),
            'hours': hours_availability
        })
    
    settings = ParkingSettings.query.first()
    
    return render_template('index.html', 
                         days_schedule=days_schedule, 
                         settings=settings,
                         today=today.strftime('%Y-%m-%d'))

@app.route('/book', methods=['POST'])
def book_parking():
    """Handle booking form submission (диапазон дат и времени)"""
    try:
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        start_date_str = request.form.get('booking_start_date', '').strip()
        start_time_str = request.form.get('booking_start_time', '').strip()
        end_date_str = request.form.get('booking_end_date', '').strip()
        end_time_str = request.form.get('booking_end_time', '').strip()
        data_consent = request.form.get('data_consent')

        # Validation
        errors = []
        if not first_name:
            errors.append('Имя обязательно для заполнения')
        if not last_name:
            errors.append('Фамилия обязательна для заполнения')
        if not phone:
            errors.append('Телефон обязателен для заполнения')
        elif not validate_russian_phone(phone):
            errors.append('Неверный формат номера телефона')
        if not start_date_str or not start_time_str:
            errors.append('Дата и время начала обязательны')
        if not end_date_str or not end_time_str:
            errors.append('Дата и время конца обязательны')
        if not data_consent:
            errors.append('Необходимо согласие на обработку данных')
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('index'))

        # Parse and validate date/time
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)
        except (ValueError, TypeError):
            flash('Неверный формат даты или времени', 'error')
            return redirect(url_for('index'))

        now = datetime.now()
        if start_dt < now:
            flash('Время начала не может быть в прошлом', 'error')
            return redirect(url_for('index'))
        if end_dt <= start_dt:
            flash('Время конца должно быть позже времени начала', 'error')
            return redirect(url_for('index'))
        if start_date != end_date:
            flash('Бронирование возможно только в пределах одной даты', 'error')
            return redirect(url_for('index'))

        # Check availability for all hours in range
        start_hour = start_time.hour
        end_hour = end_time.hour
        for hour in range(start_hour, end_hour + 1):
            available_spots = get_available_spots_for_hour(start_date, hour)
            if available_spots <= 0:
                flash(f'Нет свободных мест на {hour:02d}:00', 'error')
                return redirect(url_for('index'))

        # Get pricing
        settings = ParkingSettings.query.first()
        if not settings:
            flash('Ошибка конфигурации системы', 'error')
            return redirect(url_for('index'))
        total_amount = settings.hourly_price * (end_hour - start_hour + 1)

        # Create booking record
        booking = Booking(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            booking_date=start_date,
            booking_start_hour=start_hour,
            booking_end_hour=end_hour,
            total_amount=total_amount
        )
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for('success', booking_id=booking.id))
    except Exception as e:
        flash(f'Произошла ошибка: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/success/<int:booking_id>')
def success(booking_id=None):
    """Handle successful booking (no payment)"""
    if booking_id:
        booking = Booking.query.get_or_404(booking_id)
    else:
        flash('Ошибка подтверждения бронирования', 'error')
        return redirect(url_for('index'))
    return render_template('success.html', booking=booking)

@app.route('/cancel')
def payment_cancel():
    """Handle cancelled payment (old URL)"""
    booking_id = request.args.get('booking_id')
    if booking_id:
        # Remove the booking since payment was cancelled
        booking = Booking.query.get(booking_id)
        if booking and booking.payment_status == 'pending':
            db.session.delete(booking)
            db.session.commit()
    
    return render_template('cancel.html')

@app.route('/admin')
def admin_panel():
    """Admin panel for managing parking settings"""
    # Simple auth check
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    settings = ParkingSettings.query.first()
    if not settings:
        # Create default settings
        settings = ParkingSettings()
        db.session.add(settings)
        db.session.commit()
    
    # Get today's bookings for overview
    today = date.today()
    today_bookings = Booking.query.filter_by(
        booking_date=today,
        payment_status='paid'
    ).order_by(Booking.booking_start_hour).all()
    
    # Get recent bookings
    recent_bookings = Booking.query.filter_by(
        payment_status='paid'
    ).order_by(Booking.created_at.desc()).limit(20).all()
    
    return render_template('admin.html', 
                         settings=settings, 
                         today_bookings=today_bookings,
                         recent_bookings=recent_bookings)

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
        hourly_price = float(request.form.get('hourly_price', 0))
        
        if total_spots < 1:
            flash('Общее количество мест должно быть больше 0', 'error')
            return redirect(url_for('admin_panel'))
        
        if reserve_spots < 0:
            flash('Резервные места не могут быть отрицательными', 'error')
            return redirect(url_for('admin_panel'))
        
        if reserve_spots >= total_spots:
            flash('Резервные места должны быть меньше общего количества', 'error')
            return redirect(url_for('admin_panel'))
        
        if hourly_price < 0:
            flash('Цена не может быть отрицательной', 'error')
            return redirect(url_for('admin_panel'))
        
        settings = ParkingSettings.query.first()
        if not settings:
            settings = ParkingSettings()
            db.session.add(settings)
        
        settings.total_spots = total_spots
        settings.reserve_spots = reserve_spots
        settings.hourly_price = hourly_price
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Настройки успешно обновлены', 'success')
        
    except (ValueError, TypeError):
        flash('Неверный формат данных', 'error')
    except Exception as e:
        flash(f'Ошибка при обновлении настроек: {str(e)}', 'error')
    
    return redirect(url_for('admin_panel'))
