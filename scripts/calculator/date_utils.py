import sys
import os
from datetime import date, timedelta, datetime

# Ensure correct import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Manually override the latest Sunday if needed (set to None to disable)
MANUAL_LAST_SUNDAY = None # Set to None to use automatic date calculation

def get_latest_sunday():
    """
    Returnerar senaste söndagen som ett `datetime.date`-objekt.
    Om `MANUAL_LAST_SUNDAY` används, säkerställ att det är rätt typ.
    """
    if isinstance(MANUAL_LAST_SUNDAY, date):
        return MANUAL_LAST_SUNDAY
    elif MANUAL_LAST_SUNDAY is not None:
        raise TypeError(f"❌ `MANUAL_LAST_SUNDAY` har fel typ: {type(MANUAL_LAST_SUNDAY)}. Förväntade datetime.date")
    
    return date.today() - timedelta(days=date.today().weekday() + 1)  # Senaste söndagen automatiskt

def get_latest_full_week():
    """
    Returns start & end dates for:
    - Current Week (Monday-Sunday)
    - Last Week (Monday-Sunday)
    - Last Year (same ISO week, previous year)
    - Year 2023 (same ISO week, 2023)
    """
    
    last_sunday = get_latest_sunday()
    current_week_start = last_sunday - timedelta(days=6)
    current_week_end = last_sunday

    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = current_week_end - timedelta(days=7)

    iso_week = current_week_start.isocalendar()[1]
    last_year = current_week_start.year - 1
    year_2023 = current_week_start.year - 2

    last_year_start = date.fromisocalendar(last_year, iso_week, 1)
    last_year_end = date.fromisocalendar(last_year, iso_week, 7)

    year_2023_start = date.fromisocalendar(year_2023, iso_week, 1)
    year_2023_end = date.fromisocalendar(year_2023, iso_week, 7)

    return {
        "current_week": (current_week_start, current_week_end),
        "last_week": (last_week_start, last_week_end),
        "last_year": (last_year_start, last_year_end),
        "year_2023": (year_2023_start, year_2023_end),
    }

def get_key_dates():
    """
    Returns key date ranges used for reporting:
    - Last Sunday
    - 8 Weeks Back (for rolling reports)
    - Fiscal Start (April 1st)
    - Current Quarter Start
    - Current Month Start
    - Current Year
    """

    last_sunday = get_latest_sunday()
    eight_weeks_back = last_sunday - timedelta(weeks=8)
    fiscal_start = date(last_sunday.year if last_sunday.month >= 4 else last_sunday.year - 1, 4, 1)

    month = last_sunday.month
    quarter_start = (
        date(last_sunday.year - 1, 1, 1) if month in [1, 2, 3]
        else date(last_sunday.year, ((month - 1) // 3) * 3 + 1, 1)
    )

    month_start = date(last_sunday.year, last_sunday.month, 1)

    return {
        "last_sunday": last_sunday,
        "eight_weeks_back": eight_weeks_back,
        "fiscal_start": fiscal_start,
        "quarter_start": quarter_start,
        "month_start": month_start,
        "current_year": last_sunday.year,
    }

def get_ytd_time_periods():
    """
    Returns key date ranges for year-to-date (YTD) calculations:
    - `ytd_current_month`: From the latest April 1st to the last Sunday.
    - `ytd_last_year`: Same range as `ytd_current_month` but for the previous year.
    - `ytd_two_years`: Same range as `ytd_current_month` but for two years ago.
    """

    last_sunday = get_latest_sunday()
    fiscal_start = date(last_sunday.year if last_sunday.month >= 4 else last_sunday.year - 1, 4, 1)

    ytd_current_month_start = fiscal_start
    ytd_current_month_end = last_sunday
    ytd_last_year_start = fiscal_start.replace(year=fiscal_start.year - 1)
    ytd_last_year_end = last_sunday.replace(year=last_sunday.year - 1)
    ytd_two_years_start = fiscal_start.replace(year=fiscal_start.year - 2)
    ytd_two_years_end = last_sunday.replace(year=last_sunday.year - 2)

    return {
        "ytd_current_month": (ytd_current_month_start, ytd_current_month_end),
        "ytd_last_year": (ytd_last_year_start, ytd_last_year_end),
        "ytd_two_years": (ytd_two_years_start, ytd_two_years_end),
    }

def get_last_8_weeks():
    """
    Returnerar:
    - En lista av de senaste 8 veckorna (måndag–söndag).
    - En sammanhängande period från första måndagen till senaste söndagen.
    """
    last_sunday = get_latest_sunday()

    # 🔍 Om `get_latest_sunday()` returnerar en tuple, extrahera senaste söndagen
    if isinstance(last_sunday, tuple):
        print(f"❌ FEL: last_sunday är en tuple: {last_sunday}")
        last_sunday = last_sunday[1]  # Ta endast sista värdet om det är en tuple
    elif not isinstance(last_sunday, date):
        raise TypeError(f"❌ `last_sunday` har fel typ: {type(last_sunday)}. Förväntade datetime.date")

    # Skapa veckoperioder
    last_8_weeks = []
    for i in range(8):
        week_end = last_sunday - timedelta(weeks=i)
        week_start = week_end - timedelta(days=6)
        last_8_weeks.append({"week": 8 - i, "week_start": week_start, "week_end": week_end})

    # Full 8-veckorsperiod
    full_period_start = last_8_weeks[-1]["week_start"]
    full_period_end = last_sunday
    full_8_week_period = {"start": full_period_start, "end": full_period_end}

    return last_8_weeks, full_8_week_period

def get_last_8_weeks_range():
    """
    Returns the first and last date of the last 8 weeks period.
    - The first date is the Monday of the earliest (8th) week.
    - The last date is the latest Sunday (same as get_latest_sunday).
    """
    last_8_weeks, _ = get_last_8_weeks()  # Hämta veckolistan och ignorera full period

    if not isinstance(last_8_weeks, list) or not last_8_weeks:
        raise ValueError("❌ `last_8_weeks` är inte en lista eller är tom.")

    first_date = last_8_weeks[-1].get("week_start")  # Säkerställ att nyckeln finns
    last_date = last_8_weeks[0].get("week_end")  # Senaste söndagen i den senaste veckan

    if first_date is None or last_date is None:
        raise KeyError("❌ `week_start` eller `week_end` saknas i `get_last_8_weeks_range()`.")

    return first_date, last_date


def get_last_8_weeks_last_year():
    """
    Returnerar samma 8-veckorsperiod men för föregående år, justerat för ISO-vecka.
    """
    last_8_weeks, _ = get_last_8_weeks()
    last_8_weeks_last_year = []

    for week in last_8_weeks:
        iso_year, iso_week, _ = week["week_start"].isocalendar()  # Hämta rätt ISO-år och vecka
        last_year = iso_year - 1  # Föregående års samma ISO-vecka

        # Skapa start- och slutdatum för föregående år enligt ISO-standard
        week_start_last_year = date.fromisocalendar(last_year, iso_week, 1)  # Måndag
        week_end_last_year = date.fromisocalendar(last_year, iso_week, 7)    # Söndag

        last_8_weeks_last_year.append({
            "week": week["week"],
            "week_start": week_start_last_year,
            "week_end": week_end_last_year
        })

    full_period_start_last_year = last_8_weeks_last_year[-1]["week_start"]
    full_period_end_last_year = last_8_weeks_last_year[0]["week_end"]
    full_8_week_period_last_year = {"start": full_period_start_last_year, "end": full_period_end_last_year}

    return last_8_weeks_last_year, full_8_week_period_last_year

if __name__ == "__main__":
    last_8_weeks, full_8_week_period = get_last_8_weeks()
    last_8_weeks_last_year, full_8_week_period_last_year = get_last_8_weeks_last_year()

    first_date, last_date = full_8_week_period["start"], full_8_week_period["end"]
