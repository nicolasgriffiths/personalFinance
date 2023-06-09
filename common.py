from urllib.request import urlopen

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