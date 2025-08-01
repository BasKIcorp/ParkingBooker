import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "parking-reservation-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///parking.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to create tables
    import models  # noqa: F401
    db.create_all()
    
    # Initialize default settings if not exists
    from models import ParkingSettings
    if not ParkingSettings.query.first():
        default_settings = ParkingSettings(
            total_spots=50,
            reserve_spots=5,
            daily_price_1_25=350.0,  # 1-25 сутки
            daily_price_26_plus=150.0,  # 26+ сутки
            minibus_price=700.0  # Микроавтобус
        )
        db.session.add(default_settings)
        db.session.commit()

# Import routes
try:
    import routes  # noqa: F401
    print("=== ROUTES IMPORTED SUCCESSFULLY ===")
except Exception as e:
    print(f"=== ERROR IMPORTING ROUTES: {e} ===")
    import traceback
    traceback.print_exc()
