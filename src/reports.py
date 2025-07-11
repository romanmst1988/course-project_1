import json
import logging
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd


def report_decorator(filename=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            file = filename if filename else f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(file, "w") as f:
                json.dump(result, f)
            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    try:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=90)

        mask = (
                (transactions["Дата операции"] >= start_date) &
                (transactions["Дата операции"] <= end_date) &
                (transactions["Категория"] == category)
        )
        filtered = transactions.loc[mask]

        return filtered.groupby(pd.Grouper(key="Дата операции", freq="M"))["Сумма платежа"].sum().to_dict()
    except Exception as e:
        logging.error(f"Error in spending_by_category: {e}")
        return {}
