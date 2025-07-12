import pytest
from datetime import datetime
import pandas as pd
from src.services import investment_bank


def test_investment_bank(sample_transactions):
    """Тест функции investment_bank"""
    # Преобразуем даты в datetime
    sample_transactions['Дата операции'] = pd.to_datetime(sample_transactions['Дата операции'])

    # result = investment_bank('2023-01', sample_transactions.to_dict('records'), 100)
    # assert result == 110  # (1500-1423) + (600-567) = 77 + 33 = 110