"""Unit-тесты для модели Prophet"""

import unittest
import pandas as pd
import numpy as np
from src.models.prophet_model import (
    train_prophet_model,
    calculate_model_accuracy,
    get_forecast_scenarios
)


class TestProphetModel(unittest.TestCase):
    """Тесты для функций модели Prophet"""

    def setUp(self):
        """Подготовка тестовых данных"""
        np.random.seed(42)

        # Создаем синтетический временной ряд
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        trend = np.linspace(100, 200, 100)
        seasonality = 20 * np.sin(np.linspace(0, 8*np.pi, 100))
        noise = np.random.normal(0, 5, 100)

        self.test_data = pd.DataFrame({
            'ds': dates,
            'y': trend + seasonality + noise
        })

        # Убираем отрицательные значения
        self.test_data['y'] = self.test_data['y'].clip(lower=0)

    def test_train_prophet_model_basic(self):
        """Тест базового обучения модели Prophet"""
        model, forecast = train_prophet_model(self.test_data, periods=10)

        # Проверяем, что модель и прогноз созданы
        self.assertIsNotNone(model, "Модель должна быть создана")
        self.assertIsNotNone(forecast, "Прогноз должен быть создан")

        # Проверяем структуру прогноза
        self.assertIn('ds', forecast.columns)
        self.assertIn('yhat', forecast.columns)
        self.assertIn('yhat_lower', forecast.columns)
        self.assertIn('yhat_upper', forecast.columns)

    def test_train_prophet_model_forecast_length(self):
        """Тест длины прогноза"""
        periods = 30
        model, forecast = train_prophet_model(self.test_data, periods=periods)

        # Проверяем длину прогноза (исходные данные + periods)
        expected_length = len(self.test_data) + periods
        self.assertEqual(len(forecast), expected_length)

    def test_train_prophet_model_non_negative(self):
        """Тест, что прогноз не содержит отрицательных значений"""
        model, forecast = train_prophet_model(self.test_data, periods=10)

        # Все значения прогноза должны быть неотрицательными
        self.assertTrue((forecast['yhat'] >= 0).all(),
                       "Прогноз не должен содержать отрицательных значений")
        self.assertTrue((forecast['yhat_lower'] >= 0).all(),
                       "Нижняя граница не должна быть отрицательной")
        self.assertTrue((forecast['yhat_upper'] >= 0).all(),
                       "Верхняя граница не должна быть отрицательной")

    def test_calculate_model_accuracy(self):
        """Тест расчета метрик точности модели"""
        model, _ = train_prophet_model(self.test_data, periods=10)
        metrics = calculate_model_accuracy(self.test_data, model)

        # Проверяем, что все метрики рассчитаны
        self.assertIsNotNone(metrics, "Метрики должны быть рассчитаны")
        self.assertIn('MAE', metrics)
        self.assertIn('RMSE', metrics)
        self.assertIn('MAPE', metrics)
        self.assertIn('R2', metrics)

        # Проверяем, что метрики имеют разумные значения
        self.assertGreater(metrics['MAE'], 0, "MAE должна быть положительной")
        self.assertGreater(metrics['RMSE'], 0, "RMSE должна быть положительной")
        self.assertGreaterEqual(metrics['MAPE'], 0, "MAPE должна быть неотрицательной")

    def test_calculate_model_accuracy_r2_range(self):
        """Тест, что R² находится в допустимом диапазоне"""
        model, _ = train_prophet_model(self.test_data, periods=10)
        metrics = calculate_model_accuracy(self.test_data, model)

        # R² обычно находится между -∞ и 1, но для хорошей модели > 0
        self.assertLessEqual(metrics['R2'], 1, "R² не должен превышать 1")

    def test_get_forecast_scenarios(self):
        """Тест получения сценариев прогноза"""
        model, forecast = train_prophet_model(self.test_data, periods=10)

        # Берем только будущие прогнозы
        future_forecast = forecast.tail(10)

        realistic, optimistic, pessimistic = get_forecast_scenarios(
            future_forecast,
            volatility=0.3
        )

        # Проверяем длину сценариев
        self.assertEqual(len(realistic), 10)
        self.assertEqual(len(optimistic), 10)
        self.assertEqual(len(pessimistic), 10)

        # Проверяем порядок сценариев: pessimistic <= realistic <= optimistic
        self.assertTrue(np.all(pessimistic <= realistic),
                       "Пессимистичный сценарий должен быть <= реалистичного")
        self.assertTrue(np.all(realistic <= optimistic),
                       "Реалистичный сценарий должен быть <= оптимистичного")

        # Проверяем неотрицательность
        self.assertTrue(np.all(pessimistic >= 0),
                       "Пессимистичный сценарий не должен быть отрицательным")

    def test_train_prophet_model_with_empty_data(self):
        """Тест обучения модели на пустых данных"""
        empty_data = pd.DataFrame({'ds': [], 'y': []})

        model, forecast = train_prophet_model(empty_data, periods=10)

        # С пустыми данными модель не должна обучиться
        self.assertIsNone(model, "Модель не должна быть создана на пустых данных")
        self.assertIsNone(forecast, "Прогноз не должен быть создан на пустых данных")


class TestProphetModelIntegration(unittest.TestCase):
    """Интеграционные тесты для модели Prophet"""

    def setUp(self):
        """Подготовка тестовых данных"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')

        self.test_data = pd.DataFrame({
            'ds': dates,
            'y': 100 + np.random.normal(0, 10, 100).cumsum()
        })

        self.test_data['y'] = self.test_data['y'].clip(lower=0)

    def test_full_forecast_pipeline(self):
        """Тест полного пайплайна прогнозирования"""
        # Обучаем модель
        model, forecast = train_prophet_model(self.test_data, periods=30)

        self.assertIsNotNone(model)
        self.assertIsNotNone(forecast)

        # Рассчитываем метрики
        metrics = calculate_model_accuracy(self.test_data, model)

        self.assertIsNotNone(metrics)
        self.assertIn('MAE', metrics)

        # Получаем сценарии
        future_forecast = forecast.tail(30)
        realistic, optimistic, pessimistic = get_forecast_scenarios(
            future_forecast,
            volatility=0.2
        )

        # Проверяем весь пайплайн
        self.assertEqual(len(realistic), 30)
        self.assertTrue(np.all(realistic >= 0))


if __name__ == '__main__':
    unittest.main()
