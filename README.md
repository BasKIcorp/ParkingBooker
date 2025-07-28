# Parking Booker

Система бронирования парковочных мест без оплаты.

## Возможности

- ✅ Бронирование парковочных мест
- ✅ Валидация данных формы
- ✅ Админ панель для управления
- ✅ Настройка параметров парковки
- ✅ Расчет стоимости бронирования

## Технологии

- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **База данных**: SQLite
- **Контейнеризация**: Docker, Docker Compose

## Быстрый старт

### С Docker

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd ParkingBooker
```

2. Запустите с помощью Docker Compose:
```bash
docker-compose up --build
```

3. Откройте браузер и перейдите по адресу: `http://localhost:5000`

### Без Docker

1. Установите Python 3.11+
2. Установите зависимости:
```bash
pip install -r req.txt
```

3. Запустите приложение:
```bash
python main.py
```

## Структура проекта

```
ParkingBooker/
├── app.py              # Конфигурация Flask приложения
├── models.py           # Модели базы данных
├── routes.py           # Маршруты приложения
├── utils.py            # Утилиты
├── main.py             # Точка входа
├── templates/          # HTML шаблоны
├── static/             # Статические файлы (CSS, JS, изображения)
├── migrations/         # Миграции базы данных
├── instance/           # База данных SQLite
├── Dockerfile          # Конфигурация Docker
├── docker-compose.yml  # Конфигурация Docker Compose
└── req.txt            # Зависимости Python
```

## Админ панель

Для доступа к админ панели:
1. Перейдите по адресу: `http://localhost:5000/admin`
2. Используйте учетные данные по умолчанию:
   - Логин: `admin`
   - Пароль: `admin123`

## Переменные окружения

- `FLASK_APP` - Файл приложения (по умолчанию: app.py)
- `FLASK_ENV` - Окружение (development/production)
- `SESSION_SECRET` - Секретный ключ для сессий
- `DATABASE_URL` - URL базы данных (по умолчанию: sqlite:///parking.db)

## Развертывание в продакшене

1. Измените секретный ключ в docker-compose.yml
2. Настройте переменные окружения
3. Используйте внешнюю базу данных (PostgreSQL/MySQL)
4. Настройте reverse proxy (Nginx)
5. Настройте SSL сертификаты

## Лицензия

MIT License 