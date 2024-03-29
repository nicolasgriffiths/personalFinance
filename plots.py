import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FixedLocator, AutoMinorLocator
from common import T_SVNGS_STR, I_SVNGS_STR

BOX_STYLE = {"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5}
ROLL_MONTHS = [6, 12]
matplotlib.rcParams["font.family"] = "monospace"


# Tick label size
matplotlib.rc("xtick", labelsize=5)
matplotlib.rc("ytick", labelsize=5)


def get_poly_fit(x_data, y_data, degree) -> pd.DataFrame:
    """Fit a polynomial of the given degree to the data"""
    fit_fn = np.poly1d(np.polyfit(x_data, y_data, degree))
    return fit_fn(x_data)


def plot_total_savings(ax: plt.Axes, x_data, y_data, currency: str) -> None:
    ax.plot_date(x_data, y_data, ".-")
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 1), "--b")
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 2), "--r")
    ax.axhline(0.0, color="k")
    last_year_savings = y_data.iloc[-1] - y_data.iloc[-13]

    ax.text(
        0.7,
        0.2,
        f"{T_SVNGS_STR}: {y_data.iloc[-1]:.2f} {currency}\nYear savings: {last_year_savings:.2f} {currency}",
        transform=ax.transAxes,
        fontsize=7,
        verticalalignment="top",
        bbox=BOX_STYLE,
    )

    ax.set_title(f"{T_SVNGS_STR} ({currency})", fontsize=10)
    ax.xaxis.set_minor_locator(FixedLocator(x_data))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(which="both")
    ax.legend(["Raw", "Linear fit", "Quadratic fit"])


def plot_incremental_savings(ax: plt.Axes, x_data, y_data, currency: str) -> None:
    ax.plot_date(x_data, y_data, ".-")
    for r in ROLL_MONTHS:
        ax.plot_date(
            x_data,
            y_data.rolling(r).mean().shift(-int(r / 2)),
            "-",
            linewidth=1,
        )
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 0), "--b")
    ax.plot_date(x_data, get_poly_fit(x_data, y_data, 1), "--r")
    ax.axhline(0.0, color="k")

    mean = y_data.iloc[1:].mean()
    median = y_data.iloc[1:].median()
    stdev = np.sqrt(y_data.iloc[1:].var())

    ax.text(
        0.5,
        0.25,
        f"μ={mean:.2f} {currency}\nmedian={median:.2f} {currency}\nσ={stdev:.2f} {currency}",
        transform=ax.transAxes,
        fontsize=7,
        verticalalignment="top",
        bbox=BOX_STYLE,
    )

    last_month = y_data.iloc[-1]
    prev_month = y_data.iloc[-2]
    ax.text(
        0.25,
        0.95,
        (
            f"Month savings: {last_month:.2f} {currency}\n"
            f"{last_month-prev_month:.2f} {currency} wrt last month\n"
            f"{last_month-mean:.2f} {currency} wrt mean"
        ),
        transform=ax.transAxes,
        fontsize=7,
        verticalalignment="top",
        bbox=BOX_STYLE,
    )

    ax.set_title(f"{I_SVNGS_STR} ({currency})", fontsize=10)
    ax.xaxis.set_minor_locator(FixedLocator(x_data))
    ax.grid(which="both")
    ax.legend(["Raw"] + [f"Rolling {r} months" for r in ROLL_MONTHS] + ["Mean", "Linear fit"])


def plot_savings_distribution(ax: plt.Axes, x_data, data) -> None:
    total_savings = data[[T_SVNGS_STR]]
    clean_finance_data = data.drop(labels=T_SVNGS_STR, axis=1)
    savings_distribution = clean_finance_data.div(total_savings[T_SVNGS_STR], axis=0)
    ax.stackplot(x_data, savings_distribution.fillna(0).T)
    ax.xaxis_date()

    # Delete NaN and print current distribution
    current_distribution = savings_distribution.iloc[-1].tolist()
    idxs = [i for i, x in enumerate(current_distribution) if math.isnan(x)]
    names = [i for j, i in enumerate(list(savings_distribution)) if j not in idxs]
    current_distribution = [i for j, i in enumerate(current_distribution) if j not in idxs]
    text = "Current Savings Distribution:\n"
    for n, d in zip(names, current_distribution):
        text += f"{d: 6.1%} -> {clean_finance_data[n][-1]: 10.2f} -> {n}\n"
    ax.text(
        0.02,
        0.95,
        text.rstrip(),
        transform=ax.transAxes,
        fontsize=7,
        verticalalignment="top",
        bbox=BOX_STYLE,
    )

    ax.set_title("Savings distribution", fontsize=10)
    ax.legend(tuple(savings_distribution), loc="lower left", fontsize="x-small")
    ax.xaxis.set_minor_locator(FixedLocator(x_data))
    ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base=0.05))
    ax.set_ylim([0, 1])


def plot_data(finance_data: pd.DataFrame, currency: str) -> None:
    dates = matplotlib.dates.date2num(finance_data.index)
    _, (ax1_1, ax1_2) = plt.subplots(2, 1)
    plot_total_savings(ax1_1, dates, finance_data[T_SVNGS_STR], currency)
    plot_incremental_savings(ax1_2, dates, finance_data[I_SVNGS_STR], currency)

    _, (ax2) = plt.subplots(1, 1)
    plot_savings_distribution(ax2, dates, finance_data.drop(labels=I_SVNGS_STR, axis=1))
    plt.show()
