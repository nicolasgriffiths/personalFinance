from urllib.request import urlopen
import datetime

NOTES_STR = "Notes"
T_SVNGS_STR = "Total Savings"
I_SVNGS_STR = "Incremental Savings"
CURRENCY_STR = "Currency Symbol"
PENSION_STR = "pension"
STOCK_STR = "stock"


def is_internet_available() -> bool:
    try:
        google_url = "http://216.58.192.142"
        urlopen(google_url, timeout=2)
        return True
    except:
        print("Internet not available!")
        return False


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def get_end_of_month_or_today(d: datetime.datetime) -> datetime.datetime:
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = d.replace(day=28) + datetime.timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    end_of_month = next_month - datetime.timedelta(days=next_month.day)
    if end_of_month > datetime.datetime.now():
        return datetime.datetime.now()
    return end_of_month
