"""Утилиты для обработки данных"""

import pandas as pd
import numpy as np
import streamlit as st
from scipy.signal import savgol_filter


def remove_outliers_iqr(data, multiplier=1.5):
    """Удаляет выбросы методом IQR с корректным расчетом границ"""
    if len(data) < 4:
        return data

    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR

    return data.clip(lower=lower_bound, upper=upper_bound)


def smooth_data(data, method='ma', window=7):
    """Сглаживает данные различными методами"""
    if method == 'ma':
        return data.rolling(window=window, min_periods=1, center=True).mean()
    elif method == 'ema':
        return data.ewm(span=window, adjust=False).mean()
    elif method == 'savgol' and len(data) >= window:
        if window % 2 == 0:
            window += 1
        try:
            return pd.Series(
                savgol_filter(data, window_length=window, polyorder=min(3, window-1)),
                index=data.index
            )
        except:
            return data.rolling(window=window, min_periods=1, center=True).mean()
    else:
        return data


def prepare_prophet_data(df, remove_outliers=False, smooth_method=None, smooth_window=7):
    """Подготавливает данные для Prophet с корректной агрегацией"""
    daily_sales = df.groupby('Datasales')['Qty'].sum().reset_index()
    daily_sales.columns = ['ds', 'y']

    original_data = daily_sales.copy()

    if remove_outliers:
        daily_sales['y'] = remove_outliers_iqr(daily_sales['y'])

    if smooth_method:
        daily_sales['y'] = smooth_data(daily_sales['y'], method=smooth_method, window=smooth_window)

    daily_sales['y'] = daily_sales['y'].clip(lower=0)

    return daily_sales, original_data


def calculate_segment_volatility(df, magazin, segment):
    """Корректный расчет волатильности сегмента"""
    filtered = df[(df['Magazin'] == magazin) & (df['Segment'] == segment)]

    if len(filtered) < 2:
        return 0.3

    daily_sales = filtered.groupby('Datasales')['Qty'].sum()

    if daily_sales.mean() == 0:
        return 0.3

    volatility = daily_sales.std() / daily_sales.mean()

    return min(max(volatility, 0), 1)
