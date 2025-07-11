import pytest
from datetime import datetime
from unittest.mock import patch, Mock
from src.views import get_greeting
import pandas as pd

@pytest.fixture
def sample_transactions():
    return pd.DataFrame({
        'Номер карты': ['1234567890123456', '1234567890123456', '9876543210987654'],
        'Сумма платежа': [100, 200, 300],
        'Дата операции': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'Категория': ['A', 'B', 'A'],
        'Описание': ['Test1', 'Test2', 'Test3']
    })

def test_get_greeting():
    assert get_greeting(datetime(2023,1,1,6,0)) == "Доброе утро"
    assert get_greeting(datetime(2023,1,1,13,0)) == "Добрый день"

def test_process_cards(sample_transactions, process_cards=None):
    result = process_cards(sample_transactions)
    assert len(result) == 2
    assert result[0]['last_digits'] == '3456'
    assert result[0]['total_spent'] == 300