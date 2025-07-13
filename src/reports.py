from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar

import pandas as pd

T = TypeVar("T")

logger = logging.getLogger(__name__)


def report_to_file(filename: Optional[str] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Декоратор для сохранения результатов отчета в файл."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result = func(*args, **kwargs)

            # Создаем имя файла
            report_name = filename or f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Создаем директорию reports если ее нет
            reports_dir = Path(__file__).parent.parent / "reports"
            reports_dir.mkdir(exist_ok=True)

            # Полный путь к файлу
            report_path = reports_dir / report_name

            # Сохраняем результат
            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    if isinstance(result, pd.DataFrame):
                        # Преобразуем даты в строки перед сохранением
                        df = result.copy()
                        if "Дата операции" in df.columns:
                            df["Дата операции"] = df["Дата операции"].astype(str)
                        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
                    else:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info(f"Отчет сохранен в {report_path}")
            except Exception as e:
                logger.error(f"Ошибка сохранения отчета: {str(e)}")

            return result

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Рассчитывает траты по категории за последние 3 месяца."""
    try:
        ref_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
        start_date = ref_date - timedelta(days=90)

        filtered = transactions[
            (transactions["Категория"] == category)
            & (pd.to_datetime(transactions["Дата операции"]) >= start_date)
            & (pd.to_datetime(transactions["Дата операции"]) <= ref_date)
        ]

        return (
            filtered.groupby(pd.to_datetime(filtered["Дата операции"]).dt.to_period("M"))["Сумма операции"]
            .sum()
            .reset_index()
        )
    except Exception as e:
        logger.error("Ошибка в spending_by_category: %s", str(e))
        raise


@report_to_file()
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Рассчитывает средние траты по дням недели за последние 3 месяца."""
    try:
        ref_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
        start_date = ref_date - timedelta(days=90)

        filtered = transactions.loc[
            (pd.to_datetime(transactions["Дата операции"]) >= start_date)
            & (pd.to_datetime(transactions["Дата операции"]) <= ref_date)
        ].copy()

        filtered.loc[:, "День недели"] = pd.to_datetime(filtered["Дата операции"]).dt.day_name()
        return filtered.groupby("День недели")["Сумма операции"].mean().reset_index()
    except Exception as e:
        logger.error("Ошибка в spending_by_weekday: %s", str(e))
        raise


@report_to_file("workday_spending_report.json")
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Рассчитывает средние траты в рабочие и выходные дни за последние 3 месяца."""
    try:
        ref_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
        start_date = ref_date - timedelta(days=90)

        filtered = transactions.loc[
            (pd.to_datetime(transactions["Дата операции"]) >= start_date)
            & (pd.to_datetime(transactions["Дата операции"]) <= ref_date)
        ].copy()

        filtered.loc[:, "Тип дня"] = pd.to_datetime(filtered["Дата операции"]).dt.dayofweek.apply(
            lambda x: "Выходной" if x >= 5 else "Рабочий"
        )

        return filtered.groupby("Тип дня")["Сумма операции"].mean().reset_index()
    except Exception as e:
        logger.error("Ошибка в spending_by_workday: %s", str(e))
        raise
