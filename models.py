from app import db
from datetime import datetime
from sqlalchemy import func

class ParkingSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_spots = db.Column(db.Integer, nullable=False, default=50)
    reserve_spots = db.Column(db.Integer, nullable=False, default=5)
    hourly_price = db.Column(db.Float, nullable=False, default=100.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_start_hour = db.Column(db.Integer, nullable=False)  # начало диапазона
    booking_end_hour = db.Column(db.Integer, nullable=False)    # конец диапазона
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.first_name} {self.last_name} - {self.booking_date} {self.booking_start_hour}:00-{self.booking_end_hour+1}:00>'

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
