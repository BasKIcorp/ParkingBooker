# syntax=docker/dockerfile:1
FROM python:3.11-alpine

# Установка системных зависимостей
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    curl

# Создание пользователя для безопасности
RUN adduser -D -s /bin/sh app

WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml req.txt ./

# Установка зависимостей
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only=main --no-root && \
    pip install -r req.txt

# Копирование кода приложения
COPY . .

# Создание директории для базы данных и установка прав
RUN mkdir -p instance && \
    chown -R app:app /app && \
    chmod 755 instance

# Создание скрипта инициализации БД
RUN echo '#!/bin/sh\n\
echo "🔧 Инициализация базы данных..."\n\
python fix_database_permissions.py\n\
echo "✅ База данных готова"\n\
exec "$@"' > /app/init-db.sh && \
    chmod +x /app/init-db.sh

# Переключение на пользователя app
USER app

# Переменные окружения
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

EXPOSE 5000

# Использование скрипта инициализации и gunicorn
CMD ["/app/init-db.sh", "gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"] 