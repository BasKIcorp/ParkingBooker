#!/usr/bin/env python3
"""
Скрипт для проверки готовности проекта к развертыванию
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Проверяет существование файла"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - НЕ НАЙДЕН")
        return False

def check_imports():
    """Проверяет импорты основных модулей"""
    try:
        import flask
        import flask_sqlalchemy
        import werkzeug
        print("✅ Все основные зависимости импортируются корректно")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def main():
    print("🔍 Проверка готовности проекта к развертыванию...\n")
    
    # Список обязательных файлов
    required_files = [
        ("app.py", "Основной файл приложения"),
        ("models.py", "Модели базы данных"),
        ("routes.py", "Маршруты приложения"),
        ("utils.py", "Утилиты"),
        ("main.py", "Точка входа"),
        ("Dockerfile", "Конфигурация Docker"),
        ("docker-compose.yml", "Конфигурация Docker Compose"),
        ("req.txt", "Зависимости Python"),
        ("pyproject.toml", "Конфигурация Poetry"),
        (".dockerignore", "Исключения для Docker"),
        (".gitignore", "Исключения для Git"),
        ("README.md", "Документация"),
        ("templates/base.html", "Базовый шаблон"),
        ("templates/index.html", "Главная страница"),
        ("templates/admin.html", "Админ панель"),
        ("templates/admin_login.html", "Страница входа в админ"),
        ("templates/success.html", "Страница успеха"),
        ("static/css/style.css", "Стили CSS"),
        ("static/js/main.js", "JavaScript"),
    ]
    
    all_files_exist = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    print("\n" + "="*50)
    
    imports_ok = check_imports()
    
    print("\n" + "="*50)
    
    if all_files_exist and imports_ok:
        print("🎉 Проект готов к развертыванию!")
        print("\nДля запуска используйте:")
        print("  docker-compose up --build")
        print("\nИли без Docker:")
        print("  pip install -r req.txt")
        print("  python main.py")
    else:
        print("⚠️  Проект требует доработки перед развертыванием")
        sys.exit(1)

if __name__ == "__main__":
    main() 