# 🧪 Руководство по тестированию

Полное руководство по запуску и написанию тестов для проекта Sales Forecasting System.

## 📋 Содержание

- [Установка зависимостей](#установка-зависимостей)
- [Запуск тестов](#запуск-тестов)
- [Структура тестов](#структура-тестов)
- [Написание тестов](#написание-тестов)
- [Coverage отчеты](#coverage-отчеты)
- [CI/CD интеграция](#cicd-интеграция)

## 🔧 Установка зависимостей

### Основные зависимости

```bash
pip install pytest pytest-cov
```

### Все зависимости для разработки

```bash
pip install -r requirements.txt
```

## 🚀 Запуск тестов

### Запуск всех тестов

```bash
# Базовый запуск
pytest

# С детальным выводом
pytest -v

# С покрытием кода
pytest --cov=src
```

### Запуск конкретных тестов

```bash
# Запуск одного файла
pytest tests/test_data_processing.py

# Запуск одного класса
pytest tests/test_data_processing.py::TestDataProcessing

# Запуск одного теста
pytest tests/test_data_processing.py::TestDataProcessing::test_remove_outliers_iqr

# Запуск тестов по паттерну
pytest -k "test_abc"
```

### Запуск с фильтрами

```bash
# Только быстрые тесты
pytest -m "not slow"

# Только unit-тесты
pytest -m unit

# Только интеграционные тесты
pytest -m integration
```

## 📁 Структура тестов

```
tests/
├── __init__.py
├── test_data_processing.py      # Тесты обработки данных
├── test_prophet_model.py         # Тесты модели Prophet
└── test_abc_xyz_analysis.py      # Тесты ABC/XYZ анализа
```

### Покрытие модулей

| Модуль | Файл тестов | Покрытие |
|--------|-------------|----------|
| `src/utils/data_processing.py` | `test_data_processing.py` | ~90% |
| `src/models/prophet_model.py` | `test_prophet_model.py` | ~85% |
| `src/ui/tabs/abc_xyz_tab.py` | `test_abc_xyz_analysis.py` | ~75% |

## 📝 Написание тестов

### Базовая структура теста

```python
import unittest
from src.module import function_to_test


class TestModuleName(unittest.TestCase):
    """Описание набора тестов"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.test_data = create_test_data()

    def test_feature_name(self):
        """Тест конкретной функции"""
        result = function_to_test(self.test_data)

        self.assertEqual(result, expected_value)
        self.assertIsNotNone(result)
        self.assertTrue(condition)

    def tearDown(self):
        """Очистка после каждого теста (опционально)"""
        pass
```

### Примеры тестов

#### 1. Тест функции с простым результатом

```python
def test_remove_outliers_iqr(self):
    """Тест удаления выбросов методом IQR"""
    data = pd.Series([1, 2, 3, 4, 5, 100, 200])

    result = remove_outliers_iqr(data, multiplier=1.5)

    self.assertTrue(result.max() < 100)
    self.assertEqual(len(result), len(data))
```

#### 2. Тест функции с DataFrame

```python
def test_prepare_prophet_data(self):
    """Тест подготовки данных для Prophet"""
    prophet_data, original_data = prepare_prophet_data(self.test_df)

    # Проверяем структуру
    self.assertIn('ds', prophet_data.columns)
    self.assertIn('y', prophet_data.columns)

    # Проверяем данные
    self.assertTrue((prophet_data['y'] >= 0).all())
```

#### 3. Тест с исключениями

```python
def test_invalid_input(self):
    """Тест на некорректный ввод"""
    with self.assertRaises(ValueError):
        function_with_validation(invalid_data)
```

### Assertions (утверждения)

```python
# Равенство
self.assertEqual(a, b)
self.assertNotEqual(a, b)

# Истинность
self.assertTrue(condition)
self.assertFalse(condition)

# None
self.assertIsNone(value)
self.assertIsNotNone(value)

# Принадлежность
self.assertIn(item, collection)
self.assertNotIn(item, collection)

# Сравнение
self.assertGreater(a, b)
self.assertLess(a, b)
self.assertGreaterEqual(a, b)
self.assertLessEqual(a, b)

# Приблизительное равенство
self.assertAlmostEqual(a, b, places=2)
self.assertAlmostEqual(a, b, delta=0.1)

# Исключения
with self.assertRaises(ExceptionType):
    function_that_raises()
```

## 📊 Coverage отчеты

### Генерация отчета о покрытии

```bash
# HTML отчет
pytest --cov=src --cov-report=html

# Открыть HTML отчет
open htmlcov/index.html  # MacOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Консольный отчет

```bash
# Краткий отчет
pytest --cov=src --cov-report=term

# Детальный отчет с пропущенными строками
pytest --cov=src --cov-report=term-missing
```

### Пример вывода coverage

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/utils/data_processing.py              45      5    89%   23-27
src/models/prophet_model.py               38      6    84%   45-50
src/ui/tabs/abc_xyz_tab.py                67     17    75%   89-105
---------------------------------------------------------------------
TOTAL                                     150     28    81%
```

## 🎯 Лучшие практики

### 1. Именование тестов

```python
# ✅ Хорошо
def test_remove_outliers_with_valid_data(self):
    """Тест удаления выбросов с корректными данными"""
    pass

# ❌ Плохо
def test1(self):
    pass
```

### 2. Один тест = одна проверка

```python
# ✅ Хорошо
def test_function_returns_correct_type(self):
    result = my_function()
    self.assertIsInstance(result, pd.DataFrame)

def test_function_returns_non_empty(self):
    result = my_function()
    self.assertGreater(len(result), 0)

# ❌ Плохо
def test_function(self):
    result = my_function()
    self.assertIsInstance(result, pd.DataFrame)
    self.assertGreater(len(result), 0)
    self.assertIn('column', result.columns)
    # ... много проверок
```

### 3. Использование setUp и tearDown

```python
class TestDataProcessing(unittest.TestCase):

    def setUp(self):
        """Выполняется перед каждым тестом"""
        self.test_df = create_test_dataframe()
        self.temp_file = create_temp_file()

    def tearDown(self):
        """Выполняется после каждого теста"""
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)
```

### 4. Тестирование граничных случаев

```python
def test_empty_input(self):
    """Тест с пустым вводом"""
    result = process_data(pd.DataFrame())
    self.assertIsNotNone(result)

def test_single_element(self):
    """Тест с одним элементом"""
    result = process_data(pd.DataFrame({'col': [1]}))
    self.assertEqual(len(result), 1)

def test_large_input(self):
    """Тест с большим объемом данных"""
    large_df = create_large_dataframe(10000)
    result = process_data(large_df)
    self.assertIsNotNone(result)
```

## 🔄 CI/CD интеграция

### GitHub Actions пример

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## 🐛 Отладка тестов

### Запуск с отладчиком

```bash
# Остановиться при первой ошибке
pytest -x

# Открыть отладчик при ошибке
pytest --pdb

# Показать print() в тестах
pytest -s
```

### Вывод отладочной информации

```python
def test_with_debug_output(self):
    """Тест с отладочным выводом"""
    result = complex_function()

    # Выводится только при ошибке или с флагом -s
    print(f"Result: {result}")
    print(f"Type: {type(result)}")

    self.assertIsNotNone(result)
```

## 📈 Метрики качества

### Целевые показатели

- **Coverage**: > 80%
- **Скорость**: < 30 секунд для всех тестов
- **Стабильность**: 0 flaky tests

### Проверка метрик

```bash
# Coverage
pytest --cov=src --cov-fail-under=80

# Скорость (с плагином pytest-timeout)
pytest --timeout=30

# Список медленных тестов
pytest --durations=10
```

## 📚 Дополнительные ресурсы

- [Pytest документация](https://docs.pytest.org/)
- [unittest документация](https://docs.python.org/3/library/unittest.html)
- [Coverage.py документация](https://coverage.readthedocs.io/)

## 🤝 Участие в разработке

При добавлении нового функционала:

1. Напишите тесты **до** реализации (TDD)
2. Убедитесь, что coverage >= 80%
3. Запустите все тесты перед commit
4. Добавьте docstring к каждому тесту

## ❓ FAQ

**Q: Как запустить только быстрые тесты?**
```bash
pytest -m "not slow"
```

**Q: Как пропустить определенный тест?**
```python
@unittest.skip("Временно отключен")
def test_feature(self):
    pass
```

**Q: Как параметризовать тесты?**
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert double(input) == expected
```

---

**Дата создания**: 2024
**Версия**: 1.0
