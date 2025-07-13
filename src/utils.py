from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, TypedDict

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class CurrencyRate(TypedDict):
    currency: str
    rate: float


class StockPrice(TypedDict):
    stock: str
    price: float


def load_transactions(file_path: str | Path) -> pd.DataFrame:
    """Загружает транзакции из Excel-файла."""
    try:
        path = Path(file_path).resolve()

        if os.getenv("TESTING") != "True" and not path.exists():
            raise FileNotFoundError(f"Файл {path} не найден")

        df = pd.read_excel(path)
        logger.info("Успешно загружены транзакции из %s", path)
        return df
    except Exception as e:
        logger.error("Ошибка загрузки транзакций: %s", str(e))
        raise


def get_greeting(time: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = time.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    if 12 <= hour < 17:
        return "Добрый день"
    if 17 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def get_currency_rates(currencies: List[str]) -> List[CurrencyRate]:
    """Получает текущие курсы валют из API."""
    try:
        if os.getenv("TESTING") == "True":
            return [{"currency": c, "rate": 1.0} for c in currencies]

        api_key = os.getenv("CURRENCY_API_KEY")
        if not api_key:
            logger.error("Не задан API ключ для курсов валют")
            raise ValueError("Не задан API ключ для курсов валют")

        url = f"https://api.exchangerate-api.com/v4/latest/USD?apikey={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        rates = response.json().get("rates", {})

        return [
            {
                "currency": c,
                "rate": float(rates.get(c, 0.0)),
            }
            for c in currencies
        ]
    except Exception as e:
        logger.error("Ошибка получения курсов валют: %s", str(e))
        raise


def get_stock_prices(stocks: List[str]) -> List[StockPrice]:
    """Получает текущие цены акций из API."""
    try:
        if os.getenv("TESTING") == "True":
            return [{"stock": s, "price": 100.0} for s in stocks]

        api_key = os.getenv("STOCK_API_KEY")
        if not api_key:
            logger.error("Не задан API ключ для цен акций")
            raise ValueError("Не задан API ключ для цен акций")

        result: List[StockPrice] = []
        for stock in stocks:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            price_str = data.get("Global Quote", {}).get("05. price", "0.0")
            result.append(
                {
                    "stock": stock,
                    "price": float(price_str),
                }
            )

        return result
    except Exception as e:
        logger.error("Ошибка получения цен акций: %s", str(e))
        raise
