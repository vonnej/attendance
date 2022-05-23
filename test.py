import calendar
from calendar import HTMLCalendar

import datetime

today = datetime.date.today()

curr_year = today.year
curr_month = today.month
curr_week = today.weekday()


html_calendar = HTMLCalendar(calendar.SUNDAY)
s = html_calendar.formatmonth(curr_year, curr_month)
print(s)