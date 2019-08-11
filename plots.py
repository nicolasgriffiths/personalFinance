import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, AutoMinorLocator

# Tick label size
matplotlib.rc('xtick', labelsize=5)
matplotlib.rc('ytick', labelsize=5)


def get_poly_fit(x_data, y_data, degree):
    '''Fit a polynomial of the given degree to the data'''
    fit_fn = np.poly1d(np.polyfit(x_data, y_data, degree))
    return fit_fn(x_data)


def plot_total_savings(ax, x_data, y_data, currency):
    # TODO add stacked bars for each area
    ax.plot_date(x_data, y_data, '.-')
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 1), '--b')
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 2), '--r')

    text_latest = 'Total savings: {:.2f} {cur}'.format(
        y_data.iloc[-1], cur=currency)
    ax.text(0.02, 0.95, text_latest, transform=ax.transAxes,
            fontsize=7, verticalalignment='top',
            bbox={'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5})

    ax.set_title('Total Savings ({})'.format(currency), fontsize=7)
    ax.xaxis.set_minor_locator(FixedLocator(x_data))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(which='both')


def plot_incremental_savings(ax, x_data, y_data, currency):
    ax.plot_date(x_data, y_data, '.-')
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 1), '--r')
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 0), '--b')

    text_stats = ('μ={:.2f} {cur}\n'
                  'median={:.2f} {cur}\n'
                  'σ={:.2f} {cur}'
                  .format(y_data.mean(),
                          y_data.median(),
                          np.sqrt(y_data.var()),
                          cur=currency))
    ax.text(0.02, 0.95, text_stats, transform=ax.transAxes,
            fontsize=7, verticalalignment='top',
            bbox={'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5})

    text_latest = ('Month savings: {:.2f} {cur}\n'
                   '{:.2f} wrt last month\n'
                   '{:.2f} wrt mean'
                   .format(y_data.iloc[-1],
                           y_data.iloc[-1] - y_data.iloc[-2],
                           y_data.iloc[-1] - y_data.mean(),
                           cur=currency))
    ax.text(0.25, 0.95, text_latest, transform=ax.transAxes,
            fontsize=7, verticalalignment='top',
            bbox={'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5})

    ax.set_title('Incremental Savings ({})'.format(currency), fontsize=7)
    ax.xaxis.set_minor_locator(FixedLocator(x_data))
    ax.grid(which='both')


def plot_data(finance_data, notes, currency):
    dates = matplotlib.dates.date2num(finance_data.index)
    # TODO Add notes to plots
    _fig, (ax1, ax2) = plt.subplots(2, 1)
    plot_total_savings(
        ax1, dates, finance_data['Total Savings'], currency)
    plot_incremental_savings(
        ax2, dates, finance_data['Incremental Savings'], currency)
    plt.show()
