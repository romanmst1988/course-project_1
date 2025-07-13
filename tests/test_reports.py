from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday


class TestReports:
    @pytest.fixture
    def sample_transactions(self):
        data = {
            "Дата операции": [
                (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d"),
                (datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d"),
            ],
            "Категория": ["Супермаркеты", "Супермаркеты", "Рестораны", "Супермаркеты"],
            "Сумма операции": [1000, 2000, 1500, 3000],
        }
        return pd.DataFrame(data)

    def test_spending_by_category(self, sample_transactions):
        result = spending_by_category(sample_transactions, "Супермаркеты")
        assert len(result) == 2
        assert result["Сумма операции"].sum() == 3000

    def test_spending_by_category_with_date(self, sample_transactions):
        date_str = datetime.now().strftime("%Y-%m-%d")
        result = spending_by_category(sample_transactions, "Супермаркеты", date_str)
        assert len(result) == 2

    def test_spending_by_category_error(self, sample_transactions):
        with patch("pandas.to_datetime", side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                spending_by_category(sample_transactions, "Супермаркеты")

    def test_spending_by_weekday(self, sample_transactions):
        result = spending_by_weekday(sample_transactions)
        assert len(result) > 0

    def test_spending_by_weekday_with_date(self, sample_transactions):
        date_str = datetime.now().strftime("%Y-%m-%d")
        result = spending_by_weekday(sample_transactions, date_str)
        assert len(result) > 0

    def test_spending_by_weekday_error(self, sample_transactions):
        with patch("pandas.to_datetime", side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                spending_by_weekday(sample_transactions)

    def test_spending_by_workday(self, sample_transactions):
        result = spending_by_workday(sample_transactions)
        assert len(result) == 2

    def test_spending_by_workday_with_date(self, sample_transactions):
        date_str = datetime.now().strftime("%Y-%m-%d")
        result = spending_by_workday(sample_transactions, date_str)
        assert len(result) == 2

    def test_spending_by_workday_error(self, sample_transactions):
        with patch("pandas.to_datetime", side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                spending_by_workday(sample_transactions)

    def test_report_to_file_decorator(self, tmp_path, sample_transactions, monkeypatch):
        # Перенаправляем создание reports директории в tmp_path
        def mock_path(*args):
            return tmp_path / args[0] if args else tmp_path

        monkeypatch.setattr("src.reports.Path", mock_path)

        # Мокируем open
        mock_open_handler = mock_open()

        with patch("builtins.open", mock_open_handler):
            # Вызываем тестируемую функцию
            result = spending_by_category(sample_transactions, "Супермаркеты")

            # Проверяем что open был вызван
            mock_open_handler.assert_called_once()

            # Проверяем что функция вернула ожидаемый результат
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2

    def test_report_to_file_error(self, tmp_path, sample_transactions):
        with patch("builtins.open", side_effect=Exception("Test error")):
            with patch("src.reports.Path.parent", return_value=tmp_path):
                result = spending_by_category(sample_transactions, "Супермаркеты")
                assert isinstance(result, pd.DataFrame)
