"""Функции визуализации данных"""

import plotly.graph_objects as go


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
