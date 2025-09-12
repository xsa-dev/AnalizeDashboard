#!/usr/bin/env python3
"""
Демонстрационный скрипт для Backtest Dashboard.
Показывает основные возможности приложения без запуска веб-интерфейса.
"""

import pandas as pd
import json
import os
from data_loader import BacktestDataLoader
from visualizations import BacktestVisualizer

def main():
    """Демонстрирует основные возможности приложения."""
    
    print("🚀 Backtest Dashboard - Демонстрация")
    print("=" * 50)
    
    # Инициализация
    data_folder = "input/batch-backtest-09-2025"
    loader = BacktestDataLoader(data_folder)
    visualizer = BacktestVisualizer()
    
    print(f"📁 Загружаем данные из папки: {data_folder}")
    
    # Проверяем наличие данных
    if not os.path.exists(data_folder):
        print(f"❌ Папка {data_folder} не найдена!")
        print("Создайте папку и поместите туда JSON-файлы с результатами бэктестов.")
        return
    
    json_files = [f for f in os.listdir(data_folder) if f.endswith('.json')]
    if not json_files:
        print(f"❌ В папке {data_folder} не найдено JSON-файлов!")
        return
    
    print(f"📊 Найдено {len(json_files)} JSON-файлов")
    
    try:
        # Загружаем данные
        print("⏳ Загружаем и обрабатываем данные...")
        df = loader.load_all_data()
        
        if df.empty:
            print("❌ Не удалось загрузить данные!")
            return
        
        print(f"✅ Загружено {len(df)} сделок")
        
        # Показываем общую статистику
        # Получаем общие метрики
        overall_metrics = loader.get_overall_metrics(df)
        
        print("\n📈 Общая статистика:")
        print(f"   • Всего сделок: {overall_metrics['total_trades']:,}")
        print(f"   • Уникальных стратегий: {df['strategy_name'].nunique()}")
        print(f"   • Уникальных символов: {df['symbol'].nunique()}")
        print(f"   • Общий PNL: {overall_metrics['total_pnl']:.2f} USDT")
        print(f"   • Средний PNL: {overall_metrics['avg_pnl']:.4f} USDT")
        print(f"   • Процент прибыльных: {overall_metrics['win_rate']:.1f}%")
        print(f"   • Профит-фактор: {overall_metrics['profit_factor']:.2f}")
        print(f"   • Математическое ожидание: {overall_metrics['expected_value']:.4f} USDT")
        print(f"   • Коэффициент Шарпа: {overall_metrics['sharpe_ratio']:.4f}")
        
        # Показываем топ-5 стратегий по PNL
        print("\n🏆 Топ-5 стратегий по общему PNL:")
        strategy_metrics = loader.get_strategy_metrics(df)
        top_strategies = strategy_metrics.nlargest(5, 'total_pnl')
        
        for _, row in top_strategies.iterrows():
            print(f"   • {row['strategy_name']}: {row['total_pnl']:.2f} USDT ({row['trades_count']} сделок, PF: {row['profit_factor']:.2f}, EV: {row['expected_value']:.4f})")
        
        # Показываем топ-5 символов по PNL
        print("\n💰 Топ-5 символов по общему PNL:")
        symbol_metrics = loader.get_symbol_metrics(df)
        top_symbols = symbol_metrics.nlargest(5, 'total_pnl')
        
        for _, row in top_symbols.iterrows():
            print(f"   • {row['symbol']}: {row['total_pnl']:.2f} USDT ({row['trades_count']} сделок)")
        
        # Показываем распределение по типам сделок
        print("\n📊 Распределение по типам сделок:")
        type_counts = df['type'].value_counts()
        for trade_type, count in type_counts.items():
            print(f"   • {trade_type}: {count} сделок")
        
        # Показываем временной диапазон
        print(f"\n⏰ Временной диапазон:")
        print(f"   • Первая сделка: {df['opened_at'].min()}")
        print(f"   • Последняя сделка: {df['opened_at'].max()}")
        
        # Показываем среднее время удержания
        avg_holding_hours = df['holding_period'].mean() / 3600
        print(f"   • Среднее время удержания: {avg_holding_hours:.1f} часов")
        
        # Демонстрируем фильтрацию по датам
        print(f"\n📅 Новые возможности фильтрации по датам:")
        min_date, max_date = loader.get_date_range()
        print(f"   • Доступный период: {min_date.strftime('%Y-%m-%d')} - {max_date.strftime('%Y-%m-%d')}")
        
        # Пример фильтрации за последний месяц
        from datetime import datetime, timedelta
        last_month = (max_date - timedelta(days=30)).strftime('%Y-%m-%d')
        recent_df = loader.filter_data(
            start_date=last_month,
            end_date=max_date.strftime('%Y-%m-%d')
        )
        print(f"   • Сделок за последний месяц: {len(recent_df)}")
        if len(recent_df) > 0:
            print(f"   • PNL за последний месяц: {recent_df['PNL'].sum():.2f} USDT")
        
        print("\n✅ Демонстрация завершена!")
        print("\n🌐 Для запуска веб-интерфейса выполните:")
        print("   streamlit run app.py")
        print("\n📖 Или используйте скрипт запуска:")
        print("   python run.py")
        
    except Exception as e:
        print(f"❌ Ошибка при обработке данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
