import pytest
import logging
import pandas as pd

# Полностью отключаем все плагины логирования pytest
pytest_plugins = []

# Отключаем стандартное логирование
logging.basicConfig(level=logging.CRITICAL)


def pytest_configure(config):
    # Отключаем все встроенные обработчики логирования pytest
    config.option.log_level = "CRITICAL"
    config.option.log_format = "%(levelname)s %(message)s"
    config.option.log_cli = False
    config.option.log_file = None


@pytest.fixture
def sample_transactions():
    return [
        {"Дата операции": "2023-01-15", "Сумма операции": 1423},
        {"Дата операции": "2023-01-20", "Сумма операции": 567},
        {"Дата операции": "2023-02-10", "Сумма операции": 1234},
    ]


@pytest.fixture
def sample_transactions_1():
    return pd.DataFrame(
        {
            "Номер карты": ["1234567890123456", "1234567890123456", "9876543210987654"],
            "Сумма платежа": [100, 200, 300],
            "Дата операции": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Категория": ["A", "B", "A"],
            "Описание": ["Test1", "Test2", "Test3"],
        }
    )
