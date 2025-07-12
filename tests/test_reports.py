from unittest.mock import patch
import pandas as pd


def test_spending_by_category_basic():
    """Тест базовой функциональности без использования фикстур"""

    # Создаем тестовые данные прямо в тесте
    pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["2023-01-15", "2023-02-20"]),
            "Категория": ["Food", "Transport"],
            "Сумма платежа": [1000, 500],
        }
    )


def test_error_handling():
    """Тест обработки ошибок без логирования"""
    from src.reports import spending_by_category

    with patch("pandas.DataFrame.loc", side_effect=Exception("Test error")):
        result = spending_by_category(pd.DataFrame(), "Food")
        assert result == {}
