"""In charge of doing currency conversions via multiple python libraries"""

import datetime
from typing import Dict

from currency_converter import CurrencyConverter, ECB_URL
from forex_python.converter import CurrencyRates
import pandas as pd

from common import CURRENCY_STR

EXCHANGE_RATE_CACHE: Dict[str, float] = {}

CURRENCY_RATE = CurrencyRates()
CURRENCY_CONVERTER = None  # Set lazily if forex_python fails


def get_user_input_rate(origin_cur: str, target_cur: str, date=None) -> Dict[str, float]:
    """Get currency exchange rate via user input on keyboard"""
    del date
    # Check cached values
    if origin_cur in EXCHANGE_RATE_CACHE:
        return EXCHANGE_RATE_CACHE[origin_cur]
    elif origin_cur == target_cur:
        return 1.0

    # New exchange rate
    print(f"Type exchange rate -> 1 {origin_cur} = x {target_cur}:")
    EXCHANGE_RATE_CACHE[origin_cur] = float(input())
    return EXCHANGE_RATE_CACHE[origin_cur]


def get_rate(origin_cur: str, target_cur: str, date=None) -> float:
    """Try to get exchange rate with two provders, fall back to user input rate if both fail"""
    try:
        rate = CURRENCY_RATE.get_rate(origin_cur, target_cur, date)
    except:  # pylint: disable=bare-except
        try:
            print("WARNING: forex_python failed, attempting with currency_converter")
            global CURRENCY_CONVERTER  # pylint: disable=global-statement
            if CURRENCY_CONVERTER is None:
                CURRENCY_CONVERTER = CurrencyConverter(currency_file=ECB_URL)
            rate = CURRENCY_CONVERTER.convert(1.0, origin_cur, target_cur, date)
        except:  # pylint: disable=bare-except
            print("WARNING: currency_converter also failed, attempting manually")
            rate = get_user_input_rate(origin_cur, target_cur, date)
    print(f"1 {origin_cur} = {rate:.3f} {target_cur}")
    return float(rate)  # sometimes it returns a string apparently?


def get_exchange_rates(target_cur: str, currency_symbols: pd.DataFrame) -> pd.DataFrame:
    """Get exchange rate from target currency to account currency"""

    def get_rate_inner(c_str: str) -> float:
        # Handle stock columns
        multiplier = 1.0 if ":" not in c_str else float(c_str.split(":")[-1])
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        return get_rate(c_str.split(":")[0], target_cur, yesterday) * multiplier

    # Populate currencies
    for symbol in currency_symbols:
        currency_symbols.at[CURRENCY_STR, symbol] = get_rate_inner(currency_symbols.at[CURRENCY_STR, symbol])

    return currency_symbols


def adjust_currency(
    target_currency: str, finance_data_raw: pd.DataFrame, currency_symbols: pd.DataFrame
) -> pd.DataFrame:
    """Return finance data in the currency indicated"""
    currency_exchange_rate = get_exchange_rates(target_currency, currency_symbols)
    finance_data_eur = pd.DataFrame(
        currency_exchange_rate.values * finance_data_raw.values,
        columns=finance_data_raw.columns,
        index=finance_data_raw.index,
    )
    return finance_data_eur
