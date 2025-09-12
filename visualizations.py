"""
Модуль для создания графиков и визуализаций результатов бэктестов.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any
import numpy as np


class BacktestVisualizer:
    """Класс для создания визуализаций результатов бэктестов."""
    
    def __init__(self):
        """Инициализация визуализатора."""
        pass
    
    def plot_pnl_by_trades(self, df: pd.DataFrame, title: str = "PNL по сделкам") -> go.Figure:
        """
        Создает график PNL по сделкам.
        
        Args:
            df: DataFrame с данными сделок
            title: Заголовок графика
            
        Returns:
            go.Figure: График PNL
        """
        if df.empty:
            return go.Figure()
        
        # Сортируем по времени закрытия
        df_sorted = df.sort_values('closed_at').copy()
        df_sorted['trade_number'] = range(1, len(df_sorted) + 1)
        
        # Создаем график
        fig = go.Figure()
        
        # Добавляем столбцы для прибыльных и убыточных сделок
        profitable_trades = df_sorted[df_sorted['PNL'] > 0]
        losing_trades = df_sorted[df_sorted['PNL'] <= 0]
        
        if not profitable_trades.empty:
            fig.add_trace(go.Bar(
                x=profitable_trades['trade_number'],
                y=profitable_trades['PNL'],
                name='Прибыльные сделки',
                marker_color='green',
                opacity=0.7
            ))
        
        if not losing_trades.empty:
            fig.add_trace(go.Bar(
                x=losing_trades['trade_number'],
                y=losing_trades['PNL'],
                name='Убыточные сделки',
                marker_color='red',
                opacity=0.7
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Номер сделки',
            yaxis_title='PNL (USDT)',
            hovermode='x unified',
            showlegend=True,
            height=400
        )
        
        return fig
    
    def plot_cumulative_pnl(self, df: pd.DataFrame, title: str = "Накопленный PNL") -> go.Figure:
        """
        Создает график накопленного PNL.
        
        Args:
            df: DataFrame с данными сделок
            title: Заголовок графика
            
        Returns:
            go.Figure: График накопленного PNL
        """
        if df.empty:
            return go.Figure()
        
        # Сортируем по времени закрытия
        df_sorted = df.sort_values('closed_at').copy()
        df_sorted['cumulative_pnl'] = df_sorted['PNL'].cumsum()
        df_sorted['trade_number'] = range(1, len(df_sorted) + 1)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_sorted['trade_number'],
            y=df_sorted['cumulative_pnl'],
            mode='lines+markers',
            name='Накопленный PNL',
            line=dict(color='blue', width=2),
            marker=dict(size=4)
        ))
        
        # Добавляем горизонтальную линию на уровне 0
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title=title,
            xaxis_title='Номер сделки',
            yaxis_title='Накопленный PNL (USDT)',
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    def plot_pnl_distribution(self, df: pd.DataFrame, title: str = "Распределение PNL по стратегиям") -> go.Figure:
        """
        Создает boxplot распределения PNL по стратегиям.
        
        Args:
            df: DataFrame с данными сделок
            title: Заголовок графика
            
        Returns:
            go.Figure: Boxplot PNL
        """
        if df.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        strategies = df['strategy_name'].unique()
        
        for strategy in strategies:
            strategy_data = df[df['strategy_name'] == strategy]['PNL']
            
            fig.add_trace(go.Box(
                y=strategy_data,
                name=strategy,
                boxpoints='outliers',
                jitter=0.3,
                pointpos=-1.8
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Стратегия',
            yaxis_title='PNL (USDT)',
            height=500,
            showlegend=False
        )
        
        return fig
    
    def plot_strategy_comparison(self, df: pd.DataFrame, metrics: List[str] = None) -> go.Figure:
        """
        Создает сравнительный график стратегий по различным метрикам.
        
        Args:
            df: DataFrame с данными сделок
            metrics: Список метрик для сравнения
            
        Returns:
            go.Figure: Сравнительный график
        """
        if df.empty:
            return go.Figure()
        
        if metrics is None:
            metrics = ['PNL_percentage', 'holding_period', 'fee']
        
        # Вычисляем средние и медианные значения по стратегиям
        strategy_stats = df.groupby('strategy_name').agg({
            'PNL_percentage': ['mean', 'median'],
            'holding_period': ['mean', 'median'],
            'fee': ['mean', 'median']
        }).round(4)
        
        # Упрощаем названия колонок
        strategy_stats.columns = [
            'avg_pnl_pct', 'median_pnl_pct',
            'avg_holding_period', 'median_holding_period',
            'avg_fee', 'median_fee'
        ]
        
        strategy_stats = strategy_stats.reset_index()
        
        # Создаем subplot
        fig = make_subplots(
            rows=len(metrics), cols=1,
            subplot_titles=[f"Сравнение стратегий: {metric}" for metric in metrics],
            vertical_spacing=0.1
        )
        
        for i, metric in enumerate(metrics, 1):
            avg_col = f'avg_{metric}'
            median_col = f'median_{metric}'
            
            if avg_col in strategy_stats.columns and median_col in strategy_stats.columns:
                fig.add_trace(go.Bar(
                    x=strategy_stats['strategy_name'],
                    y=strategy_stats[avg_col],
                    name=f'Среднее {metric}',
                    marker_color='lightblue',
                    opacity=0.7
                ), row=i, col=1)
                
                fig.add_trace(go.Bar(
                    x=strategy_stats['strategy_name'],
                    y=strategy_stats[median_col],
                    name=f'Медиана {metric}',
                    marker_color='darkblue',
                    opacity=0.7
                ), row=i, col=1)
        
        fig.update_layout(
            title="Сравнительный анализ стратегий",
            height=300 * len(metrics),
            showlegend=True
        )
        
        return fig
    
    def plot_pnl_timeline(self, df: pd.DataFrame, title: str = "PNL по времени") -> go.Figure:
        """
        Создает график PNL по времени.
        
        Args:
            df: DataFrame с данными сделок
            title: Заголовок графика
            
        Returns:
            go.Figure: График PNL по времени
        """
        if df.empty:
            return go.Figure()
        
        # Сортируем по времени закрытия
        df_sorted = df.sort_values('closed_at').copy()
        
        fig = go.Figure()
        
        # Добавляем точки для каждой сделки
        colors = ['green' if pnl > 0 else 'red' for pnl in df_sorted['PNL']]
        
        fig.add_trace(go.Scatter(
            x=df_sorted['closed_at'],
            y=df_sorted['PNL'],
            mode='markers',
            marker=dict(
                color=colors,
                size=8,
                opacity=0.7
            ),
            text=df_sorted['strategy_name'],
            hovertemplate='<b>%{text}</b><br>' +
                         'Время: %{x}<br>' +
                         'PNL: %{y:.2f} USDT<br>' +
                         '<extra></extra>',
            name='Сделки'
        ))
        
        # Добавляем линию накопленного PNL
        df_sorted['cumulative_pnl'] = df_sorted['PNL'].cumsum()
        
        fig.add_trace(go.Scatter(
            x=df_sorted['closed_at'],
            y=df_sorted['cumulative_pnl'],
            mode='lines',
            name='Накопленный PNL',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Время',
            yaxis_title='PNL (USDT)',
            hovermode='x unified',
            height=500
        )
        
        return fig
    
    def plot_win_rate_by_strategy(self, df: pd.DataFrame, title: str = "Процент прибыльных сделок по стратегиям") -> go.Figure:
        """
        Создает график процента прибыльных сделок по стратегиям.
        
        Args:
            df: DataFrame с данными сделок
            title: Заголовок графика
            
        Returns:
            go.Figure: График процента прибыльных сделок
        """
        if df.empty:
            return go.Figure()
        
        # Вычисляем процент прибыльных сделок по стратегиям
        win_rates = df.groupby('strategy_name').agg({
            'is_profitable': ['sum', 'count']
        })
        
        win_rates.columns = ['profitable_trades', 'total_trades']
        win_rates['win_rate'] = (win_rates['profitable_trades'] / win_rates['total_trades'] * 100).round(2)
        win_rates = win_rates.reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=win_rates['strategy_name'],
            y=win_rates['win_rate'],
            marker_color='lightgreen',
            text=win_rates['win_rate'].astype(str) + '%',
            textposition='auto'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Стратегия',
            yaxis_title='Процент прибыльных сделок (%)',
            height=400
        )
        
        return fig
    
    def plot_holding_period_distribution(self, df: pd.DataFrame, title: str = "Распределение времени удержания") -> go.Figure:
        """
        Создает гистограмму распределения времени удержания.
        
        Args:
            df: DataFrame с данными сделок
            title: Заголовок графика
            
        Returns:
            go.Figure: Гистограмма времени удержания
        """
        if df.empty:
            return go.Figure()
        
        # Конвертируем в часы
        holding_hours = df['holding_period'] / 3600
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=holding_hours,
            nbinsx=30,
            marker_color='lightblue',
            opacity=0.7
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='Время удержания (часы)',
            yaxis_title='Количество сделок',
            height=400
        )
        
        return fig
