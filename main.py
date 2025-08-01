import os
import stat
from app import app

def check_database_permissions():
    """Проверяет права доступа к базе данных при запуске"""
    db_paths = [
        'instance/parking_booker.db',
        'parking_booker.db',
        'app.db'
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                st = os.stat(db_path)
                permissions = stat.filemode(st.st_mode)
                print(f"📁 База данных: {db_path}")
                print(f"   Права доступа: {permissions}")
                
                # Проверяем права на запись
                if not (st.st_mode & stat.S_IWUSR):
                    print("   ⚠️  Предупреждение: База данных доступна только для чтения")
                    print("   💡 Запустите: python fix_database_permissions.py")
                    return False
                else:
                    print("   ✅ Права доступа в порядке")
                    return True
                    
            except Exception as e:
                print(f"   ❌ Ошибка при проверке прав: {e}")
                return False
    
    print("📝 База данных не найдена, будет создана при первом запуске")
    return True

if __name__ == '__main__':
    print("🚀 Запуск ParkingBooker...")
    
    # Проверяем права доступа к БД
    if not check_database_permissions():
        print("\n⚠️  Рекомендуется исправить права доступа перед запуском")
        print("   Запустите: python fix_database_permissions.py")
    
    print("\n🌐 Приложение доступно по адресу: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
