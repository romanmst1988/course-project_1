import json
import logging
from datetime import datetime
from typing import List, Dict, Any


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    try:
        total_saved = 0.0
        year, month = map(int, month.split('-'))

        for transaction in transactions:
            trans_date = datetime.strptime(transaction["Дата операции"], "%Y-%m-%d")
            if trans_date.year == year and trans_date.month == month:
                amount = transaction["Сумма операции"]
                rounded = ((amount // limit) + 1) * limit
                saved = rounded - amount
                total_saved += saved

        return round(total_saved, 2)
    except Exception as e:
        logging.error(f"Error in investment_bank: {e}")
        return 0.0

if __name__ == "__main__":
    print(investment_bank)

