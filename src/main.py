import json

from src.services import investment_bank
from src.views import home_page

if __name__ == "__main__":
    transactions = [
        {"Дата операции": "2023-01-15", "Сумма операции": 1423},
        {"Дата операции": "2023-01-20", "Сумма операции": 567},
        {"Дата операции": "2023-01-25", "Сумма операции": 890},
    ]
    print(investment_bank("2023-01", transactions, 100))

    result = home_page("2023-01-01 12:00:00")
    print(json.dumps(result, indent=2, ensure_ascii=False))
