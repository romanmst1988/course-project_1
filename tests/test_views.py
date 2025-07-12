import pytest
from datetime import datetime
import pandas as pd  # type: ignore
from src.views import get_greeting, process_cards


def test_get_greeting():
    """Тест функции получения приветствия"""
    # Тест с утренним временем
    assert get_greeting("2023-01-01 08:00:00") == "Доброе утро"

    # Тест с передачей datetime объекта вместо строки
    with pytest.raises(TypeError):
        get_greeting(datetime(2023, 1, 1, 8, 0, 0))


# def test_process_cards():
#     """Тест обработки карт"""
#     # Создаем тестовый DataFrame
#     test_data = pd.DataFrame({
#         'Номер карты': ['1234567890123456', '9876543210987654'],
#         'Сумма платежа': [1000, 2000],
#         'Кешбэк': [10, 20]
#     })
#
#     result = process_cards(test_data)
#     assert len(result) == 2
#     assert result[0]['last_digits'] == '3456'