from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.reports import spending_by_category, spending_by_weekday, spending_by_workday
from src.services import investment_bank, profitable_cashback_categories
from src.utils import load_transactions
from src.views import events_page, home_page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"


def main() -> None:
    """Основная функция для демонстрации всех функциональностей."""
    try:
        transactions = load_transactions(DATA_DIR / "operations.xlsx")

        transactions_list: List[Dict[str, Any]] = [
            {
                "Дата операции": str(row["Дата операции"]),
                "Категория": str(row["Категория"]),
                "Кешбэк": float(row.get("Кешбэк", 0)),
                "Сумма операции": float(row["Сумма операции"]),
                "Описание": str(row["Описание"]),
                "Номер карты": str(row.get("Номер карты", "")),
            }
            for _, row in transactions.iterrows()
        ]

        current_date = datetime.now()
        date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
        date_only_str = current_date.strftime("%Y-%m-%d")

        home_data = home_page(date_str)
        print("Home Page Data:")
        print(json.dumps(home_data, indent=2, ensure_ascii=False))

        events_data = events_page(transactions, date_only_str)
        print("\nEvents Page Data:")
        print(json.dumps(events_data, indent=2, ensure_ascii=False))

        cashback = profitable_cashback_categories(transactions_list, current_date.year, current_date.month)
        print("\nProfitable Cashback Categories:")
        print(json.dumps(cashback, indent=2, ensure_ascii=False))

        savings = investment_bank(current_date.strftime("%Y-%m"), transactions_list, 50)
        print(f"\nInvestment Savings: {savings:.2f}")

        category_spending = spending_by_category(transactions, "Супермаркеты")
        print("\nSpending by Category:")
        print(category_spending)

        weekday_spending = spending_by_weekday(transactions)
        print("\nSpending by Weekday:")
        print(weekday_spending)

        workday_spending = spending_by_workday(transactions)
        print("\nSpending by Workday/Weekend:")
        print(workday_spending)

    except Exception as e:
        logger.error("Ошибка в main: %s", str(e))


if __name__ == "__main__":
    main()
