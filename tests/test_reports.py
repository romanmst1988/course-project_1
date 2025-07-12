import pytest
from unittest.mock import patch, mock_open
import pandas as pd
from datetime import datetime


def test_spending_by_category_basic():
    """Тест базовой функциональности без использования фикстур"""
    from src.reports import spending_by_category

    # Создаем тестовые данные прямо в тесте
    test_data = pd.DataFrame({
        "Дата операции": pd.to_datetime(["2023-01-15", "2023-02-20"]),
        "Категория": ["Food", "Transport"],
        "Сумма платежа": [1000, 500]
    })

    # with patch('views.datetime') as mock_dt:
    #     mock_dt.now.return_value = datetime(2023, 4, 1)
    #     mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
    #
    #     result = spending_by_category(test_data, "Food", "2023-04-01")
    #     assert result == {'2023-01-01 00:00:00': 1000.0}


def test_error_handling():
    """Тест обработки ошибок без логирования"""
    from src.reports import spending_by_category

    with patch('pandas.DataFrame.loc', side_effect=Exception("Test error")):
        result = spending_by_category(pd.DataFrame(), "Food")
        assert result == {}