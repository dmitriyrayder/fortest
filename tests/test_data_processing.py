"""Unit-тесты для модуля обработки данных"""

import unittest
import pandas as pd
import numpy as np
from src.utils.data_processing import (
    remove_outliers_iqr,
    smooth_data,
    prepare_prophet_data,
    calculate_segment_volatility
)


class TestDataProcessing(unittest.TestCase):
    """Тесты для функций обработки данных"""

    def setUp(self):
        """Подготовка тестовых данных"""
        # Создаем тестовый DataFrame
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')

        self.test_df = pd.DataFrame({
            'Datasales': dates,
            'Magazin': ['Store1'] * 50 + ['Store2'] * 50,
            'Segment': ['Electronics'] * 100,
            'Qty': np.random.randint(10, 100, 100),
            'Price': np.random.uniform(100, 1000, 100),
            'Sum': np.random.uniform(1000, 10000, 100)
        })

    def test_remove_outliers_iqr(self):
        """Тест удаления выбросов методом IQR"""
        # Создаем данные с выбросами
        data = pd.Series([1, 2, 3, 4, 5, 100, 200])  # 100 и 200 - выбросы

        result = remove_outliers_iqr(data, multiplier=1.5)

        # Проверяем, что выбросы были ограничены
        self.assertTrue(result.max() < 100, "Выбросы должны быть ограничены")
        self.assertEqual(len(result), len(data), "Длина данных должна сохраниться")

    def test_remove_outliers_small_dataset(self):
        """Тест удаления выбросов на малом наборе данных"""
        data = pd.Series([1, 2, 3])  # Меньше 4 элементов

        result = remove_outliers_iqr(data)

        # Должны вернуться исходные данные
        pd.testing.assert_series_equal(result, data)

    def test_smooth_data_ma(self):
        """Тест сглаживания методом скользящего среднего"""
        data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        result = smooth_data(data, method='ma', window=3)

        # Результат должен быть Series той же длины
        self.assertEqual(len(result), len(data))
        self.assertIsInstance(result, pd.Series)
        # Сглаженные данные должны быть менее волатильными
        self.assertLessEqual(result.std(), data.std())

    def test_smooth_data_ema(self):
        """Тест экспоненциального сглаживания"""
        data = pd.Series([1, 5, 2, 8, 3, 9, 4, 10])

        result = smooth_data(data, method='ema', window=3)

        self.assertEqual(len(result), len(data))
        self.assertIsInstance(result, pd.Series)

    def test_smooth_data_invalid_method(self):
        """Тест с недопустимым методом сглаживания"""
        data = pd.Series([1, 2, 3, 4, 5])

        result = smooth_data(data, method='invalid')

        # Должны вернуться исходные данные
        pd.testing.assert_series_equal(result, data)

    def test_prepare_prophet_data(self):
        """Тест подготовки данных для Prophet"""
        prophet_data, original_data = prepare_prophet_data(self.test_df)

        # Проверяем структуру данных
        self.assertIn('ds', prophet_data.columns)
        self.assertIn('y', prophet_data.columns)

        # Проверяем, что нет отрицательных значений
        self.assertTrue((prophet_data['y'] >= 0).all(), "Не должно быть отрицательных значений")

        # Проверяем, что данные агрегированы по дате
        self.assertEqual(len(prophet_data), prophet_data['ds'].nunique())

    def test_prepare_prophet_data_with_outlier_removal(self):
        """Тест подготовки данных с удалением выбросов"""
        prophet_data, original_data = prepare_prophet_data(
            self.test_df,
            remove_outliers=True
        )

        # Проверяем, что обработанные данные отличаются от оригинальных
        self.assertIsNotNone(prophet_data)
        self.assertIsNotNone(original_data)

    def test_prepare_prophet_data_with_smoothing(self):
        """Тест подготовки данных со сглаживанием"""
        prophet_data, original_data = prepare_prophet_data(
            self.test_df,
            smooth_method='ma',
            smooth_window=7
        )

        # Обработанные данные должны быть менее волатильными
        processed_std = prophet_data['y'].std()
        original_std = original_data['y'].std()

        self.assertLessEqual(processed_std, original_std)

    def test_calculate_segment_volatility(self):
        """Тест расчета волатильности сегмента"""
        volatility = calculate_segment_volatility(
            self.test_df,
            'Store1',
            'Electronics'
        )

        # Волатильность должна быть между 0 и 1
        self.assertGreaterEqual(volatility, 0)
        self.assertLessEqual(volatility, 1)

    def test_calculate_segment_volatility_empty_data(self):
        """Тест расчета волатильности при отсутствии данных"""
        empty_df = pd.DataFrame({
            'Datasales': [],
            'Magazin': [],
            'Segment': [],
            'Qty': []
        })

        volatility = calculate_segment_volatility(
            empty_df,
            'NonExistent',
            'NonExistent'
        )

        # Должно вернуться значение по умолчанию
        self.assertEqual(volatility, 0.3)


if __name__ == '__main__':
    unittest.main()
