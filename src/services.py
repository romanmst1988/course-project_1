from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def profitable_cashback_categories(transactions: List[Dict[str, Any]], year: int, month: int) -> Dict[str, float]:
    """Рассчитывает наиболее выгодные категории кешбэка за указанный месяц и год.

    Args:
        transactions: Список транзакций
        year: Год для анализа
        month: Месяц для анализа (1-12)

    Returns:
        Словарь с категориями и суммарным кешбэком

    Raises:
        ValueError: При некорректных параметрах года или месяца
    """
    if not (1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12")
    if year < 2000 or year > datetime.now().year:
        raise ValueError("Invalid year")

    cashback_by_category: Dict[str, float] = {}

    for transaction in transactions:
        try:
            op_date = datetime.strptime(transaction["Дата операции"], "%Y-%m-%d")
            if op_date.year == year and op_date.month == month:
                category = transaction["Категория"]
                cashback = float(transaction.get("Кешбэк", 0))

                if cashback > 0:
                    cashback_by_category[category] = cashback_by_category.get(category, 0.0) + cashback

        except (KeyError, ValueError) as e:
            logger.warning("Пропущена некорректная транзакция: %s", e)
            continue

    return cashback_by_category


def investment_bank(month: str, transactions: List[Dict[str, Any]], rounding_limit: int) -> float:
    """Рассчитывает сбережения от округления транзакций до указанного лимита.

    Args:
        month: Месяц для анализа (формат YYYY-MM)
        transactions: Список транзакций
        rounding_limit: Лимит округления

    Returns:
        Сумма сбережений

    Raises:
        ValueError: При некорректных параметрах
    """
    try:
        year, month_num = map(int, month.split("-"))
        if not (1 <= month_num <= 12):
            raise ValueError("Month must be between 1 and 12")
        if rounding_limit <= 0:
            raise ValueError("Rounding limit must be positive")
    except ValueError as e:
        raise ValueError(f"Invalid month format: {e}") from e

    total_savings = 0.0

    for transaction in transactions:
        try:
            op_date = datetime.strptime(transaction["Дата операции"], "%Y-%m-%d")
            if op_date.year == year and op_date.month == month_num:
                amount = float(transaction["Сумма операции"])
                if amount > 0:  # Округляем только расходы
                    remainder = amount % rounding_limit
                    if remainder > 0:
                        savings = rounding_limit - remainder
                        total_savings += savings

        except (KeyError, ValueError) as e:
            logger.warning("Пропущена некорректная транзакция: %s", e)
            continue

    return round(total_savings, 2)


def simple_search(
    query: str, transactions: List[Dict[str, Any]], case_sensitive: bool = False
) -> List[Dict[str, Any]]:
    """Ищет транзакции по запросу в описании или категории.

    Args:
        query: Строка поиска
        transactions: Список транзакций
        case_sensitive: Учитывать регистр при поиске

    Returns:
        Список найденных транзакций
    """
    if not query:
        return []

    search_query = query if case_sensitive else query.lower()

    results = []
    for transaction in transactions:
        try:
            description = transaction["Описание"]
            category = transaction["Категория"]

            if not case_sensitive:
                description = description.lower()
                category = category.lower()

            if search_query in description or search_query in category:
                results.append(transaction)

        except KeyError as e:
            logger.warning("Пропущена некорректная транзакция: %s", e)
            continue

    return results


def phone_number_search(
    transactions: List[Dict[str, Any]], phone_pattern: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Ищет транзакции с номерами телефонов в описании.

    Args:
        transactions: Список транзакций
        phone_pattern: Опциональный шаблон для поиска номеров

    Returns:
        Список найденных транзакций
    """
    pattern = phone_pattern or r"\+7\s?\d{3}\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}"
    compiled_pattern = re.compile(pattern)

    results = []
    for transaction in transactions:
        try:
            if compiled_pattern.search(transaction["Описание"]):
                results.append(transaction)
        except KeyError as e:
            logger.warning("Пропущена некорректная транзакция: %s", e)
            continue

    return results


def person_transfers_search(
    transactions: List[Dict[str, Any]], name_pattern: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Ищет переводы физическим лицам.

    Args:
        transactions: Список транзакций
        name_pattern: Опциональный шаблон для поиска имен

    Returns:
        Список найденных транзакций
    """
    pattern = name_pattern or r"[А-Я][а-я]+\s[А-Я]\."
    compiled_pattern = re.compile(pattern)

    results = []
    for transaction in transactions:
        try:
            if transaction["Категория"] == "Переводы" and compiled_pattern.search(transaction["Описание"]):
                results.append(transaction)
        except KeyError as e:
            logger.warning("Пропущена некорректная транзакция: %s", e)
            continue

    return results
