import pytest
from src.services import investment_bank
from datetime import datetime

@pytest.fixture
def sample_transactions():
    return [
        {"Дата операции": "2023-01-15", "Сумма операции": 1423},
        {"Дата операции": "2023-01-20", "Сумма операции": 567},
        {"Дата операции": "2023-02-10", "Сумма операции": 1234},
    ]

def test_investment_bank(sample_transactions):
    assert investment_bank("2023-01", sample_transactions, 100) == 10  # (1500-1423) + (600-567) = 77 + 33 = 110