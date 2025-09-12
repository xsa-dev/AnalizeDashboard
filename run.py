#!/usr/bin/env python3
"""
Скрипт для запуска Backtest Dashboard.
"""

import subprocess
import sys
import os

def main():
    """Запускает Streamlit-приложение."""
    
    # Проверяем наличие файла app.py
    if not os.path.exists('app.py'):
        print("❌ Ошибка: Файл app.py не найден!")
        print("Убедитесь, что вы находитесь в правильной директории.")
        sys.exit(1)
    
    # Проверяем наличие папки с данными
    if not os.path.exists('input/batch-backtest-09-2025'):
        print("⚠️  Предупреждение: Папка input/batch-backtest-09-2025 не найдена!")
        print("Создайте папку и поместите туда JSON-файлы с результатами бэктестов.")
    
    print("🚀 Запуск Backtest Dashboard...")
    print("📊 Приложение будет доступно по адресу: http://0.0.0.0:8501")
    print("🌐 Доступ извне: http://[YOUR_IP]:8501")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("-" * 50)
    
    try:
        # Запускаем Streamlit
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0'
        ])
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено пользователем.")
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
