# Настройка GitHub Actions для ParkingBooker

## Обзор

Проект настроен с полным CI/CD пайплайном, включающим:
- Автоматическое развертывание
- Тестирование
- Проверки безопасности
- Мониторинг

## Workflows

### 1. Deploy (`deploy.yml`)
- **Триггер**: Push в master/main
- **Функции**:
  - Автоматическое развертывание на сервер
  - Создание SSL сертификатов
  - Проверка здоровья сервисов
  - Очистка неиспользуемых образов
  - Fallback на Alpine Dockerfile при проблемах

### 2. Test (`test.yml`)
- **Триггер**: Push и Pull Request
- **Функции**:
  - Тестирование Python кода
  - Тестирование Docker образов
  - Проверка покрытия кода

### 3. Security (`security.yml`)
- **Триггер**: Push, PR, еженедельно
- **Функции**:
  - Сканирование уязвимостей Trivy
  - Проверка безопасности кода Bandit
  - Проверка зависимостей Safety

### 4. Monitor (`monitor.yml`)
- **Триггер**: Каждые 15 минут, ручной запуск
- **Функции**:
  - Проверка здоровья приложения
  - Мониторинг SSL сертификатов
  - Проверка бэкапов БД

## Исправление проблем деплоя

### Автоматические исправления

GitHub Actions автоматически пытается исправить проблемы:

1. **Конфликты git**: Автоматическое сохранение и сброс изменений
2. **Проблемы сборки**: Fallback на Alpine Dockerfile
3. **Сетевые проблемы**: Retry с обновлением системы
4. **Проблемы с зависимостями**: Альтернативные источники пакетов

### Ручное исправление

Если автоматические исправления не помогли, используйте скрипт:

```bash
# На сервере
cd /home/ParkingBooker
chmod +x fix-deploy.sh
./fix-deploy.sh
```

### Частые проблемы и решения

#### 1. Проблемы с git pull
```bash
# На сервере
cd /home/ParkingBooker
git stash
git fetch origin
git reset --hard origin/master
```

#### 2. Проблемы с Docker сборкой
```bash
# Очистка Docker
docker system prune -f
docker volume prune -f

# Использование Alpine Dockerfile
cp Dockerfile.alpine Dockerfile
docker compose -f docker-compose.prod.yml build --no-cache
```

#### 3. Проблемы с сетью
```bash
# Обновление системы
apt-get update
apt-get upgrade -y

# Проверка DNS
nslookup deb.debian.org
```

#### 4. Предупреждение "version is obsolete"
```bash
# Это предупреждение означает, что в docker-compose.yml используется устаревший атрибут version
# Автоматическое исправление:
./cleanup.sh

# Или ручное исправление:
sed -i '/^version:/d' docker-compose.yml
sed -i '/^version:/d' docker-compose.prod.yml
```

## Настройка Secrets

### Обязательные Secrets

1. **SERVER_IP**
   - IP адрес вашего сервера
   - Пример: `192.168.1.100`

2. **SERVER_SSH_KEY**
   - Приватный SSH ключ для доступа к серверу
   - Содержимое файла `~/.ssh/id_rsa`

### Опциональные Secrets

3. **DOMAIN_NAME**
   - Доменное имя для SSL сертификатов
   - Пример: `parkingbooker.com`

4. **SLACK_WEBHOOK_URL**
   - Webhook URL для уведомлений в Slack
   - Пример: `https://hooks.slack.com/services/...`

## Настройка на GitHub

### 1. Переход в Settings

1. Откройте ваш репозиторий на GitHub
2. Перейдите в `Settings` → `Secrets and variables` → `Actions`

### 2. Добавление Secrets

Нажмите `New repository secret` и добавьте:

```
Name: SERVER_IP
Value: ваш_ip_адрес_сервера
```

```
Name: SERVER_SSH_KEY
Value: -----BEGIN OPENSSH PRIVATE KEY-----
        ваш_приватный_ключ
        -----END OPENSSH PRIVATE KEY-----
```

```
Name: DOMAIN_NAME
Value: ваш_домен.com
```

```
Name: SLACK_WEBHOOK_URL
Value: https://hooks.slack.com/services/...
```

### 3. Настройка сервера

#### Подготовка сервера

```bash
# Создание пользователя для деплоя
sudo adduser deploy
sudo usermod -aG docker deploy

# Настройка SSH ключей
sudo mkdir -p /home/deploy/.ssh
sudo chown deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh

# Копирование публичного ключа
sudo -u deploy ssh-keygen -t rsa -b 4096 -C "deploy@server"
```

#### Настройка проекта

```bash
# Клонирование репозитория
sudo mkdir -p /home/ParkingBooker
sudo chown deploy:deploy /home/ParkingBooker
cd /home/ParkingBooker
git clone https://github.com/your-username/ParkingBooker.git .
```

## Мониторинг

### Просмотр логов

```bash
# GitHub Actions
# Перейдите в Actions tab на GitHub

# Серверные логи
docker compose -f docker-compose.prod.yml logs -f
```

### Уведомления

- **Slack**: Настройте webhook для получения уведомлений
- **Email**: GitHub отправляет уведомления на email
- **Telegram**: Можно настроить через webhook

## Устранение неполадок

### Частые проблемы

1. **SSH подключение не работает**
   ```bash
   # Проверка SSH ключей
   ssh -i ~/.ssh/id_rsa deploy@SERVER_IP
   ```

2. **Docker не установлен на сервере**
   ```bash
   # Установка Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **SSL сертификаты не создаются**
   ```bash
   # Проверка OpenSSL
   openssl version
   
   # Создание сертификатов вручную
   mkdir -p ssl
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/key.pem -out ssl/cert.pem \
     -subj "/C=RU/ST=Moscow/L=Moscow/O=ParkingBooker/CN=localhost"
   ```

4. **Проблемы с сетью при сборке**
   ```bash
   # Проверка DNS
   nslookup deb.debian.org
   
   # Альтернативные репозитории
   echo "deb http://mirror.yandex.ru/debian/ bookworm main" > /etc/apt/sources.list
   apt-get update
   ```

5. **Предупреждение "version is obsolete"**
   ```bash
   # Автоматическое исправление
   ./cleanup.sh
   
   # Или ручное удаление строки version
   sed -i '/^version:/d' docker-compose.yml
   sed -i '/^version:/d' docker-compose.prod.yml
   ```

### Полезные команды

```bash
# Проверка статуса workflows
gh run list

# Просмотр логов конкретного run
gh run view RUN_ID

# Ручной запуск workflow
gh workflow run deploy.yml

# Проверка secrets
gh secret list

# Исправление проблем на сервере
./fix-deploy.sh

# Очистка устаревших файлов
./cleanup.sh
```

## Автоматизация

### Автоматическое обновление SSL

Создайте cron job на сервере:

```bash
# Добавьте в crontab
0 2 * * 1 cd /home/ParkingBooker && ./renew-ssl.sh
```

### Автоматические бэкапы

```bash
# Создайте скрипт бэкапа
cat > /home/ParkingBooker/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp instance/parking.db "backups/parking_$DATE.db"
find backups/ -name "*.db" -mtime +7 -delete
EOF

chmod +x /home/ParkingBooker/backup.sh

# Добавьте в crontab
0 3 * * * /home/ParkingBooker/backup.sh
```

### Мониторинг здоровья

```bash
# Создайте скрипт мониторинга
cat > /home/ParkingBooker/health-check.sh << 'EOF'
#!/bin/bash
if ! curl -f -s --max-time 10 http://localhost > /dev/null; then
    echo "Application is down, restarting..."
    docker compose -f docker-compose.prod.yml restart
fi
EOF

chmod +x /home/ParkingBooker/health-check.sh

# Добавьте в crontab
*/5 * * * * /home/ParkingBooker/health-check.sh
``` 