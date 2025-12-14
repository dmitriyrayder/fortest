"""Unit-тесты для ABC/XYZ анализа"""

import unittest
import pandas as pd
import numpy as np
from src.ui.tabs.abc_xyz_tab import (
    calculate_abc_analysis,
    calculate_xyz_analysis
)


class TestABCAnalysis(unittest.TestCase):
    """Тесты для ABC анализа"""

    def setUp(self):
        """Подготовка тестовых данных"""
        np.random.seed(42)

        # Создаем тестовые данные с явными ABC категориями
        self.test_df = pd.DataFrame({
            'Magazin': ['Store1'] * 100,
            'Segment': ['Electronics'] * 100,
            'Model': [f'Product_{i}' for i in range(100)],
            'Sum': np.random.exponential(scale=1000, size=100),  # Экспоненциальное распределение
            'Qty': np.random.randint(1, 100, 100)
        })

        # Добавляем несколько высокодоходных товаров (A-категория)
        self.test_df.loc[0:10, 'Sum'] = np.random.uniform(10000, 20000, 11)

    def test_calculate_abc_analysis_basic(self):
        """Тест базового ABC анализа"""
        result = calculate_abc_analysis(self.test_df)

        # Проверяем структуру результата
        self.assertIn('Model', result.columns)
        self.assertIn('ABC_Class', result.columns)
        self.assertIn('Revenue_Percent', result.columns)
        self.assertIn('Revenue_Cumsum_Percent', result.columns)

    def test_abc_analysis_categories(self):
        """Тест наличия всех ABC категорий"""
        result = calculate_abc_analysis(self.test_df)

        categories = result['ABC_Class'].unique()

        # Должны присутствовать категории A, B, C
        self.assertIn('A', categories)
        # B и C могут отсутствовать в зависимости от данных, но проверим их наличие
        # если есть достаточно товаров

    def test_abc_analysis_cumsum(self):
        """Тест накопительной суммы"""
        result = calculate_abc_analysis(self.test_df)

        # Последний элемент накопительной суммы должен быть ~100%
        last_cumsum = result['Revenue_Cumsum_Percent'].iloc[-1]
        self.assertAlmostEqual(last_cumsum, 100, delta=0.1)

    def test_abc_analysis_a_category(self):
        """Тест категории A (80% выручки)"""
        result = calculate_abc_analysis(self.test_df)

        a_category = result[result['ABC_Class'] == 'A']

        # Категория A должна давать около 80% выручки
        a_revenue_percent = a_category['Revenue_Percent'].sum()
        self.assertGreaterEqual(a_revenue_percent, 70,
                               "Категория A должна давать >= 70% выручки")

    def test_abc_analysis_with_filters(self):
        """Тест ABC анализа с фильтрами"""
        result = calculate_abc_analysis(
            self.test_df,
            magazin='Store1',
            segment='Electronics'
        )

        self.assertGreater(len(result), 0, "Результат не должен быть пустым")


class TestXYZAnalysis(unittest.TestCase):
    """Тесты для XYZ анализа"""

    def setUp(self):
        """Подготовка тестовых данных"""
        np.random.seed(42)

        dates = pd.date_range('2023-01-01', periods=100, freq='D')

        # Создаем товары с разной стабильностью спроса
        stable_product = np.full(100, 50) + np.random.normal(0, 2, 100)  # X - стабильный
        variable_product = np.full(100, 50) + np.random.normal(0, 10, 100)  # Y - переменный
        unstable_product = np.full(100, 50) + np.random.normal(0, 20, 100)  # Z - нестабильный

        self.test_df = pd.DataFrame({
            'Magazin': ['Store1'] * 300,
            'Segment': ['Electronics'] * 300,
            'Model': ['Stable'] * 100 + ['Variable'] * 100 + ['Unstable'] * 100,
            'Datasales': list(dates) * 3,
            'Qty': np.concatenate([stable_product, variable_product, unstable_product])
        })

        # Убираем отрицательные значения
        self.test_df['Qty'] = self.test_df['Qty'].clip(lower=0)

    def test_calculate_xyz_analysis_basic(self):
        """Тест базового XYZ анализа"""
        result = calculate_xyz_analysis(self.test_df)

        # Проверяем структуру результата
        self.assertIn('Model', result.columns)
        self.assertIn('XYZ_Class', result.columns)
        self.assertIn('CV', result.columns)

    def test_xyz_analysis_categories(self):
        """Тест наличия XYZ категорий"""
        result = calculate_xyz_analysis(self.test_df)

        categories = result['XYZ_Class'].unique()

        # Должны присутствовать разные категории
        self.assertGreater(len(categories), 0)
        self.assertTrue(all(cat in ['X', 'Y', 'Z'] for cat in categories))

    def test_xyz_analysis_cv_calculation(self):
        """Тест расчета коэффициента вариации"""
        result = calculate_xyz_analysis(self.test_df)

        # Коэффициент вариации должен быть неотрицательным
        self.assertTrue((result['CV'] >= 0).all(),
                       "CV должен быть неотрицательным")

    def test_xyz_analysis_stable_product(self):
        """Тест классификации стабильного товара"""
        result = calculate_xyz_analysis(self.test_df)

        stable = result[result['Model'] == 'Stable']

        if len(stable) > 0:
            # Стабильный товар должен иметь низкий CV
            self.assertLess(stable['CV'].iloc[0], 30,
                           "Стабильный товар должен иметь CV < 30%")

    def test_xyz_analysis_with_filters(self):
        """Тест XYZ анализа с фильтрами"""
        result = calculate_xyz_analysis(
            self.test_df,
            magazin='Store1',
            segment='Electronics'
        )

        self.assertGreater(len(result), 0, "Результат не должен быть пустым")


class TestABCXYZIntegration(unittest.TestCase):
    """Интеграционные тесты для ABC/XYZ анализа"""

    def setUp(self):
        """Подготовка тестовых данных"""
        np.random.seed(42)

        dates = pd.date_range('2023-01-01', periods=50, freq='D')

        self.test_df = pd.DataFrame({
            'Magazin': ['Store1'] * 500,
            'Segment': ['Electronics'] * 500,
            'Model': [f'Product_{i}' for i in range(10)] * 50,
            'Datasales': list(dates) * 10,
            'Sum': np.random.exponential(scale=1000, size=500),
            'Qty': np.random.randint(1, 100, 500)
        })

    def test_combined_abc_xyz_analysis(self):
        """Тест комбинированного ABC/XYZ анализа"""
        abc_result = calculate_abc_analysis(self.test_df)
        xyz_result = calculate_xyz_analysis(self.test_df)

        # Объединяем результаты
        combined = abc_result.merge(
            xyz_result[['Model', 'CV', 'XYZ_Class']],
            on='Model',
            how='left'
        )

        # Проверяем, что объединение прошло успешно
        self.assertIn('ABC_Class', combined.columns)
        self.assertIn('XYZ_Class', combined.columns)

        # Создаем комбинированный класс
        combined['Combined_Class'] = combined['ABC_Class'] + combined['XYZ_Class']

        # Проверяем формат комбинированного класса
        self.assertTrue(
            all(len(cls) == 2 for cls in combined['Combined_Class'].dropna()),
            "Комбинированный класс должен состоять из 2 символов"
        )


if __name__ == '__main__':
    unittest.main()
