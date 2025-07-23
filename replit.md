# Parking Reservation System

## Overview

This is a Flask-based parking reservation system that allows users to book parking spots by hour with integrated Stripe payment processing. The system features a public booking interface and an admin panel for managing settings and viewing bookings.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a traditional Flask MVC pattern with the following components:

- **Frontend**: Server-rendered HTML templates using Jinja2 with Bootstrap for responsive UI
- **Backend**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development (configurable via DATABASE_URL environment variable)
- **Payment Processing**: Stripe integration for secure payment handling
- **Session Management**: Flask sessions for admin authentication

## Key Components

### Models (`models.py`)
- **ParkingSettings**: Stores system configuration (total spots, reserved spots, hourly pricing)
- **Booking**: Stores reservation data with payment status tracking
- **AdminUser**: Stores admin credentials for system management

### Routes (`routes.py`)
- **Public Routes**: Main booking interface and payment flow
- **Admin Routes**: Administrative panel for settings and booking management
- **Payment Routes**: Stripe integration for payment processing

### Utilities (`utils.py`)
- **Phone Validation**: Russian phone number format validation
- **Availability Calculation**: Real-time parking spot availability tracking
- **Phone Formatting**: Display formatting for phone numbers

### Frontend Components
- **Responsive Design**: Bootstrap-based UI with dark theme support
- **Interactive Schedule**: Grid-based hourly availability display
- **Form Validation**: Client-side and server-side validation
- **Payment Integration**: Stripe Checkout integration

## Data Flow

1. **Booking Flow**:
   - User views 7-day availability schedule
   - Selects date/time slot and fills booking form
   - System validates availability and creates pending booking
   - User redirected to payment page with QR-code for СБП
   - Real-time payment status tracking updates booking automatically

2. **Admin Flow**:
   - Admin login with username/password
   - Access to system settings and booking management
   - Real-time availability calculations based on settings

## External Dependencies

### Payment Processing
- **СБП (Система быстрых платежей)**: Российская платежная система с QR-кодами
- **QR Code Generation**: Автоматическая генерация QR-кодов для оплаты
- **Real-time Status Tracking**: Отслеживание статуса платежа в реальном времени

### Database
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Default database (configurable via DATABASE_URL)

### Frontend Libraries
- **Bootstrap**: Responsive UI framework
- **Font Awesome**: Icon library
- **Custom CSS/JS**: Application-specific styling and behavior

## Deployment Strategy

The application is configured for Replit deployment with:

- **Environment Variables**: 
  - `DATABASE_URL`: Database connection string  
  - `SESSION_SECRET`: Flask session encryption key
  - `REPLIT_DEV_DOMAIN`: Domain configuration for payment callbacks
  - `ADMIN_PASSWORD`: Admin panel access password (default: admin123)

- **Production Considerations**:
  - ProxyFix middleware for proper header handling
  - Database connection pooling
  - Automatic table creation on startup
  - Default settings initialization

- **Security Features**:
  - Password hashing for admin accounts
  - Session-based authentication
  - Input validation and sanitization
  - CSRF protection through form handling

The system is designed to be easily deployable on Replit with minimal configuration, while maintaining flexibility for other deployment environments through environment variable configuration.