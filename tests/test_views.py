import pytest
from datetime import datetime
from src.views import get_greeting


def test_get_greeting():
    """Тест функции получения приветствия"""
    # Тест с утренним временем
    assert get_greeting("2023-01-01 08:00:00") == "Доброе утро"

    # Тест с передачей datetime объекта вместо строки
    with pytest.raises(TypeError):
        get_greeting(datetime(2023, 1, 1, 8, 0, 0))
