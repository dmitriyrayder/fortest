"""Функции визуализации данных"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def plot_data_preprocessing(original, processed, title):
    """Визуализирует эффект предобработки данных"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=original['ds'],
        y=original['y'],
        mode='lines',
        name='Оригинальные данные',
        line=dict(color='lightgray', width=1),
        opacity=0.5
    ))

    fig.add_trace(go.Scatter(
        x=processed['ds'],
        y=processed['y'],
        mode='lines',
        name='Обработанные данные',
        line=dict(color='#667eea', width=2)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Дата",
        yaxis_title="Количество",
        hovermode='x unified',
        height=400
    )

    return fig


def plot_forecast(train_data, forecast, title):
    """Визуализирует прогноз"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=train_data['ds'],
        y=train_data['y'],
        mode='lines',
        name='Фактические продажи',
        line=dict(color='#1f77b4', width=2)
    ))

    forecast_future = forecast[forecast['ds'] > train_data['ds'].max()]

    fig.add_trace(go.Scatter(
        x=forecast_future['ds'],
        y=forecast_future['yhat'],
        mode='lines',
        name='Прогноз',
        line=dict(color='#ff7f0e', width=2, dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=forecast_future['ds'].tolist() + forecast_future['ds'].tolist()[::-1],
        y=forecast_future['yhat_upper'].tolist() + forecast_future['yhat_lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(255, 127, 14, 0.2)',
        line=dict(color='rgba(255, 127, 14, 0)'),
        name='Доверительный интервал',
        showlegend=True
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Дата",
        yaxis_title="Количество",
        hovermode='x unified',
        height=500
    )

    return fig


def plot_prophet_components(model, forecast):
    """Визуализирует компоненты модели Prophet"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['trend'],
        mode='lines',
        name='Тренд',
        line=dict(color='#2ca02c', width=2)
    ))

    fig.update_layout(
        title="📊 Декомпозиция: Тренд",
        xaxis_title="Дата",
        yaxis_title="Значение тренда",
        hovermode='x unified',
        height=400
    )

    return fig


def plot_sales_by_weekday(df, title="📅 Продажи по дням недели"):
    """Визуализирует продажи по дням недели"""
    # Добавляем день недели
    df_copy = df.copy()
    df_copy['weekday'] = pd.to_datetime(df_copy['Datasales']).dt.day_name()

    # Порядок дней недели
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    # Агрегация по дням недели
    weekday_stats = df_copy.groupby('weekday').agg({
        'Qty': 'sum',
        'Sum': 'sum'
    }).reindex(weekday_order)

    # Замена на русские названия
    weekday_stats.index = weekday_ru

    fig = go.Figure()

    # Столбцы - количество
    fig.add_trace(go.Bar(
        x=weekday_ru,
        y=weekday_stats['Qty'],
        name='Количество',
        marker_color='#667eea',
        yaxis='y'
    ))

    # Линия - выручка
    fig.add_trace(go.Scatter(
        x=weekday_ru,
        y=weekday_stats['Sum'],
        name='Выручка',
        line=dict(color='#ff7f0e', width=3),
        yaxis='y2'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="День недели",
        yaxis=dict(title="Количество", side='left'),
        yaxis2=dict(title="Выручка (ГРН)", overlaying='y', side='right'),
        hovermode='x unified',
        height=450,
        showlegend=True
    )

    return fig


def plot_top_products(df, top_n=10, title="🏆 ТОП товаров по выручке"):
    """Визуализирует топ товаров по выручке"""
    # Агрегация по товарам
    product_stats = df.groupby('Art').agg({
        'Describe': 'first',
        'Sum': 'sum',
        'Qty': 'sum'
    }).sort_values('Sum', ascending=False).head(top_n)

    # Создаем краткие названия
    product_stats['short_name'] = product_stats['Describe'].str[:30] + '...'

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=product_stats['short_name'][::-1],
        x=product_stats['Sum'][::-1],
        orientation='h',
        marker=dict(
            color=product_stats['Sum'][::-1],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Выручка")
        ),
        text=product_stats['Sum'][::-1].round(0),
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Выручка: %{x:.0f} ГРН<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Выручка (ГРН)",
        yaxis_title="Товар",
        height=400,
        showlegend=False
    )

    return fig


def plot_monthly_revenue_trend(df, title="📈 Динамика выручки по месяцам"):
    """Визуализирует динамику выручки по месяцам с трендом"""
    df_copy = df.copy()
    df_copy['month'] = pd.to_datetime(df_copy['Datasales']).dt.to_period('M')

    # Агрегация по месяцам
    monthly_stats = df_copy.groupby('month').agg({
        'Sum': 'sum',
        'Qty': 'sum'
    }).reset_index()

    monthly_stats['month_str'] = monthly_stats['month'].astype(str)

    fig = go.Figure()

    # Основная линия выручки
    fig.add_trace(go.Scatter(
        x=monthly_stats['month_str'],
        y=monthly_stats['Sum'],
        mode='lines+markers',
        name='Выручка',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8)
    ))

    # Линия тренда
    z = np.polyfit(range(len(monthly_stats)), monthly_stats['Sum'], 1)
    p = np.poly1d(z)

    fig.add_trace(go.Scatter(
        x=monthly_stats['month_str'],
        y=p(range(len(monthly_stats))),
        mode='lines',
        name='Тренд',
        line=dict(color='red', width=2, dash='dash')
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Месяц",
        yaxis_title="Выручка (ГРН)",
        hovermode='x unified',
        height=450
    )

    return fig


def plot_sales_heatmap(df, title="🔥 Тепловая карта продаж"):
    """Визуализирует heatmap продаж по дням недели и месяцам"""
    df_copy = df.copy()
    df_copy['weekday'] = pd.to_datetime(df_copy['Datasales']).dt.day_name()
    df_copy['month'] = pd.to_datetime(df_copy['Datasales']).dt.to_period('M').astype(str)

    # Порядок дней недели
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_ru = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    # Создаем pivot таблицу
    heatmap_data = df_copy.pivot_table(
        values='Sum',
        index='weekday',
        columns='month',
        aggfunc='sum',
        fill_value=0
    ).reindex(weekday_order)

    heatmap_data.index = weekday_ru

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='YlOrRd',
        hoverongaps=False,
        hovertemplate='Месяц: %{x}<br>День: %{y}<br>Выручка: %{z:.0f} ГРН<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        xaxis_title="Месяц",
        yaxis_title="День недели",
        height=400
    )

    return fig


def plot_daily_sales_distribution(df, title="📊 Распределение продаж по дням недели"):
    """Визуализирует box plot распределения продаж по дням недели"""
    df_copy = df.copy()
    df_copy['weekday'] = pd.to_datetime(df_copy['Datasales']).dt.day_name()
    df_copy['date'] = pd.to_datetime(df_copy['Datasales']).dt.date

    # Группируем по дате и дню недели
    daily_sales = df_copy.groupby(['date', 'weekday']).agg({
        'Sum': 'sum'
    }).reset_index()

    # Порядок дней недели
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    fig = go.Figure()

    for weekday, weekday_name in zip(weekday_order, weekday_ru):
        weekday_data = daily_sales[daily_sales['weekday'] == weekday]['Sum']

        fig.add_trace(go.Box(
            y=weekday_data,
            name=weekday_name,
            boxmean='sd'
        ))

    fig.update_layout(
        title=title,
        xaxis_title="День недели",
        yaxis_title="Выручка (ГРН)",
        height=450,
        showlegend=False
    )

    return fig


def plot_sales_trend_comparison(df, title="📊 Сравнение периодов продаж"):
    """Сравнивает продажи текущего и предыдущего периода"""
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['Datasales'])

    # Разделяем на два периода
    max_date = df_copy['date'].max()
    mid_date = max_date - pd.Timedelta(days=len(df_copy['date'].unique()) // 2)

    period1 = df_copy[df_copy['date'] < mid_date].copy()
    period2 = df_copy[df_copy['date'] >= mid_date].copy()

    # Агрегация по дням от начала периода
    period1['day_num'] = (period1['date'] - period1['date'].min()).dt.days
    period2['day_num'] = (period2['date'] - period2['date'].min()).dt.days

    period1_agg = period1.groupby('day_num')['Sum'].sum()
    period2_agg = period2.groupby('day_num')['Sum'].sum()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=period1_agg.index,
        y=period1_agg.values,
        mode='lines',
        name=f'Период 1 ({period1["date"].min().strftime("%Y-%m-%d")} - {period1["date"].max().strftime("%Y-%m-%d")})',
        line=dict(color='#667eea', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=period2_agg.index,
        y=period2_agg.values,
        mode='lines',
        name=f'Период 2 ({period2["date"].min().strftime("%Y-%m-%d")} - {period2["date"].max().strftime("%Y-%m-%d")})',
        line=dict(color='#ff7f0e', width=2)
    ))

    fig.update_layout(
        title=title,
        xaxis_title="День от начала периода",
        yaxis_title="Выручка (ГРН)",
        hovermode='x unified',
        height=450
    )

    return fig
