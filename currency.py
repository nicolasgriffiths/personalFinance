import datetime
import pandas as pd
from forex_python.converter import CurrencyRates
from currency_converter import CurrencyConverter

from common import is_internet_available

CURRENCY_STR = "Currency Symbol"
EXCHANGE_RATE_CACHE = {}

CURRENCY_RATE = CurrencyRates()
CURRENCY_CONVERTER = CurrencyConverter(fallback_on_wrong_date=True, fallback_on_missing_rate=True)


def get_user_input_rate(origin_cur, target_cur, date=None):
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


def get_rate(origin_cur, target_cur, date=None):
    """Try to get exchange rate with two provders, fall back to user input rate if both fail"""
    try:
        return CURRENCY_RATE.get_rate(origin_cur, target_cur, date)
    except:
        try:
            print("WARNING: forex_python failed, attempting with currency_converter")
            return CURRENCY_CONVERTER.convert(1.0, origin_cur, target_cur, date)
        except:
            print("WARNING: forex_python failed, attempting manually")
            return get_user_input_rate(origin_cur, target_cur, date)


def get_exchange_rates(target_cur, currency_symbols, force_manual=False):
    """Get exchange rate from target currency to account currency"""

    def get_rate_inner(c_str):
        # Handle stock columns
        multiplier = 1.0 if ":" not in c_str else float(c_str.split(":")[-1])
        return get_rate(c_str.split(":")[0], target_cur, datetime.datetime.now()) * multiplier

    # Populate currencies
    for symbol in currency_symbols:
        currency_symbols.at[CURRENCY_STR, symbol] = get_rate_inner(currency_symbols.at[CURRENCY_STR, symbol])

    return currency_symbols


def adjust_currency(target_currency, finance_data_raw, currency_symbols, force_manual=False):
    """Return finance data in the currency indicated"""
    currency_exchange_rate = get_exchange_rates(target_currency, currency_symbols, force_manual)
    finance_data_eur = pd.DataFrame(
        currency_exchange_rate.values * finance_data_raw.values,
        columns=finance_data_raw.columns,
        index=finance_data_raw.index,
    )
    return finance_data_eur
