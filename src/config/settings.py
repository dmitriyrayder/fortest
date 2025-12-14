"""Конфигурация приложения"""

# Параметры страницы
PAGE_CONFIG = {
    "page_title": "🏪 Система прогнозирования продаж",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Обязательные колонки в данных
REQUIRED_COLUMNS = [
    'Magazin', 'Datasales', 'Art', 'Describe',
    'Model', 'Segment', 'Price', 'Qty', 'Sum'
]

# Параметры прогнозирования
FORECAST_CONFIG = {
    'min_days': 7,
    'max_days': 90,
    'default_days': 30,
    'min_records': 10
}

# Параметры Prophet модели
PROPHET_PARAMS = {
    'daily_seasonality': False,
    'weekly_seasonality': True,
    'yearly_seasonality': True,
    'seasonality_mode': 'multiplicative',
    'changepoint_prior_scale': 0.05,
    'seasonality_prior_scale': 10
}

# Методы сглаживания
SMOOTH_METHODS = {
    'none': 'Без сглаживания',
    'ma': 'Скользящее среднее',
    'ema': 'Экспоненциальное сглаживание',
    'savgol': 'Фильтр Савицкого-Голея'
}

# Перевод дней недели
WEEKDAY_TRANSLATION = {
    'Monday': 'Понедельник',
    'Tuesday': 'Вторник',
    'Wednesday': 'Среда',
    'Thursday': 'Четверг',
    'Friday': 'Пятница',
    'Saturday': 'Суббота',
    'Sunday': 'Воскресенье'
}
