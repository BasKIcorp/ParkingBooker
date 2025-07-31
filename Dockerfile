# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Установка системных зависимостей
#RUN apt-get update && apt-get install -y \
#    gcc \
#    && rm -rf /var/lib/apt/lists/*


# Установка системных зависимостей
RUN apt-get update --fix-missing && apt-get install -y \
    apt-transport-https \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml req.txt ./

# Установка зависимостей
RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only=main --no-root \
    && pip install -r req.txt



# Копирование кода приложения
COPY . .

# Создание директории для базы данных
RUN mkdir -p instance && chown -R app:app /app

# Переключение на пользователя app
USER app

# Переменные окружения
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

EXPOSE 5000

# Использование gunicorn для продакшена
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"] 
