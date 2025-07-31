#!/bin/bash

# Скрипт для запуска проекта ParkingBooker с Nginx

echo "🚀 Запуск проекта ParkingBooker с Nginx..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

# Проверка наличия Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Создание директории для SSL сертификатов (если не существует)
mkdir -p ssl

# Создание директории для статических файлов (если не существует)
mkdir -p static

# Выбор режима запуска
echo "Выберите режим запуска:"
echo "1) Разработка (HTTP на порту 80)"
echo "2) Продакшн (HTTPS на порту 80)"
read -p "Введите номер (1 или 2): " choice

case $choice in
    1)
        echo "🔧 Запуск в режиме разработки..."
        docker-compose up --build
        ;;
    2)
        echo "🚀 Запуск в продакшн режиме..."
        
        # Проверка SSL сертификатов
        if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
            echo "⚠️  SSL сертификаты не найдены в папке ssl/"
            echo "Создание самоподписанного сертификата для тестирования..."
            
            # Создание самоподписанного сертификата
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout ssl/key.pem -out ssl/cert.pem \
                -subj "/C=RU/ST=Moscow/L=Moscow/O=ParkingBooker/CN=localhost"
            
            echo "✅ Самоподписанный сертификат создан"
        fi
        
        docker-compose -f docker-compose.prod.yml up --build
        ;;
    *)
        echo "❌ Неверный выбор. Запуск в режиме разработки..."
        docker-compose up --build
        ;;
esac 