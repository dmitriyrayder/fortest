"""Модели прогнозирования на основе Prophet"""

import numpy as np
import streamlit as st
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from ..config.settings import PROPHET_PARAMS


def train_prophet_model(data, periods=30):
    """Обучает модель Prophet"""
    try:
        model = Prophet(**PROPHET_PARAMS)
        model.fit(data)

        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        forecast['yhat'] = forecast['yhat'].clip(lower=0)
        forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
        forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0)

        return model, forecast

    except Exception as e:
        st.error(f"❌ Ошибка при обучении модели: {str(e)}")
        return None, None


def calculate_model_accuracy(train_data, model):
    """Корректный расчет метрик точности"""
    try:
        historical_forecast = model.predict(train_data[['ds']])

        y_true = train_data['y'].values
        y_pred = historical_forecast['yhat'].values

        min_len = min(len(y_true), len(y_pred))
        y_true = y_true[:min_len]
        y_pred = y_pred[:min_len]

        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))

        mask = y_true != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        else:
            mape = 0

        r2 = r2_score(y_true, y_pred)

        return {
            'MAE': mae,
            'RMSE': rmse,
            'MAPE': mape,
            'R2': r2
        }
    except Exception as e:
        st.warning(f"Не удалось рассчитать метрики точности: {str(e)}")
        return None


def get_forecast_scenarios(forecast_df, volatility):
    """Корректный расчет сценариев прогноза"""
    realistic = forecast_df['yhat'].values
    lower_bound = forecast_df['yhat_lower'].values
    upper_bound = forecast_df['yhat_upper'].values

    pessimistic = np.maximum(lower_bound, 0)
    optimistic = np.maximum(upper_bound, 0)

    return realistic, optimistic, pessimistic
