from __future__ import annotations
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from src.utils import load_transactions, get_greeting, get_currency_rates, get_stock_prices


class TestUtils:
    def test_load_transactions_success(self, mocker):
        mock_data = MagicMock()
        # mock_read_excel = mocker.patch("pandas.read_excel", return_value=mock_data)
        mocker.patch.dict("os.environ", {"TESTING": "True"})

        result = load_transactions("dummy_path.xlsx")
        assert result == mock_data

    def test_load_transactions_failure(self, mocker):
        mocker.patch("pandas.read_excel", side_effect=Exception("File error"))
        with pytest.raises(Exception):
            load_transactions("invalid_path.xlsx")

    def test_load_transactions_file_not_found(self, mocker):
        mocker.patch.dict("os.environ", {"TESTING": "False"})
        mocker.patch("pathlib.Path.exists", return_value=False)
        with pytest.raises(FileNotFoundError):
            load_transactions("nonexistent.xlsx")

    @pytest.mark.parametrize(
        "time,expected",
        [
            (datetime(2023, 1, 1, 5, 0), "Доброе утро"),
            (datetime(2023, 1, 1, 11, 59), "Доброе утро"),
            (datetime(2023, 1, 1, 12, 0), "Добрый день"),
            (datetime(2023, 1, 1, 16, 59), "Добрый день"),
            (datetime(2023, 1, 1, 17, 0), "Добрый вечер"),
            (datetime(2023, 1, 1, 22, 59), "Добрый вечер"),
            (datetime(2023, 1, 1, 23, 0), "Доброй ночи"),
            (datetime(2023, 1, 1, 4, 59), "Доброй ночи"),
        ],
    )
    def test_get_greeting(self, time, expected):
        assert get_greeting(time) == expected

    def test_get_currency_rates(self, mocker):
        mocker.patch.dict("os.environ", {"TESTING": "True"})
        result = get_currency_rates(["USD", "EUR"])
        assert len(result) == 2
        assert all(item["rate"] == 1.0 for item in result)

    def test_get_currency_rates_api_error(self, mocker):
        mocker.patch("requests.get", side_effect=Exception("API error"))
        mocker.patch.dict("os.environ", {"TESTING": "False", "CURRENCY_API_KEY": "test"})
        with pytest.raises(Exception):
            get_currency_rates(["USD", "EUR"])

    def test_get_currency_rates_no_api_key(self, mocker):
        mocker.patch.dict("os.environ", {"TESTING": "False", "CURRENCY_API_KEY": ""})
        with pytest.raises(ValueError, match="Не задан API ключ для курсов валют"):
            get_currency_rates(["USD", "EUR"])

    def test_get_stock_prices(self, mocker):
        mocker.patch.dict("os.environ", {"TESTING": "True"})
        result = get_stock_prices(["AAPL"])
        assert len(result) == 1
        assert result[0]["price"] == 100.0

    def test_get_stock_prices_api_error(self, mocker):
        mocker.patch("requests.get", side_effect=Exception("API error"))
        mocker.patch.dict("os.environ", {"TESTING": "False", "STOCK_API_KEY": "test"})
        with pytest.raises(Exception):
            get_stock_prices(["AAPL"])

    def test_get_stock_prices_no_api_key(self, mocker):
        mocker.patch.dict("os.environ", {"TESTING": "False", "STOCK_API_KEY": ""})
        with pytest.raises(ValueError, match="Не задан API ключ для цен акций"):
            get_stock_prices(["AAPL"])
