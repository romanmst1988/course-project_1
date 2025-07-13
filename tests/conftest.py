from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

import pandas as pd
import pytest


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура с тестовыми транзакциями"""
    now = datetime.now()
    return [
        {
            "Дата операции": (now - timedelta(days=i)).strftime("%Y-%m-%d"),
            "Номер карты": "1234567890123456",
            "Сумма платежа": 100 * (i + 1),
            "Категория": "Супермаркеты" if i % 2 else "Развлечения",
            "Описание": f"Покупка {i}",
            "Кешбэк": 1 * (i + 1),
            "Сумма операции": 100 * (i + 1),
        }
        for i in range(10)
    ]


@pytest.fixture
def mock_transactions(sample_transactions):
    """Фикстура с DataFrame транзакций для тестов"""
    df = pd.DataFrame(sample_transactions)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    return df


@pytest.fixture
def mock_requests(monkeypatch):
    """Фикстура для мокирования requests"""

    def mock_get(*args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self._json = {"rates": {"USD": 75.0, "EUR": 85.0}, "Global Quote": {"05. price": "150.0"}}

            def json(self):
                return self._json

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)
