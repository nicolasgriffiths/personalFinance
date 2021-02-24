import argparse
import pandas as pd
from common import NOTES_STR
from currency import adjust_currency, CURRENCY_STR
from plots import plot_data


def clean_data(finance_data_raw, include_pension):
    '''Extract notes and currencies from the raw financial data'''
    notes = finance_data_raw[[NOTES_STR]].drop(CURRENCY_STR, 0)
    currency_symbols = finance_data_raw.loc[[CURRENCY_STR]].drop(NOTES_STR, 1)
    finance_data = finance_data_raw.drop(CURRENCY_STR, 0).drop(NOTES_STR, 1)

    if not include_pension:
        cols_to_drop = []
        for col_name in finance_data.columns:
            if "Pension" in col_name:
                cols_to_drop.append(col_name)
        
        for col_name in cols_to_drop:
            currency_symbols = currency_symbols.drop(col_name, 1)
            finance_data = finance_data.drop(col_name, 1)

    return notes, currency_symbols, finance_data


def compute_savings(finance_data):
    '''Compute total and incremental savings based on clean financial data'''
    finance_data['Total Savings'] = finance_data.sum(axis=1)

    # Incremental savings
    prev = 0
    increments = []
    for row in finance_data['Total Savings']:
        increments.append(row - prev)
        prev = row
    increments[0] = 0
    finance_data['Incremental Savings'] = increments

    return finance_data


def run(args):
    # Load data
    finance_data_raw = pd.read_excel(args.data_path, index_col=0)

    notes, currency_symbols, finance_data = clean_data(finance_data_raw, args.include_pension)
    finance_data = adjust_currency(args.currency, finance_data, currency_symbols)
    finance_data = compute_savings(finance_data)
    plot_data(finance_data, notes, args.currency)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--currency', type=str, default='EUR',
                        help='Target currency in which the results will be displayed')
    parser.add_argument('--data-path', type=str, default='data/data.xlsx',
                        help='Path to formatted xlsx file')
    parser.add_argument('--include-pension', action='store_true', default=False,
                        help='Wether to include columns containing \"Pension\" in the calculations')
    args = parser.parse_args()
    run(args)
