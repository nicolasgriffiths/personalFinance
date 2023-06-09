import datetime
from typing import Dict, Optional
from functools import lru_cache

from currency_converter import CurrencyConverter, ECB_URL
from forex_python.converter import CurrencyRates
import pandas as pd

from common import CURRENCY_STR, singleton

EXCHANGE_RATE_CACHE: Dict[str, float] = {}

class CurrencyRatesSingleton(CurrencyRates):
    pass

@singleton
class CurrencyConverterSingleton(CurrencyConverter):
    def __init__(self):
        super().__init__(currency_file=ECB_URL)


def get_user_input_rate(origin_cur: str, target_cur: str) -> Dict[str, float]:
    """Get currency exchange rate via user input on keyboard"""
    # Check cached values
    if origin_cur in EXCHANGE_RATE_CACHE:
        return EXCHANGE_RATE_CACHE[origin_cur]
    elif origin_cur == target_cur:
        return 1.0

    # New exchange rate
    print(f"Type exchange rate -> 1 {origin_cur} = x {target_cur}:")
    EXCHANGE_RATE_CACHE[origin_cur] = float(input())
    return EXCHANGE_RATE_CACHE[origin_cur]

@lru_cache(maxsize=None)
def get_rate(origin_cur: str, target_cur: str, date=None) -> Optional[float]:
    """Try to get exchange rate with two provders, fall back to user input rate if both fail"""
    try:
        rate = CurrencyConverterSingleton().convert(1.0, origin_cur, target_cur, date)
    except:
        print("WARNING: currency_converter failed, attempting with forex_python")
        try:
            rate = CurrencyRatesSingleton().get_rate(origin_cur, target_cur, date)
        except:
            print("WARNING: forex_python failed")
            return None
    print(f"1 {origin_cur} = {rate:.3f} {target_cur} -- date:{date.date()}")
    return float(rate)  # sometimes it returns a string apparently?

@lru_cache(maxsize=None)
def now() -> datetime.datetime:
    return datetime.datetime.now()

def get_exchange_rates(target_cur: str, currency_symbols: pd.DataFrame) -> pd.DataFrame:
    """Get exchange rate from target currency to account currency"""

    def get_rate_inner(c_str: str) -> float:
        # Handle stock columns
        multiplier = 1.0 if ":" not in c_str else float(c_str.split(":")[-1])
        for i in range(10):
            day = now() - (datetime.timedelta(hours=6) * (2**i))
            maybe_rate = get_rate(c_str.split(":")[0], target_cur, day) 
            if maybe_rate is not None:
                return maybe_rate * multiplier
        print("WARNING: All automatic currency conversion failed, attempting manually")
        return get_user_input_rate(c_str, target_cur)

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
