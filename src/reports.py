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
            try:
                with open(file, "w", encoding='utf-8') as f:
                    # Сериализуем datetime и pandas.Timestamp
                    def json_serializer(obj):
                        if isinstance(obj, (datetime, pd.Timestamp)):
                            return obj.strftime('%Y-%m-%d %H:%M:%S')
                        raise TypeError(f"Type {type(obj)} not serializable")

                    json.dump(result, f, default=json_serializer, ensure_ascii=False)
            except Exception as e:
                logging.error(f"Error saving report: {e}")
            return result

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> dict:
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

        # Группируем по месяцам и суммируем платежи
        result = filtered.groupby(pd.Grouper(key="Дата операции", freq="M"))["Сумма платежа"].sum()

        # Преобразуем в словарь с строковыми ключами
        return {
            ts.strftime('%Y-%m-%d %H:%M:%S'): float(amount)
            for ts, amount in result.items()
        }

    except Exception as e:
        logging.error(f"Error in spending_by_category: {e}", exc_info=True)
        return {}

if __name__ == "__main__":
    print(report_decorator(filename=None))