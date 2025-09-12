"""
Модуль для загрузки и обработки данных бэктестов из JSON-файлов.
"""

import json
import pandas as pd
import os
from typing import List, Dict, Any
from datetime import datetime
import streamlit as st


class BacktestDataLoader:
    """Класс для загрузки и обработки данных бэктестов."""
    
    def __init__(self, data_folder: str):
        """
        Инициализация загрузчика данных.
        
        Args:
            data_folder: Путь к папке с JSON-файлами
        """
        self.data_folder = data_folder
        self.df = None
        self.raw_data = []
    
    @st.cache_data
    def load_all_data(_self) -> pd.DataFrame:
        """
        Загружает все JSON-файлы из папки и объединяет в DataFrame.
        
        Returns:
            pd.DataFrame: Объединенные данные всех сделок
        """
        all_trades = []
        
        # Получаем список всех JSON-файлов
        json_files = [f for f in os.listdir(_self.data_folder) if f.endswith('.json')]
        
        for file_name in json_files:
            file_path = os.path.join(_self.data_folder, file_name)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Добавляем информацию о файле к каждой сделке
                for trade in data.get('trades', []):
                    trade['file_name'] = file_name
                    trade['considering_timeframes'] = data.get('considering_timeframes', [])
                    all_trades.append(trade)
                    
            except Exception as e:
                st.warning(f"Ошибка при загрузке файла {file_name}: {str(e)}")
                continue
        
        if not all_trades:
            st.error("Не найдено ни одного файла с данными!")
            return pd.DataFrame()
        
        # Создаем DataFrame
        df = pd.DataFrame(all_trades)
        
        # Конвертируем временные метки в datetime
        df['opened_at'] = pd.to_datetime(df['opened_at'], unit='ms')
        df['closed_at'] = pd.to_datetime(df['closed_at'], unit='ms')
        
        # Добавляем дополнительные колонки
        df['duration_hours'] = df['holding_period'] / 3600  # длительность в часах
        df['is_profitable'] = df['PNL'] > 0
        df['is_long'] = df['type'] == 'long'
        
        return df
    
    def get_unique_symbols(self) -> List[str]:
        """Возвращает список уникальных символов."""
        if self.df is None:
            self.df = self.load_all_data()
        return sorted(self.df['symbol'].unique().tolist())
    
    def get_unique_strategies(self) -> List[str]:
        """Возвращает список уникальных стратегий."""
        if self.df is None:
            self.df = self.load_all_data()
        return sorted(self.df['strategy_name'].unique().tolist())
    
    def get_date_range(self) -> tuple:
        """
        Возвращает минимальную и максимальную даты в данных.
        
        Returns:
            tuple: (min_date, max_date) в формате datetime
        """
        if self.df is None:
            self.df = self.load_all_data()
        
        if self.df.empty:
            return None, None
        
        min_date = self.df['opened_at'].min()
        max_date = self.df['opened_at'].max()
        
        return min_date, max_date
    
    def filter_data(self, symbols: List[str] = None, strategies: List[str] = None, 
                   start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Фильтрует данные по символам, стратегиям и временному периоду.
        
        Args:
            symbols: Список символов для фильтрации
            strategies: Список стратегий для фильтрации
            start_date: Начальная дата в формате 'YYYY-MM-DD'
            end_date: Конечная дата в формате 'YYYY-MM-DD'
            
        Returns:
            pd.DataFrame: Отфильтрованные данные
        """
        if self.df is None:
            self.df = self.load_all_data()
        
        filtered_df = self.df.copy()
        
        if symbols:
            filtered_df = filtered_df[filtered_df['symbol'].isin(symbols)]
        
        if strategies:
            filtered_df = filtered_df[filtered_df['strategy_name'].isin(strategies)]
        
        # Фильтрация по датам
        if start_date:
            start_datetime = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['opened_at'] >= start_datetime]
        
        if end_date:
            end_datetime = pd.to_datetime(end_date) + pd.Timedelta(days=1)  # Включаем весь день
            filtered_df = filtered_df[filtered_df['opened_at'] < end_datetime]
        
        return filtered_df
    
    def get_strategy_metrics(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Вычисляет метрики по стратегиям.
        
        Args:
            df: DataFrame для анализа (если None, используется весь датасет)
            
        Returns:
            pd.DataFrame: Метрики по стратегиям
        """
        if df is None:
            df = self.df if self.df is not None else self.load_all_data()
        
        if df.empty:
            return pd.DataFrame()
        
        metrics = df.groupby('strategy_name').agg({
            'PNL': ['sum', 'mean', 'median', 'std', 'count'],
            'PNL_percentage': ['mean', 'median', 'std'],
            'holding_period': ['mean', 'median'],
            'fee': ['sum', 'mean', 'median'],
            'is_profitable': 'sum'
        }).round(4)
        
        # Упрощаем названия колонок
        metrics.columns = [
            'total_pnl', 'avg_pnl', 'median_pnl', 'std_pnl', 'trades_count',
            'avg_pnl_pct', 'median_pnl_pct', 'std_pnl_pct',
            'avg_holding_hours', 'median_holding_hours',
            'total_fees', 'avg_fee', 'median_fee',
            'profitable_trades'
        ]
        
        # Добавляем дополнительные метрики
        metrics['win_rate'] = (metrics['profitable_trades'] / metrics['trades_count'] * 100).round(2)
        
        # Сбрасываем индекс, чтобы strategy_name стала обычной колонкой
        metrics = metrics.reset_index()
        
        # Вычисляем профит-фактор для каждой стратегии отдельно
        profit_factors = []
        for strategy in metrics['strategy_name']:
            strategy_df = df[df['strategy_name'] == strategy]
            gross_profit = strategy_df[strategy_df['PNL'] > 0]['PNL'].sum()
            gross_loss = abs(strategy_df[strategy_df['PNL'] < 0]['PNL'].sum())
            
            if gross_loss > 0:
                profit_factor = gross_profit / gross_loss
            else:
                profit_factor = float('inf') if gross_profit > 0 else 0
            
            profit_factors.append(round(profit_factor, 2))
        
        metrics['profit_factor'] = profit_factors
        
        # Вычисляем математическое ожидание (ожидаемая прибыль на сделку)
        expected_values = []
        for strategy in metrics['strategy_name']:
            strategy_df = df[df['strategy_name'] == strategy]
            expected_value = strategy_df['PNL'].mean()
            expected_values.append(round(expected_value, 4))
        
        metrics['expected_value'] = expected_values
        
        return metrics
    
    def get_symbol_metrics(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Вычисляет метрики по символам.
        
        Args:
            df: DataFrame для анализа (если None, используется весь датасет)
            
        Returns:
            pd.DataFrame: Метрики по символам
        """
        if df is None:
            df = self.df if self.df is not None else self.load_all_data()
        
        if df.empty:
            return pd.DataFrame()
        
        metrics = df.groupby('symbol').agg({
            'PNL': ['sum', 'mean', 'median', 'std', 'count'],
            'PNL_percentage': ['mean', 'median', 'std'],
            'holding_period': ['mean', 'median'],
            'fee': ['sum', 'mean', 'median'],
            'is_profitable': 'sum'
        }).round(4)
        
        # Упрощаем названия колонок
        metrics.columns = [
            'total_pnl', 'avg_pnl', 'median_pnl', 'std_pnl', 'trades_count',
            'avg_pnl_pct', 'median_pnl_pct', 'std_pnl_pct',
            'avg_holding_hours', 'median_holding_hours',
            'total_fees', 'avg_fee', 'median_fee',
            'profitable_trades'
        ]
        
        # Добавляем дополнительные метрики
        metrics['win_rate'] = (metrics['profitable_trades'] / metrics['trades_count'] * 100).round(2)
        
        # Сбрасываем индекс, чтобы symbol стала обычной колонкой
        metrics = metrics.reset_index()
        
        # Вычисляем профит-фактор для каждого символа отдельно
        profit_factors = []
        expected_values = []
        
        for symbol in metrics['symbol']:
            symbol_df = df[df['symbol'] == symbol]
            gross_profit = symbol_df[symbol_df['PNL'] > 0]['PNL'].sum()
            gross_loss = abs(symbol_df[symbol_df['PNL'] < 0]['PNL'].sum())
            
            if gross_loss > 0:
                profit_factor = gross_profit / gross_loss
            else:
                profit_factor = float('inf') if gross_profit > 0 else 0
            
            profit_factors.append(round(profit_factor, 2))
            
            # Математическое ожидание
            expected_value = symbol_df['PNL'].mean()
            expected_values.append(round(expected_value, 4))
        
        metrics['profit_factor'] = profit_factors
        metrics['expected_value'] = expected_values
        
        return metrics
    
    def get_cumulative_pnl(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Вычисляет накопленный PNL по времени.
        
        Args:
            df: DataFrame для анализа (если None, используется весь датасет)
            
        Returns:
            pd.DataFrame: Данные с накопленным PNL
        """
        if df is None:
            df = self.df if self.df is not None else self.load_all_data()
        
        if df.empty:
            return pd.DataFrame()
        
        # Сортируем по времени закрытия
        df_sorted = df.sort_values('closed_at').copy()
        
        # Вычисляем накопленный PNL
        df_sorted['cumulative_pnl'] = df_sorted['PNL'].cumsum()
        df_sorted['trade_number'] = range(1, len(df_sorted) + 1)
        
        return df_sorted[['closed_at', 'trade_number', 'PNL', 'cumulative_pnl', 'symbol', 'strategy_name']]
    
    def get_overall_metrics(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Вычисляет общие метрики для всего датасета.
        
        Args:
            df: DataFrame для анализа (если None, используется весь датасет)
            
        Returns:
            Dict: Словарь с общими метриками
        """
        if df is None:
            df = self.df if self.df is not None else self.load_all_data()
        
        if df.empty:
            return {}
        
        # Базовые метрики
        total_trades = len(df)
        total_pnl = df['PNL'].sum()
        avg_pnl = df['PNL'].mean()
        median_pnl = df['PNL'].median()
        std_pnl = df['PNL'].std()
        
        # Прибыльные и убыточные сделки
        profitable_trades = df[df['PNL'] > 0]
        losing_trades = df[df['PNL'] < 0]
        
        win_rate = (len(profitable_trades) / total_trades * 100) if total_trades > 0 else 0
        
        # Профит-фактор
        gross_profit = profitable_trades['PNL'].sum() if not profitable_trades.empty else 0
        gross_loss = abs(losing_trades['PNL'].sum()) if not losing_trades.empty else 0
        
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
        else:
            profit_factor = float('inf') if gross_profit > 0 else 0
        
        # Математическое ожидание
        expected_value = avg_pnl
        
        # Дополнительные метрики
        max_profit = df['PNL'].max()
        max_loss = df['PNL'].min()
        
        # Коэффициент Шарпа (упрощенный)
        sharpe_ratio = (avg_pnl / std_pnl) if std_pnl > 0 else 0
        
        return {
            'total_trades': total_trades,
            'total_pnl': round(total_pnl, 2),
            'avg_pnl': round(avg_pnl, 4),
            'median_pnl': round(median_pnl, 4),
            'std_pnl': round(std_pnl, 4),
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'expected_value': round(expected_value, 4),
            'max_profit': round(max_profit, 2),
            'max_loss': round(max_loss, 2),
            'sharpe_ratio': round(sharpe_ratio, 4),
            'gross_profit': round(gross_profit, 2),
            'gross_loss': round(gross_loss, 2)
        }
