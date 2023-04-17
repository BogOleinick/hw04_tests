import datetime as dt


def year(request):
    year_now = dt.date.today().year
    return {
        'year': year_now,
    }
