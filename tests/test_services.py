from __future__ import annotations

import pytest

from src.services import (investment_bank, person_transfers_search, phone_number_search,
                          profitable_cashback_categories, simple_search)


class TestServices:
    @pytest.fixture
    def sample_transactions(self):
        return [
            {
                "Дата операции": "2023-01-01",
                "Категория": "Супермаркеты",
                "Кешбэк": 10.0,
                "Сумма операции": 1007.0,
                "Описание": "Покупка в магазине",
            },
            {
                "Дата операции": "2023-01-02",
                "Категория": "Рестораны",
                "Кешбэк": 5.0,
                "Сумма операции": 493.0,
                "Описание": "Ужин в ресторане",
            },
            {
                "Дата операции": "invalid-date",
                "Категория": "Invalid",
                "Кешбэк": "invalid",
                "Сумма операции": "invalid",
                "Описание": "Invalid",
            },
        ]

    def test_profitable_cashback_categories(self, sample_transactions):
        result = profitable_cashback_categories(sample_transactions, 2023, 1)
        assert "Супермаркеты" in result
        assert result["Супермаркеты"] == 10.0

    def test_profitable_cashback_invalid_month(self):
        with pytest.raises(ValueError):
            profitable_cashback_categories([], 2023, 13)

    def test_profitable_cashback_invalid_year(self):
        with pytest.raises(ValueError):
            profitable_cashback_categories([], 1000, 1)

    def test_profitable_cashback_invalid_transaction(self, sample_transactions):
        result = profitable_cashback_categories(sample_transactions, 2023, 1)
        assert "Invalid" not in result

    @pytest.mark.parametrize("limit,expected", [(10, 10.0), (50, 50.0), (100, 100.0)])
    def test_investment_bank(self, sample_transactions, limit, expected):
        result = investment_bank("2023-01", sample_transactions, limit)
        assert result == expected

    def test_investment_bank_invalid_month(self):
        with pytest.raises(ValueError):
            investment_bank("2023-13", [], 10)

    def test_investment_bank_invalid_limit(self):
        with pytest.raises(ValueError):
            investment_bank("2023-01", [], -1)

    def test_investment_bank_invalid_transaction(self, sample_transactions):
        result = investment_bank("2023-01", sample_transactions, 10)
        assert result == 10.0

    def test_simple_search(self, sample_transactions):
        result = simple_search("магазине", sample_transactions)
        assert len(result) == 1
        assert result[0]["Описание"] == "Покупка в магазине"

    def test_simple_search_case_sensitive(self, sample_transactions):
        result = simple_search("МАГАЗИНЕ", sample_transactions, case_sensitive=True)
        assert len(result) == 0

    def test_simple_search_empty_query(self):
        assert simple_search("", []) == []

    def test_phone_number_search(self):
        transactions = [
            {"Описание": "Платеж +7 123 456-78-90", "Категория": "Мобильная связь"},
            {"Описание": "Без номера", "Категория": "Другое"},
        ]
        result = phone_number_search(transactions)
        assert len(result) == 1

    def test_phone_number_search_custom_pattern(self):
        transactions = [{"Описание": "Платеж +1-234-567-8900", "Категория": "Мобильная связь"}]
        result = phone_number_search(transactions, phone_pattern=r"\+1-\d{3}-\d{3}-\d{4}")
        assert len(result) == 1

    def test_person_transfers_search(self):
        transactions = [
            {"Описание": "Перевод Иванов И.", "Категория": "Переводы"},
            {"Описание": "Платеж в магазин", "Категория": "Супермаркеты"},
        ]
        result = person_transfers_search(transactions)
        assert len(result) == 1
        assert result[0]["Категория"] == "Переводы"

    def test_person_transfers_search_custom_pattern(self):
        transactions = [{"Описание": "Перевод John D.", "Категория": "Переводы"}]
        result = person_transfers_search(transactions, name_pattern=r"[A-Z][a-z]+\s[A-Z]\.")
        assert len(result) == 1
