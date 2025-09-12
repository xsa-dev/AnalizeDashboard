"""
Streamlit-приложение для визуализации результатов бэктестов.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import json
from datetime import datetime

from data_loader import BacktestDataLoader
from visualizations import BacktestVisualizer

# Настройка страницы
st.set_page_config(
    page_title="Backtest Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Заголовок приложения
st.title("📊 Backtest Dashboard")
st.markdown("---")

# Функции для работы с настройками
def export_settings(selected_symbols, selected_strategies, start_date, end_date, chart_type, show_columns, max_rows):
    """Экспортирует текущие настройки в JSON формат."""
    settings = {
        "selected_symbols": selected_symbols,
        "selected_strategies": selected_strategies,
        "start_date": start_date.strftime('%Y-%m-%d') if start_date else None,
        "end_date": end_date.strftime('%Y-%m-%d') if end_date else None,
        "chart_type": chart_type,
        "show_columns": show_columns,
        "max_rows": max_rows,
        "export_timestamp": datetime.now().isoformat()
    }
    return json.dumps(settings, ensure_ascii=False, indent=2)

def import_settings(uploaded_file):
    """Импортирует настройки из JSON файла."""
    try:
        settings = json.load(uploaded_file)
        return settings
    except Exception as e:
        st.error(f"Ошибка при загрузке настроек: {str(e)}")
        return None

def apply_settings(settings, symbols, strategies, min_date, max_date):
    """Применяет загруженные настройки к интерфейсу."""
    if not settings:
        return None, None, None, None, None, None, None
    
    # Валидация и применение настроек
    selected_symbols = settings.get('selected_symbols', symbols[:5] if len(symbols) > 5 else symbols)
    selected_strategies = settings.get('selected_strategies', strategies[:3] if len(strategies) > 3 else strategies)
    
    # Проверяем, что выбранные символы и стратегии существуют
    selected_symbols = [s for s in selected_symbols if s in symbols]
    selected_strategies = [s for s in selected_strategies if s in strategies]
    
    # Если ничего не выбрано, используем значения по умолчанию
    if not selected_symbols:
        selected_symbols = symbols[:5] if len(symbols) > 5 else symbols
    if not selected_strategies:
        selected_strategies = strategies[:3] if len(strategies) > 3 else strategies
    
    # Обработка дат
    start_date_str = settings.get('start_date')
    end_date_str = settings.get('end_date')
    
    start_date = None
    end_date = None
    
    if start_date_str and min_date:
        try:
            start_date = pd.to_datetime(start_date_str).date()
            if start_date < min_date.date():
                start_date = min_date.date()
            if start_date > max_date.date():
                start_date = max_date.date()
        except:
            start_date = min_date.date()
    
    if end_date_str and max_date:
        try:
            end_date = pd.to_datetime(end_date_str).date()
            if end_date < min_date.date():
                end_date = min_date.date()
            if end_date > max_date.date():
                end_date = max_date.date()
        except:
            end_date = max_date.date()
    
    chart_type = settings.get('chart_type', 'PNL по сделкам')
    show_columns = settings.get('show_columns', ['symbol', 'strategy_name', 'type', 'entry_price', 'exit_price', 'PNL', 'PNL_percentage', 'holding_period', 'opened_at'])
    max_rows = settings.get('max_rows', 100)
    
    return selected_symbols, selected_strategies, start_date, end_date, chart_type, show_columns, max_rows

# Инициализация компонентов
@st.cache_resource
def initialize_components():
    """Инициализирует компоненты приложения."""
    data_folder = "input/batch-backtest-09-2025"
    loader = BacktestDataLoader(data_folder)
    visualizer = BacktestVisualizer()
    return loader, visualizer

# Загружаем данные
loader, visualizer = initialize_components()

# Функция для загрузки настроек по умолчанию
def load_default_settings():
    """Загружает настройки по умолчанию из example_settings.json если они еще не загружены."""
    if not any(key in st.session_state for key in ['imported_symbols', 'imported_strategies', 'imported_start_date', 'imported_end_date']):
        try:
            with open('example_settings.json', 'r', encoding='utf-8') as f:
                default_settings = json.load(f)
            
            # Применяем настройки по умолчанию
            symbols = loader.get_unique_symbols()
            strategies = loader.get_unique_strategies()
            min_date, max_date = loader.get_date_range()
            
            new_symbols, new_strategies, new_start_date, new_end_date, new_chart_type, new_show_columns, new_max_rows = apply_settings(
                default_settings, symbols, strategies, min_date, max_date
            )
            
            if new_symbols is not None:
                st.session_state.imported_symbols = new_symbols
                st.session_state.imported_strategies = new_strategies
                st.session_state.imported_start_date = new_start_date
                st.session_state.imported_end_date = new_end_date
                st.session_state.imported_chart_type = new_chart_type
                st.session_state.imported_show_columns = new_show_columns
                st.session_state.imported_max_rows = new_max_rows
                
                # Показываем уведомление о загрузке настроек по умолчанию
                st.info("🎯 Загружены настройки по умолчанию из example_settings.json")
        except FileNotFoundError:
            # Файл не найден, это нормально
            pass
        except Exception as e:
            # Ошибка при загрузке, игнорируем
            pass

# Загружаем настройки по умолчанию
load_default_settings()

# Проверяем наличие данных
try:
    df = loader.load_all_data()
    if df.empty:
        st.error("❌ Не найдено данных для анализа!")
        st.stop()
except Exception as e:
    st.error(f"❌ Ошибка при загрузке данных: {str(e)}")
    st.stop()

# Боковая панель с фильтрами
st.sidebar.header("🔍 Фильтры")

# Получаем уникальные значения
symbols = loader.get_unique_symbols()
strategies = loader.get_unique_strategies()
min_date, max_date = loader.get_date_range()

# Фильтр по символам
# Проверяем, есть ли импортированные настройки
default_symbols = st.session_state.get('imported_symbols', symbols[:5] if len(symbols) > 5 else symbols)
selected_symbols = st.sidebar.multiselect(
    "Выберите монеты:",
    options=symbols,
    default=default_symbols,
    help="Выберите одну или несколько монет для анализа"
)

# Фильтр по стратегиям
# Проверяем, есть ли импортированные настройки
default_strategies = st.session_state.get('imported_strategies', strategies[:3] if len(strategies) > 3 else strategies)
selected_strategies = st.sidebar.multiselect(
    "Выберите стратегии:",
    options=strategies,
    default=default_strategies,
    help="Выберите одну или несколько стратегий для анализа"
)

# Фильтр по датам
st.sidebar.markdown("---")
st.sidebar.subheader("📅 Временной период")

if min_date and max_date:
    # Показываем доступный диапазон дат
    st.sidebar.info(f"Доступный период:\n{min_date.strftime('%Y-%m-%d')} - {max_date.strftime('%Y-%m-%d')}")
    
    # Проверяем, есть ли импортированные настройки для дат
    imported_start_date = st.session_state.get('imported_start_date')
    imported_end_date = st.session_state.get('imported_end_date')
    
    default_start_date = imported_start_date if imported_start_date else min_date.date()
    default_end_date = imported_end_date if imported_end_date else max_date.date()
    
    # Фильтр по начальной дате
    start_date = st.sidebar.date_input(
        "Период с:",
        value=default_start_date,
        min_value=min_date.date(),
        max_value=max_date.date(),
        help="Выберите начальную дату для анализа"
    )
    
    # Фильтр по конечной дате
    end_date = st.sidebar.date_input(
        "Период по:",
        value=default_end_date,
        min_value=min_date.date(),
        max_value=max_date.date(),
        help="Выберите конечную дату для анализа"
    )
    
    # Проверяем корректность диапазона
    if start_date > end_date:
        st.sidebar.error("❌ Начальная дата не может быть больше конечной!")
        start_date = min_date.date()
        end_date = max_date.date()
    
    # Быстрые кнопки для выбора периодов
    st.sidebar.markdown("**Быстрый выбор:**")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("📅 За последний месяц", help="Последние 30 дней"):
            end_date = max_date.date()
            start_date = (pd.Timestamp(end_date) - pd.Timedelta(days=30)).date()
            st.rerun()
    
    with col2:
        if st.button("📅 За последние 3 месяца", help="Последние 90 дней"):
            end_date = max_date.date()
            start_date = (pd.Timestamp(end_date) - pd.Timedelta(days=90)).date()
            st.rerun()
    
    col3, col4 = st.sidebar.columns(2)
    
    with col3:
        if st.button("📅 За последние 6 месяцев", help="Последние 180 дней"):
            end_date = max_date.date()
            start_date = (pd.Timestamp(end_date) - pd.Timedelta(days=180)).date()
            st.rerun()
    
    with col4:
        if st.button("📅 За весь период", help="Все доступные данные"):
            start_date = min_date.date()
            end_date = max_date.date()
            st.rerun()
    
    # Кнопка для сброса фильтров по датам
    if st.sidebar.button("🔄 Сбросить даты"):
        start_date = min_date.date()
        end_date = max_date.date()
        st.rerun()
    
    # Кнопка для сброса всех импортированных настроек
    if st.sidebar.button("🗑️ Сбросить импортированные настройки"):
        # Очищаем session state
        for key in ['imported_symbols', 'imported_strategies', 'imported_start_date', 'imported_end_date', 'imported_chart_type', 'imported_show_columns', 'imported_max_rows']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Импортированные настройки сброшены!")
        st.rerun()
else:
    start_date = None
    end_date = None

# Применяем фильтры
filtered_df = loader.filter_data(
    selected_symbols, 
    selected_strategies, 
    start_date.strftime('%Y-%m-%d') if start_date else None,
    end_date.strftime('%Y-%m-%d') if end_date else None
)

if filtered_df.empty:
    st.warning("⚠️ Нет данных, соответствующих выбранным фильтрам!")
    st.stop()

# Основной контент
# Показываем выбранный период
if start_date and end_date:
    st.info(f"📅 Анализируемый период: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")

# Получаем общие метрики
overall_metrics = loader.get_overall_metrics(filtered_df)

# Отображаем ключевые метрики
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric("Всего сделок", f"{overall_metrics['total_trades']:,}")
with col2:
    st.metric("Общий PNL", f"{overall_metrics['total_pnl']:.2f} USDT", delta=f"{overall_metrics['total_pnl']:.2f}")
with col3:
    st.metric("Процент прибыльных", f"{overall_metrics['win_rate']:.1f}%")
with col4:
    st.metric("Профит-фактор", f"{overall_metrics['profit_factor']:.2f}")
with col5:
    st.metric("Мат. ожидание", f"{overall_metrics['expected_value']:.4f} USDT")
with col6:
    st.metric("Коэф. Шарпа", f"{overall_metrics['sharpe_ratio']:.4f}")

# Дополнительные метрики в отдельной строке
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Средний PNL", f"{overall_metrics['avg_pnl']:.4f} USDT")
with col2:
    st.metric("Медианный PNL", f"{overall_metrics['median_pnl']:.4f} USDT")
with col3:
    st.metric("Макс. прибыль", f"{overall_metrics['max_profit']:.2f} USDT")
with col4:
    st.metric("Макс. убыток", f"{overall_metrics['max_loss']:.2f} USDT")

st.markdown("---")

# Вкладки для разных типов анализа
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Графики PNL", "📊 Анализ стратегий", "💰 Метрики", "📋 Таблицы", "⚙️ Настройки"])

with tab1:
    st.header("Графики PNL")
    
    # Выбор типа графика
    # Проверяем, есть ли импортированные настройки
    default_chart_type = st.session_state.get('imported_chart_type', "PNL по сделкам")
    chart_type = st.selectbox(
        "Выберите тип графика:",
        ["PNL по сделкам", "Накопленный PNL", "PNL по времени", "Распределение PNL"],
        index=["PNL по сделкам", "Накопленный PNL", "PNL по времени", "Распределение PNL"].index(default_chart_type) if default_chart_type in ["PNL по сделкам", "Накопленный PNL", "PNL по времени", "Распределение PNL"] else 0
    )
    
    if chart_type == "PNL по сделкам":
        fig = visualizer.plot_pnl_by_trades(filtered_df, f"PNL по сделкам - {', '.join(selected_symbols)}")
        st.plotly_chart(fig, width='stretch')
    
    elif chart_type == "Накопленный PNL":
        fig = visualizer.plot_cumulative_pnl(filtered_df, f"Накопленный PNL - {', '.join(selected_symbols)}")
        st.plotly_chart(fig, width='stretch')
    
    elif chart_type == "PNL по времени":
        fig = visualizer.plot_pnl_timeline(filtered_df, f"PNL по времени - {', '.join(selected_symbols)}")
        st.plotly_chart(fig, width='stretch')
    
    elif chart_type == "Распределение PNL":
        fig = visualizer.plot_pnl_distribution(filtered_df, f"Распределение PNL по стратегиям")
        st.plotly_chart(fig, width='stretch')

with tab2:
    st.header("Анализ стратегий")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Сравнительный анализ стратегий
        fig = visualizer.plot_strategy_comparison(filtered_df)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Процент прибыльных сделок
        fig = visualizer.plot_win_rate_by_strategy(filtered_df)
        st.plotly_chart(fig, width='stretch')
    
    # Распределение времени удержания
    st.subheader("Распределение времени удержания")
    fig = visualizer.plot_holding_period_distribution(filtered_df)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Метрики")
    
    # Метрики по стратегиям
    st.subheader("Метрики по стратегиям")
    strategy_metrics = loader.get_strategy_metrics(filtered_df)
    
    if not strategy_metrics.empty:
        # Отображаем ключевые метрики
        display_metrics = strategy_metrics[['strategy_name', 'total_pnl', 'avg_pnl', 'win_rate', 'trades_count', 'profit_factor', 'expected_value']].copy()
        display_metrics.columns = ['Стратегия', 'Общий PNL', 'Средний PNL', 'Процент прибыльных', 'Количество сделок', 'Профит-фактор', 'Мат. ожидание']
        
        st.dataframe(
            display_metrics,
            width='stretch',
            hide_index=True
        )
        
        # График метрик
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Общий PNL по стратегиям', 'Профит-фактор по стратегиям', 
                          'Математическое ожидание по стратегиям', 'Процент прибыльных сделок'),
            vertical_spacing=0.15
        )
        
        # Общий PNL
        fig.add_trace(go.Bar(
            x=strategy_metrics['strategy_name'],
            y=strategy_metrics['total_pnl'],
            name='Общий PNL',
            marker_color='lightblue'
        ), row=1, col=1)
        
        # Профит-фактор
        fig.add_trace(go.Bar(
            x=strategy_metrics['strategy_name'],
            y=strategy_metrics['profit_factor'],
            name='Профит-фактор',
            marker_color='lightgreen'
        ), row=1, col=2)
        
        # Математическое ожидание
        fig.add_trace(go.Bar(
            x=strategy_metrics['strategy_name'],
            y=strategy_metrics['expected_value'],
            name='Мат. ожидание',
            marker_color='lightcoral'
        ), row=2, col=1)
        
        # Процент прибыльных
        fig.add_trace(go.Bar(
            x=strategy_metrics['strategy_name'],
            y=strategy_metrics['win_rate'],
            name='Процент прибыльных',
            marker_color='lightyellow'
        ), row=2, col=2)
        
        fig.update_layout(
            title="Сравнительный анализ стратегий",
            height=600,
            showlegend=False
        )
        
        st.plotly_chart(fig, width='stretch')
    
    # Метрики по символам
    st.subheader("Метрики по символам")
    symbol_metrics = loader.get_symbol_metrics(filtered_df)
    
    if not symbol_metrics.empty:
        display_symbol_metrics = symbol_metrics[['symbol', 'total_pnl', 'avg_pnl', 'win_rate', 'trades_count', 'profit_factor', 'expected_value']].copy()
        display_symbol_metrics.columns = ['Символ', 'Общий PNL', 'Средний PNL', 'Процент прибыльных', 'Количество сделок', 'Профит-фактор', 'Мат. ожидание']
        
        st.dataframe(
            display_symbol_metrics,
            width='stretch',
            hide_index=True
        )

with tab4:
    st.header("Таблицы данных")
    
    # Настройки отображения таблицы
    col1, col2 = st.columns(2)
    
    with col1:
        # Проверяем, есть ли импортированные настройки для колонок
        default_show_columns = st.session_state.get('imported_show_columns', ['symbol', 'strategy_name', 'type', 'entry_price', 'exit_price', 'PNL', 'PNL_percentage', 'holding_period', 'opened_at'])
        show_columns = st.multiselect(
            "Выберите колонки для отображения:",
            options=filtered_df.columns.tolist(),
            default=default_show_columns
        )
    
    with col2:
        # Проверяем, есть ли импортированные настройки для количества строк
        default_max_rows = st.session_state.get('imported_max_rows', 100)
        max_rows = st.slider("Максимальное количество строк:", 10, 1000, default_max_rows)
    
    # Отображаем таблицу
    if show_columns:
        display_df = filtered_df[show_columns].head(max_rows)
        
        # Форматируем числовые колонки
        numeric_columns = ['entry_price', 'exit_price', 'PNL', 'PNL_percentage', 'holding_period']
        for col in numeric_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].round(4)
        
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True
        )
        
        # Скачивание данных
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Скачать данные как CSV",
            data=csv,
            file_name=f"backtest_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with tab5:
    st.header("⚙️ Управление настройками")
    st.markdown("Здесь вы можете сохранить и загрузить настройки фильтров и отображения.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📤 Экспорт настроек")
        st.markdown("Сохраните текущие настройки в файл для последующего использования.")
        
        # Получаем текущие настройки
        current_settings = {
            "selected_symbols": selected_symbols,
            "selected_strategies": selected_strategies,
            "start_date": start_date.strftime('%Y-%m-%d') if start_date else None,
            "end_date": end_date.strftime('%Y-%m-%d') if end_date else None,
            "chart_type": chart_type if 'chart_type' in locals() else "PNL по сделкам",
            "show_columns": show_columns if 'show_columns' in locals() else ['symbol', 'strategy_name', 'type', 'entry_price', 'exit_price', 'PNL', 'PNL_percentage', 'holding_period', 'opened_at'],
            "max_rows": max_rows if 'max_rows' in locals() else 100
        }
        
        # Создаем JSON для экспорта
        settings_json = export_settings(
            current_settings["selected_symbols"],
            current_settings["selected_strategies"],
            start_date,
            end_date,
            current_settings["chart_type"],
            current_settings["show_columns"],
            current_settings["max_rows"]
        )
        
        # Кнопка скачивания
        st.download_button(
            label="💾 Скачать настройки",
            data=settings_json,
            file_name=f"backtest_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Скачивает текущие настройки фильтров и отображения"
        )
        
        # Показываем текущие настройки
        st.markdown("**Текущие настройки:**")
        st.json(current_settings)
    
    with col2:
        st.subheader("📥 Импорт настроек")
        st.markdown("Загрузите ранее сохраненные настройки из файла.")
        
        # Загрузка файла
        uploaded_file = st.file_uploader(
            "Выберите JSON файл с настройками:",
            type=['json'],
            help="Выберите файл с настройками, экспортированный ранее"
        )
        
        if uploaded_file is not None:
            # Импортируем настройки
            imported_settings = import_settings(uploaded_file)
            
            if imported_settings:
                st.success("✅ Настройки успешно загружены!")
                
                # Показываем загруженные настройки
                st.markdown("**Загруженные настройки:**")
                st.json(imported_settings)
                
                # Кнопка применения настроек
                if st.button("🔄 Применить настройки", type="primary"):
                    # Применяем настройки
                    new_symbols, new_strategies, new_start_date, new_end_date, new_chart_type, new_show_columns, new_max_rows = apply_settings(
                        imported_settings, symbols, strategies, min_date, max_date
                    )
                    
                    if new_symbols is not None:
                        # Сохраняем настройки в session state
                        st.session_state.imported_symbols = new_symbols
                        st.session_state.imported_strategies = new_strategies
                        st.session_state.imported_start_date = new_start_date
                        st.session_state.imported_end_date = new_end_date
                        st.session_state.imported_chart_type = new_chart_type
                        st.session_state.imported_show_columns = new_show_columns
                        st.session_state.imported_max_rows = new_max_rows
                        
                        st.success("✅ Настройки применены! Обновляем страницу...")
                        st.rerun()
                    else:
                        st.error("❌ Не удалось применить настройки!")
            else:
                st.error("❌ Ошибка при загрузке файла!")
    
    # Раздел с предустановленными настройками
    st.markdown("---")
    st.subheader("🎯 Предустановленные настройки")
    st.markdown("Быстро примените популярные комбинации настроек.")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Топ-стратегии", help="Показать только лучшие стратегии"):
            # Находим топ-3 стратегии по PNL
            strategy_metrics = loader.get_strategy_metrics(filtered_df)
            top_strategies = strategy_metrics.nlargest(3, 'total_pnl')['strategy_name'].tolist()
            st.session_state.imported_strategies = top_strategies
            st.session_state.imported_symbols = selected_symbols  # Оставляем текущие символы
            st.success("✅ Применены настройки для топ-стратегий!")
            st.rerun()
    
    with col2:
        if st.button("💰 Топ-монеты", help="Показать только лучшие монеты"):
            # Находим топ-5 монет по PNL
            symbol_metrics = loader.get_symbol_metrics(filtered_df)
            top_symbols = symbol_metrics.nlargest(5, 'total_pnl')['symbol'].tolist()
            st.session_state.imported_symbols = top_symbols
            st.session_state.imported_strategies = selected_strategies  # Оставляем текущие стратегии
            st.success("✅ Применены настройки для топ-монет!")
            st.rerun()
    
    with col3:
        if st.button("📅 Последний месяц", help="Показать данные за последний месяц"):
            if max_date:
                last_month = (pd.Timestamp(max_date) - pd.Timedelta(days=30)).date()
                st.session_state.imported_start_date = last_month
                st.session_state.imported_end_date = max_date.date()
                st.success("✅ Применены настройки для последнего месяца!")
                st.rerun()
    
    with col4:
        if st.button("🎯 Настройки по умолчанию", help="Загрузить example_settings.json"):
            try:
                with open('example_settings.json', 'r', encoding='utf-8') as f:
                    default_settings = json.load(f)
                
                new_symbols, new_strategies, new_start_date, new_end_date, new_chart_type, new_show_columns, new_max_rows = apply_settings(
                    default_settings, symbols, strategies, min_date, max_date
                )
                
                if new_symbols is not None:
                    st.session_state.imported_symbols = new_symbols
                    st.session_state.imported_strategies = new_strategies
                    st.session_state.imported_start_date = new_start_date
                    st.session_state.imported_end_date = new_end_date
                    st.session_state.imported_chart_type = new_chart_type
                    st.session_state.imported_show_columns = new_show_columns
                    st.session_state.imported_max_rows = new_max_rows
                    
                    st.success("✅ Загружены настройки по умолчанию!")
                    st.rerun()
                else:
                    st.error("❌ Не удалось загрузить настройки по умолчанию!")
            except FileNotFoundError:
                st.error("❌ Файл example_settings.json не найден!")
            except Exception as e:
                st.error(f"❌ Ошибка при загрузке настроек: {str(e)}")
    
    # Информация о настройках
    st.markdown("---")
    st.subheader("ℹ️ Информация")
    st.markdown("""
    **Что сохраняется в настройках:**
    - Выбранные символы (монеты)
    - Выбранные стратегии
    - Временной период (даты начала и окончания)
    - Тип графика для отображения
    - Колонки для отображения в таблице
    - Максимальное количество строк в таблице
    
    **Как использовать:**
    1. При первом запуске автоматически загружаются настройки из example_settings.json
    2. Настройте фильтры и отображение по своему усмотрению
    3. Перейдите на вкладку "Настройки"
    4. Нажмите "Скачать настройки" для сохранения
    5. Для загрузки выберите файл и нажмите "Применить настройки"
    6. Используйте кнопку "🎯 Настройки по умолчанию" для возврата к исходным настройкам
    """)

# Футер
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Backtest Dashboard | Создано с помощью Streamlit и Plotly</p>
    </div>
    """,
    unsafe_allow_html=True
)
