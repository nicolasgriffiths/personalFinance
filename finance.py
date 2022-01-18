import argparse
import pandas as pd
import urllib.request

from common import NOTES_STR, CURRENCY_STR, PENSION_STR, STOCK_STR
from mycurrency import adjust_currency
from plots import plot_data
from typing import Tuple

from common import T_SVNGS_STR, I_SVNGS_STR


def clean_data(
    finance_data_raw: pd.DataFrame, include_pension: bool, include_stock: bool
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Extract notes and currencies from the raw financial data"""
    if not include_pension:
        cols = [c for c in finance_data_raw.columns if PENSION_STR not in c.lower()]
        finance_data_raw = finance_data_raw[cols]

    if not include_stock:
        cols = [c for c in finance_data_raw.columns if STOCK_STR not in c.lower()]
        finance_data_raw = finance_data_raw[cols]

    currency_symbols = finance_data_raw.loc[[CURRENCY_STR]].drop(labels=NOTES_STR, axis=1)
    finance_data = finance_data_raw.drop(labels=CURRENCY_STR, axis=0).drop(labels=NOTES_STR, axis=1)

    return currency_symbols, finance_data


def compute_savings(finance_data: pd.DataFrame) -> pd.DataFrame:
    """Compute total and incremental savings based on clean financial data"""
    finance_data[T_SVNGS_STR] = finance_data.sum(axis=1)
    finance_data[I_SVNGS_STR] = finance_data[T_SVNGS_STR].diff().fillna(0.0)
    return finance_data


def run(args):
    if args.url is not None:
        filename, headers = urllib.request.urlretrieve(args.url)
    else:
        filename = args.data_path

    finance_data_raw = pd.read_excel(filename, index_col=0)
    currency_symbols, finance_data = clean_data(finance_data_raw, args.include_pension, args.include_stock)
    finance_data = adjust_currency(args.currency, finance_data, currency_symbols)
    finance_data = compute_savings(finance_data)
    plot_data(finance_data, args.currency)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--currency",
        type=str,
        default="EUR",
        help="Target currency in which the results will be displayed",
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/data.xlsx",
        help="Path to formatted xlsx file",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="URL to xlsx file. For google sheets, replace `/edit#gid=` in normal URL with `/export?format=xlsx&gid=`",
    )
    parser.add_argument(
        "--include-pension",
        action="store_true",
        default=False,
        help=f'Wether to include columns containing "{PENSION_STR}" in the calculations',
    )
    parser.add_argument(
        "--include-stock",
        action="store_true",
        default=False,
        help=f'Wether to include columns containing "{STOCK_STR}" in the calculations',
    )
    args = parser.parse_args()
    run(args)
