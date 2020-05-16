import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, AutoMinorLocator
from common import T_SVNGS_STR, I_SVNGS_STR

BOX_STYLE = {'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5}
N_MONTHS = 6


# Tick label size
matplotlib.rc('xtick', labelsize=5)
matplotlib.rc('ytick', labelsize=5)


def get_poly_fit(x_data, y_data, degree):
    '''Fit a polynomial of the given degree to the data'''
    fit_fn = np.poly1d(np.polyfit(x_data, y_data, degree))
    return fit_fn(x_data)


def plot_total_savings(ax, x_data, y_data, currency):
    ax.plot_date(x_data, y_data, '.-')
    ax.plot_date(x_data, y_data.rolling(N_MONTHS).mean(), '-', linewidth=1)
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 1), '--b')
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 2), '--r')

    text_latest = T_SVNGS_STR + ': {:.2f} {cur}'.format(
        y_data.iloc[-1], cur=currency)
    ax.text(0.02, 0.95, text_latest, transform=ax.transAxes,
            fontsize=7, verticalalignment='top', bbox=BOX_STYLE)

    ax.set_title(T_SVNGS_STR + ' ({})'.format(currency), fontsize=10)
    ax.xaxis.set_minor_locator(FixedLocator(x_data))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(which='both')
    ax.legend(['Raw',
               f'Rolling {N_MONTHS} months',
               'Linear fit',
               'Quadratic fit'])


def plot_incremental_savings(ax, x_data, y_data, currency):
    ax.plot_date(x_data, y_data, '.-')
    ax.plot_date(x_data, y_data.rolling(N_MONTHS).mean(), '-', linewidth=1)
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 0), '--b')
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 1), '--r')

    mean = y_data.iloc[1:, ].mean()

    text_stats = ('μ={:.2f} {cur}\n'
                  'median={:.2f} {cur}\n'
                  'σ={:.2f} {cur}'
                  .format(mean,
                          y_data.iloc[1:, ].median(),
                          np.sqrt(y_data.iloc[1:, ].var()),
                          cur=currency))
    ax.text(0.02, 0.95, text_stats, transform=ax.transAxes,
            fontsize=7, verticalalignment='top', bbox=BOX_STYLE)

    text_latest = ('Month savings: {:.2f} {cur}\n'
                   '{:.2f} wrt last month\n'
                   '{:.2f} wrt mean'
                   .format(y_data.iloc[-1],
                           y_data.iloc[-1] - y_data.iloc[-2],
                           y_data.iloc[-1] - mean,
                           cur=currency))
    ax.text(0.25, 0.95, text_latest, transform=ax.transAxes,
            fontsize=7, verticalalignment='top', bbox=BOX_STYLE)

    ax.set_title(I_SVNGS_STR + ' ({})'.format(currency), fontsize=10)
    ax.xaxis.set_minor_locator(FixedLocator(x_data))
    ax.grid(which='both')
    ax.legend(['Raw',
               f'Rolling {N_MONTHS} months',
               'Mean',
               'Linear fit'])


def plot_savings_distribution(ax, x_data, data):
    total_savings = data[[T_SVNGS_STR]]
    clean_finance_data = data.drop(T_SVNGS_STR, 1)
    savings_distribution = clean_finance_data.div(
        total_savings[T_SVNGS_STR], axis=0)

    ax.plot_date(x_data, savings_distribution, '.-')

    # Delete NaN and print current distribution
    current_distribution = savings_distribution.iloc[-1].tolist()
    idxs = [i for i, x in enumerate(current_distribution) if math.isnan(x)]
    names = [i for j, i in enumerate(
        list(savings_distribution)) if j not in idxs]
    current_distribution = [i for j, i in enumerate(
        current_distribution) if j not in idxs]
    text = 'Current Savings Distribution:\n'
    for i in range(len(names)):
        text += '{:.2f}% -> {}\n'.format(
            current_distribution[i] * 100, str(names[i]))
    ax.text(0.02, 0.95, text.rstrip(), transform=ax.transAxes,
            fontsize=7, verticalalignment='top', bbox=BOX_STYLE)

    ax.set_title('Savings distribution', fontsize=10)
    ax.legend(tuple(savings_distribution),
              loc='lower left', fontsize='x-small')
    ax.xaxis.set_minor_locator(FixedLocator(x_data))
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base=0.05))
    ax.set_ylim([0, 1])
    ax.grid(which='both')


def plot_data(finance_data, notes, currency):
    dates = matplotlib.dates.date2num(finance_data.index)
    # TODO Add notes to plots
    _fig1, (ax1_1, ax1_2) = plt.subplots(2, 1)
    plot_total_savings(
        ax1_1, dates, finance_data[T_SVNGS_STR], currency)
    plot_incremental_savings(
        ax1_2, dates, finance_data[I_SVNGS_STR], currency)

    _fig2, (ax2) = plt.subplots(1, 1)
    plot_savings_distribution(ax2, dates,
                              finance_data.drop(I_SVNGS_STR, 1))
    plt.show()
