from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from src.main import main


class TestMain:
    @pytest.fixture
    def mock_transactions(self):
        data = {
            "Дата операции": ["2023-01-01", "2023-01-02"],
            "Категория": ["Супермаркеты", "Рестораны"],
            "Кешбэк": [10.0, 5.0],
            "Сумма операции": [1000.0, 500.0],
            "Описание": ["Покупка 1", "Покупка 2"],
            "Номер карты": ["1234", "5678"],
        }
        return pd.DataFrame(data)

    @patch("src.main.load_transactions")
    @patch("src.main.home_page")
    @patch("src.main.events_page")
    @patch("src.main.profitable_cashback_categories")
    @patch("src.main.investment_bank")
    @patch("src.main.spending_by_category")
    @patch("src.main.spending_by_weekday")
    @patch("src.main.spending_by_workday")
    def test_main_success(
        self,
        mock_workday,
        mock_weekday,
        mock_category,
        mock_bank,
        mock_cashback,
        mock_events,
        mock_home,
        mock_load,
        mock_transactions,
    ):
        mock_load.return_value = mock_transactions
        mock_home.return_value = {}
        mock_events.return_value = {}
        mock_cashback.return_value = {}
        mock_bank.return_value = 100.0
        mock_category.return_value = pd.DataFrame()
        mock_weekday.return_value = pd.DataFrame()
        mock_workday.return_value = pd.DataFrame()

        main()
        assert mock_load.called
        assert mock_home.called
        assert mock_events.called
        assert mock_cashback.called
        assert mock_bank.called
        assert mock_category.called
        assert mock_weekday.called
        assert mock_workday.called

    @patch("src.main.load_transactions", side_effect=Exception("Test error"))
    @patch("src.main.logger")
    def test_main_error(self, mock_logger, mock_load):
        main()
        assert mock_load.called
        assert mock_logger.error.called
