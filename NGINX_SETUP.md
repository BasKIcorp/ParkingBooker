# Настройка Nginx для проекта ParkingBooker

## Обзор

Nginx настроен как обратный прокси-сервер перед Flask приложением. Это обеспечивает:
- Лучшую производительность
- Статическое обслуживание файлов
- Сжатие контента
- Дополнительную безопасность
- SSL поддержку на порту 80

## Архитектура

```
Internet → Nginx (порт 80 с SSL) → Flask App (порт 5000)
```

## Быстрый запуск

### Автоматический запуск

```bash
# Запуск скрипта (выберите режим)
./start.sh
```

### Ручной запуск

#### Режим разработки (HTTP на порту 80)

```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d --build
```

#### Продакшн режим (HTTPS на порту 80)

```bash
# Создание SSL сертификатов (если нужно)
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=ParkingBooker/CN=localhost"

# Запуск продакшн версии
docker-compose -f docker-compose.prod.yml up --build
```

## Конфигурация Nginx

### Основные настройки (`nginx.conf`)

- **Порт**: 80 (HTTP)
- **Статические файлы**: `/static/` → `/app/static/`
- **Проксирование**: все остальные запросы → Flask app
- **Сжатие**: Gzip для текстовых файлов
- **Безопасность**: Заголовки безопасности

### Продакшн настройки (`nginx-ssl.conf`)

- **Порт**: 80 (HTTPS с SSL)
- **SSL/TLS поддержка**
- **HSTS заголовки**
- **DDoS защита**
- **Улучшенная безопасность**

### Ключевые особенности

1. **Статические файлы**
   - Обслуживаются напрямую nginx
   - Кэширование на 1 год
   - Сжатие включено

2. **Проксирование**
   - Все запросы к Flask приложению
   - Правильные заголовки для прокси
   - Таймауты настроены

3. **Безопасность**
   - Заголовки безопасности
   - Скрытие версии nginx
   - Ограничения на размер запросов
   - Защита от DDoS атак
   - SSL шифрование

## Переменные окружения

Создайте файл `.env` на основе `env.example`:

```bash
cp env.example .env
# Отредактируйте .env файл
```

### Важные переменные

- `SESSION_SECRET` - секретный ключ для сессий
- `DATABASE_URL` - URL базы данных
- `DOMAIN_NAME` - доменное имя для nginx

## Мониторинг

### Логи

```bash
# Логи nginx
docker-compose exec nginx tail -f /var/log/nginx/access.log
docker-compose exec nginx tail -f /var/log/nginx/error.log

# Логи Flask приложения
docker-compose logs -f web
```

### Проверка здоровья

```bash
# Проверка nginx
curl -I http://localhost

# Проверка Flask app напрямую
curl -I http://localhost:5000

# Проверка HTTPS (в продакшн)
curl -I https://localhost
```

## Производительность

### Настройки оптимизации

- **Worker connections**: 1024
- **Keepalive**: 65 секунд
- **Gzip сжатие**: уровень 6
- **Буферизация**: включена

### Мониторинг производительности

```bash
# Статистика nginx (если включен модуль stub_status)
curl http://localhost/nginx_status

# Проверка использования памяти
docker stats

# Проверка сетевых соединений
docker-compose exec nginx netstat -tulpn
```

## Безопасность

### Заголовки безопасности

- `X-Frame-Options`: SAMEORIGIN
- `X-XSS-Protection`: 1; mode=block
- `X-Content-Type-Options`: nosniff
- `Referrer-Policy`: no-referrer-when-downgrade
- `Content-Security-Policy`: настроен
- `Strict-Transport-Security`: (в HTTPS режиме)

### Ограничения

- Максимальный размер запроса: 10MB
- Таймаут клиента: 12 секунд
- Rate limiting для API: 10 запросов/сек

## Развертывание

### Продакшн настройки

1. Измените `server_name` в `nginx-ssl.conf`
2. Настройте SSL сертификаты
3. Обновите переменные окружения
4. Настройте мониторинг

### SSL/HTTPS

Для добавления SSL:

1. Добавьте сертификаты в папку `ssl/`
2. Обновите `DOMAIN_NAME` в переменных окружения
3. Используйте `docker-compose.prod.yml`

### Получение SSL сертификатов

#### Let's Encrypt (бесплатно)

```bash
# Установка certbot
sudo apt install certbot

# Получение сертификата
sudo certbot certonly --standalone -d your-domain.com

# Копирование сертификатов
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
```

## Устранение неполадок

### Частые проблемы

1. **Nginx не может подключиться к Flask**
   - Проверьте, что Flask app запущен
   - Проверьте сеть Docker

2. **Статические файлы не загружаются**
   - Проверьте монтирование volume
   - Проверьте права доступа

3. **Ошибки 502 Bad Gateway**
   - Проверьте логи Flask app
   - Проверьте healthcheck

4. **SSL ошибки**
   - Проверьте наличие сертификатов
   - Проверьте права доступа к сертификатам

### Команды диагностики

```bash
# Проверка конфигурации nginx
docker-compose exec nginx nginx -t

# Проверка сетевых соединений
docker-compose exec nginx netstat -tulpn

# Проверка процессов
docker-compose exec nginx ps aux

# Проверка SSL сертификатов
openssl x509 -in ssl/cert.pem -text -noout
```

### Полезные команды

```bash
# Перезапуск только nginx
docker-compose restart nginx

# Перезапуск только Flask app
docker-compose restart web

# Просмотр всех логов
docker-compose logs

# Очистка и пересборка
docker-compose down
docker-compose up --build
``` 