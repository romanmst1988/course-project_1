from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import events_page, home_page


class TestViews:
    @pytest.fixture
    def mock_transactions(self):
        data = {
            "Дата операции": ["2023-01-01", "2023-01-02"],
            "Номер карты": ["1234", "5678"],  # Упрощенные номера карт
            "Сумма операции": [1000.0, 500.0],
            "Кешбэк": [10.0, 5.0],
            "Категория": ["Супермаркеты", "Рестораны"],
            "Описание": ["Покупка в магазине", "Ужин в ресторане"],
        }
        df = pd.DataFrame(data)
        df["Дата операции"] = pd.to_datetime(df["Дата операции"])
        return df

    @pytest.fixture
    def mock_settings_file(self, tmp_path):
        settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}
        file_path = tmp_path / "user_settings.json"
        file_path.write_text(json.dumps(settings))
        return file_path

    @pytest.fixture
    def mock_settings_file_invalid(self, tmp_path):
        file_path = tmp_path / "user_settings.json"
        file_path.write_text("invalid json")
        return file_path

    @pytest.mark.parametrize(
        "time,expected",
        [
            ("2023-01-01 06:00:00", "Доброе утро"),
            ("2023-01-01 12:00:00", "Добрый день"),
            ("2023-01-01 18:00:00", "Добрый вечер"),
            ("2023-01-01 23:00:00", "Доброй ночи"),
        ],
    )
    def test_home_page_greeting(self, mocker, time, expected, mock_settings_file, mock_transactions):
        mocker.patch("src.views.load_transactions", return_value=mock_transactions)
        mocker.patch("src.views.get_currency_rates", return_value=[])
        mocker.patch("src.views.get_stock_prices", return_value=[])
        mocker.patch("src.views.DATA_DIR", Path("dummy"))

        result = home_page(time)
        assert result["greeting"] == expected

    def test_home_page_structure(self, mocker, mock_transactions, mock_settings_file):
        # Мокируем текущий месяц, чтобы обе транзакции попадали в выборку
        mock_date = mocker.patch("src.views.datetime")
        mock_date.now.return_value = datetime(2023, 1, 3)  # После дат транзакций
        mock_date.strptime.side_effect = lambda *args, **kw: datetime.strptime(*args, **kw)

        mocker.patch("src.views.load_transactions", return_value=mock_transactions)
        mocker.patch("src.views.get_currency_rates", return_value=[{"currency": "USD", "rate": 75.0}])
        mocker.patch("src.views.get_stock_prices", return_value=[{"stock": "AAPL", "price": 150.0}])
        mocker.patch("src.views.DATA_DIR", Path("dummy"))

        result = home_page("2023-01-01 12:00:00")
        assert "greeting" in result
        assert "cards" in result
        assert len(result["cards"]) == 2  # Теперь должно быть 2 карты
        assert "top_transactions" in result
        assert "currency_rates" in result
        assert "stock_prices" in result

    def test_home_page_missing_columns(self, mocker, mock_settings_file):
        mock_transactions = pd.DataFrame({"wrong_column": [1, 2]})
        mocker.patch("src.views.load_transactions", return_value=mock_transactions)
        mocker.patch("src.views.DATA_DIR", Path("dummy"))

        with pytest.raises(ValueError):
            home_page("2023-01-01 12:00:00")

    def test_home_page_settings_error(self, mocker, mock_settings_file_invalid):
        mocker.patch("src.views.load_transactions", return_value=pd.DataFrame())
        mocker.patch("src.views.DATA_DIR", Path("dummy"))
        with patch("builtins.open", side_effect=json.JSONDecodeError("Expecting value", "", 0)):
            with pytest.raises(json.JSONDecodeError):
                home_page("2023-01-01 12:00:00")

    def test_events_page_structure(self, mocker, mock_transactions, mock_settings_file):
        mocker.patch("src.views.get_currency_rates", return_value=[])
        mocker.patch("src.views.get_stock_prices", return_value=[])

        result = events_page(mock_transactions, "2023-01-01")
        assert "expenses" in result
        assert "income" in result
        assert "currency_rates" in result
        assert "stock_prices" in result

    def test_events_page_date_ranges(self, mocker, mock_transactions, mock_settings_file):
        mocker.patch("src.views.get_currency_rates", return_value=[])
        mocker.patch("src.views.get_stock_prices", return_value=[])

        for date_range in ["W", "M", "Y", "ALL"]:
            result = events_page(mock_transactions, "2023-01-01", date_range)
            assert result is not None

    def test_events_page_invalid_date_range(self, mocker, mock_transactions, mock_settings_file):
        with pytest.raises(ValueError):
            events_page(mock_transactions, "2023-01-01", "INVALID")

    def test_events_page_settings_error(self, mocker, mock_transactions, mock_settings_file_invalid):
        with patch("builtins.open", side_effect=json.JSONDecodeError("Expecting value", "", 0)):
            with pytest.raises(json.JSONDecodeError):
                events_page(mock_transactions, "2023-01-01")
