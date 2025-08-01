from app import db
from datetime import datetime
from sqlalchemy import func

class ParkingSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_spots = db.Column(db.Integer, nullable=False, default=50)
    reserve_spots = db.Column(db.Integer, nullable=False, default=5)
    # Новая тарификация
    daily_price_1_25 = db.Column(db.Float, nullable=False, default=350.0)  # 1-25 сутки
    daily_price_26_plus = db.Column(db.Float, nullable=False, default=150.0)  # 26+ сутки
    minibus_price = db.Column(db.Float, nullable=False, default=700.0)  # Микроавтобус
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False, default='car')  # car или minibus
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.first_name} {self.last_name} - {self.start_date} to {self.end_date} ({self.total_days} days)>'

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
