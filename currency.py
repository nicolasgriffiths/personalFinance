import pandas as pd
from urllib.request import urlopen
from forex_python.converter import CurrencyRates

CURRENCY_STR = 'Currency Symbol'
exchange_rate_cache = {}


def is_internet_available():
    try:
        google_url = 'http://216.58.192.142'
        urlopen(google_url, timeout=1)
        return True
    except:
        print('Internet not available!')
        return False


def get_user_input_rate(origin_cur, target_cur):
    # Check cached values
    if origin_cur in exchange_rate_cache:
        return exchange_rate_cache[origin_cur]
    elif origin_cur == target_cur:
        return 1.0

    # New exchange rate
    print('Type exchange rate -> 1 {} = x {}:'.format(origin_cur, target_cur))
    exchange_rate_cache[origin_cur] = float(input())
    return exchange_rate_cache[origin_cur]


def get_exchange_rates(target_cur, currency_symbols):
    '''Get exchange rate from target currency to account currency'''
    # Decide online or offline information
    if is_internet_available():
        get_rate = CurrencyRates().get_rate
    else:
        get_rate = get_user_input_rate

    # Populate currencies
    for symbol in currency_symbols:
        currency_symbols.at[CURRENCY_STR, symbol] = get_rate(
            currency_symbols.at[CURRENCY_STR, symbol], target_cur)
    return currency_symbols


def adjust_currency(target_currency, finance_data_raw, currency_symbols):
    '''Return finance data in the currency indicated'''
    currency_exchange_rate = get_exchange_rates(
        target_currency, currency_symbols)
    finance_data_eur = pd.DataFrame(currency_exchange_rate.values * finance_data_raw.values,
                                    columns=finance_data_raw.columns, index=finance_data_raw.index)
    return finance_data_eur
