import pytest

mport
pytest
from datetime import datetime, timedelta
import pandas as pd
from unittest.mock import patch
import logging
from your_module import spending_by_category  # Импортируем тестируемую функцию


# Фикстура для тестовых данных
@pytest.fixture
def sample_transactions():
    return pd.DataFrame({
        "Дата операции": pd.to_datetime([
            "2023-01-15", "2023-02-20", "2023-03-10",
            "2023-04-05", "2023-01-25", "2023-03-28"
        ]),
        "Категория": [
            "Food", "Transport", "Food",
            "Transport", "Food", "Entertainment"
        ],
        "Сумма платежа": [1000, 500, 1500, 700, 2000, 3000]
    })


# Тест на корректную работу функции
def test_spending_by_category_success(sample_transactions):
    result = spending_by_category(sample_transactions, "Food", "2023-04-01")
    expected = {
        pd.Timestamp('2023-01-01'): 3000.0,
        pd.Timestamp('2023-02-01'): 0.0,
        pd.Timestamp('2023-03-01'): 1500.0
    }
    assert result == expected


# Тест на обработку пустого DataFrame
def test_empty_dataframe():
    empty_df = pd.DataFrame(columns=["Дата операции", "Категория", "Сумма платежа"])
    result = spending_by_category(empty_df, "Any")
    assert result == {}


# Тест на отсутствие категории
def test_category_not_found(sample_transactions):
    result = spending_by_category(sample_transactions, "NonExisting", "2023-04-01")
    assert result == {}


# Тест с использованием текущей даты
def test_with_current_date(sample_transactions):
    with patch('your_module.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 4, 1)
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        result = spending_by_category(sample_transactions, "Food")
        expected = {
            pd.Timestamp('2023-01-01'): 3000.0,
            pd.Timestamp('2023-02-01'): 0.0,
            pd.Timestamp('2023-03-01'): 1500.0
        }
        assert result == expected


# Тест на обработку ошибок
def test_error_handling(sample_transactions, caplog):
    with patch('pandas.DataFrame.loc') as mock_loc:
        mock_loc.side_effect = Exception("Test error")
        with pytest.raises(Exception):
            spending_by_category(sample_transactions, "Food")

        # Проверяем, что ошибка залогирована
        assert "Error in spending_by_category: Test error" in caplog.text


# Параметризованный тест для разных категорий
@pytest.mark.parametrize("category, expected", [
    ("Food", {
        pd.Timestamp('2023-01-01'): 3000.0,
        pd.Timestamp('2023-02-01'): 0.0,
        pd.Timestamp('2023-03-01'): 1500.0
    }),
    ("Transport", {
        pd.Timestamp('2023-01-01'): 0.0,
        pd.Timestamp('2023-02-01'): 500.0,
        pd.Timestamp('2023-03-01'): 0.0
    }),
    ("Entertainment", {
        pd.Timestamp('2023-01-01'): 0.0,
        pd.Timestamp('2023-02-01'): 0.0,
        pd.Timestamp('2023-03-01'): 3000.0
    })
])
def test_parametrized_categories(sample_transactions, category, expected):
    result = spending_by_category(sample_transactions, category, "2023-04-01")
    assert result == expected


# Фикстура для проверки записи в файл
@pytest.fixture
def mock_open():
    with patch("builtins.open", create=True) as mock_open:
        yield mock_open


# Тест декоратора report_decorator
def test_report_decorator(sample_transactions, mock_open):
    # Вызываем функцию с декоратором
    result = spending_by_category(sample_transactions, "Food", "2023-04-01")

    # Проверяем, что файл был открыт для записи
    mock_open.assert_called_once()

    # Проверяем, что результат корректный
    expected = {
        pd.Timestamp('2023-01-01'): 3000.0,
        pd.Timestamp('2023-02-01'): 0.0,
        pd.Timestamp('2023-03-01'): 1500.0
    }
    assert result == expected