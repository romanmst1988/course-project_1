import json
import logging
from datetime import datetime
import pandas as pd
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
import os


def configure_logging():
    """Настройка логирования с ротацией файлов"""
    # Создаем папку для логов
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Полный путь к файлу лога
    log_file = os.path.join(log_dir, '../logs/finance_app.log')

    # Создаем логгер
    logger = logging.getLogger('../logs/finance_app.log')
    logger.setLevel(logging.INFO)

    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Обработчик для записи в файл с ротацией
    try:
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Не удалось настроить файловый логгер: {e}")

    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


@dataclass
class CardStats:
    last_digits: str
    total_spent: float
    cashback: float


@dataclass
class Transaction:
    date: str
    amount: float
    category: str
    description: str


@dataclass
class CurrencyRate:
    currency: str
    rate: Optional[float]


@dataclass
class StockPrice:
    stock: str
    price: Optional[float]


class FinanceDataFetcher:
    """Класс для получения финансовых данных с кэшированием и задержкой"""

    def __init__(self):
        self._cache = {}
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Минимальный интервал между запросами (секунды)

    def _make_request(self, url: str) -> Optional[Dict]:
        """Выполняет запрос с учетом ограничений по частоте"""
        current_time = time.time()
        elapsed = current_time - self._last_request_time

        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            self._last_request_time = time.time()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None

    def get_currency_rate(self, currency: str) -> Optional[float]:
        """Получает курс валюты с кэшированием"""
        cache_key = f"currency_{currency}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Альтернативный API с бесплатным доступом
        url = f"https://api.exchangerate-api.com/v4/latest/{currency}?apikey=a11c748a999c985289f73542"
        data = self._make_request(url)

        if data and 'rates' in data and 'RUB' in data['rates']:
            rate = round(data['rates']['RUB'], 2)
            self._cache[cache_key] = rate
            return rate

        return None

    def get_stock_price(self, symbol: str) -> Optional[float]:
        """Получает цену акции с кэшированием"""
        cache_key = f"stock_{symbol}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Используем более стабильный API
        url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}?apikey=NrRoryan8HPhS27PvjlSqdRMuHvkslSU"
        data = self._make_request(url)

        if data and isinstance(data, list) and len(data) > 0 and 'price' in data[0]:
            price = round(data[0]['price'], 2)
            self._cache[cache_key] = price
            return price

        return None


def get_greeting(time_str: str) -> str:
    """Возвращает приветствие в зависимости от времени суток"""
    try:
        time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").time()
        if 5 <= time_obj.hour < 12:
            return "Доброе утро"
        elif 12 <= time_obj.hour < 18:
            return "Добрый день"
        elif 18 <= time_obj.hour < 23:
            return "Добрый вечер"
        return "Доброй ночи"
    except ValueError as e:
        logging.error(f"Ошибка формата времени: {e}")
        return "Добрый день"


def load_transactions(file_path: str) -> pd.DataFrame:
    """Загружает транзакции из Excel файла"""
    try:
        df = pd.read_excel(
            file_path,
            parse_dates=['Дата операции'],
            date_format='%d.%m.%Y %H:%M:%S'
        )

        # Проверка обязательных столбцов
        required_cols = ['Номер карты', 'Сумма платежа', 'Дата операции']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            raise ValueError(f"Отсутствуют обязательные столбцы: {', '.join(missing_cols)}")

        return df
    except Exception as e:
        logging.error(f"Ошибка загрузки транзакций: {e}")
        raise


def analyze_cards(transactions: pd.DataFrame) -> List[CardStats]:
    """Анализирует статистику по картам"""
    if transactions.empty:
        return []

    try:
        # Создаем копию DataFrame, чтобы избежать предупреждений
        df = transactions.copy()

        # Преобразуем номера карт в строки и извлекаем последние 4 цифры
        df['last_digits'] = df['Номер карты'].astype(str).str.strip().str[-4:]

        # Заменяем пустые значения на '0000'
        df['last_digits'] = df['last_digits'].replace('nan', '0000')

        # Группируем по последним 4 цифрам карты
        grouped = df.groupby('last_digits')

        stats = []
        for card, group in grouped:
            # Проверяем наличие столбца 'Кешбэк'
            cashback = group['Кешбэк'].sum() if 'Кешбэк' in group.columns else 0.0

            stats.append(CardStats(
                last_digits = card,
                total_spent=round(group['Сумма платежа'].sum(), 2),
                cashback=round(float(cashback), 2)
            ))

        return stats
    except Exception as e:
        logging.error(f"Ошибка анализа карт: {e}", exc_info=True)
        return []

def get_top_transactions(transactions: pd.DataFrame, n: int = 5) -> List[Transaction]:
    """Возвращает топ-N транзакций по сумме"""
    if transactions.empty or 'Сумма платежа' not in transactions.columns:
        return []

    try:
        top = transactions.nlargest(n, 'Сумма платежа')
        return [
            Transaction(
                date=row['Дата операции'].strftime('%d.%m.%Y'),
                amount=round(float(row['Сумма платежа']), 2),
                category=str(row.get('Категория', '')),
                description=str(row.get('Описание', ''))
            )
            for _, row in top.iterrows()
        ]
    except Exception as e:
        logging.error(f"Ошибка получения топ транзакций: {e}")
        return []


def load_user_settings(file_path: str = '../user_settings.json') -> Dict:
    """Загружает пользовательские настройки"""
    default_settings = {
        'user_currencies': ['USD', 'EUR'],
        'user_stocks': ['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA']
    }

    try:
        with open(file_path) as f:
            settings = json.load(f)
            # Валидация настроек
            if not all(key in settings for key in ['user_currencies', 'user_stocks']):
                raise ValueError("Неполные настройки")
            return settings
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        logging.warning(f"Используются настройки по умолчанию: {e}")
        return default_settings


def home_page(date_time_str: str) -> Dict[str, Any]:
    """Главная страница с аналитикой"""
    try:
        # Инициализация компонентов
        fetcher = FinanceDataFetcher()

        # Загрузка данных
        transactions = load_transactions("../data/operations.xlsx")
        settings = load_user_settings()

        # Получение курсов валют
        currency_rates = [
            CurrencyRate(currency=curr, rate=fetcher.get_currency_rate(curr))
            for curr in settings['user_currencies']
        ]

        # Получение цен акций
        stock_prices = [
            StockPrice(stock=stock, price=fetcher.get_stock_price(stock))
            for stock in settings['user_stocks']
        ]

        # Формирование ответа
        return {
            'greeting': get_greeting(date_time_str),
            'cards': [card.__dict__ for card in analyze_cards(transactions)],
            'top_transactions': [tx.__dict__ for tx in get_top_transactions(transactions)],
            'currency_rates': [rate.__dict__ for rate in currency_rates],
            'stock_prices': [stock.__dict__ for stock in stock_prices]
        }
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}", exc_info=True)
        return {'error': str(e)}


def process_cards():
    return None

if __name__ == "__main__":
    print(load_user_settings())
    print(configure_logging())
