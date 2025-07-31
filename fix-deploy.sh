#!/bin/bash

# Скрипт для исправления проблем деплоя на сервере

echo "🔧 Исправление проблем деплоя..."

# Остановка всех контейнеров
echo "🛑 Останавливаем все контейнеры..."
docker compose down || true
docker compose -f docker-compose.prod.yml down || true

# Очистка Docker
echo "🧹 Очищаем Docker..."
docker system prune -f
docker volume prune -f
docker network prune -f

# Обновление системы
echo "📦 Обновляем систему..."
apt-get update || true
apt-get upgrade -y || true

# Создание необходимых директорий
echo "📁 Создаем директории..."
mkdir -p ssl static instance backups

# Создание SSL сертификатов
echo "🔐 Создаем SSL сертификаты..."
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem -out ssl/cert.pem \
        -subj "/C=RU/ST=Moscow/L=Moscow/O=ParkingBooker/CN=localhost"
fi

# Попытка сборки с разными Dockerfile
echo "🔨 Пробуем разные варианты сборки..."

# Попытка 1: Основной Dockerfile
echo "Попытка 1: Основной Dockerfile"
if docker compose -f docker-compose.prod.yml build --no-cache; then
    echo "✅ Основной Dockerfile работает"
else
    echo "⚠️  Основной Dockerfile не работает, пробуем Alpine..."
    
    # Попытка 2: Alpine Dockerfile
    cp Dockerfile.alpine Dockerfile
    if docker compose -f docker-compose.prod.yml build --no-cache; then
        echo "✅ Alpine Dockerfile работает"
    else
        echo "❌ Alpine Dockerfile тоже не работает"
        echo "Пробуем минимальную конфигурацию..."
        
        # Попытка 3: Минимальная конфигурация
        docker compose up -d web
        if [ $? -eq 0 ]; then
            echo "✅ Минимальная конфигурация работает"
        else
            echo "❌ Все попытки не удались"
            exit 1
        fi
    fi
fi

# Запуск контейнеров
echo "🚀 Запускаем контейнеры..."
docker compose -f docker-compose.prod.yml up -d

# Проверка здоровья
echo "🏥 Проверяем здоровье..."
sleep 30

# Проверка nginx
if curl -f -s --max-time 10 http://localhost > /dev/null; then
    echo "✅ Nginx работает"
else
    echo "❌ Nginx не работает"
    docker compose -f docker-compose.prod.yml logs nginx
fi

# Проверка Flask
if curl -f -s --max-time 10 http://localhost:5000 > /dev/null; then
    echo "✅ Flask работает"
else
    echo "❌ Flask не работает"
    docker compose -f docker-compose.prod.yml logs web
fi

echo "🔧 Исправление завершено!" 