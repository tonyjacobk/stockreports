from datetime import datetime
from datetime import date,time
from dateutil.relativedelta import relativedelta
import logging
logger = logging.getLogger(__name__)

month_mapping = {
        "January": [],
        "February": [],
        "March": [],
        "April": [],
        "May": [],
        "June": [],
        "July": [],
        "August": [],
        "September": [],
        "October": [],
        "November": [],
        "December": []
    }

def get_abbr(month):
    return (month_mapping[month])

def get_date_object(date_string1):
  date_string=date_string1.strip()

  reverse_mapping = {}
  for full_month, abbreviations in month_mapping.items():
    for abbr in abbreviations:
       reverse_mapping[abbr] = full_month

    # Split the string
  parts = date_string.strip().split()
  if len(parts) != 2:
      return None
  month_part, year_part = parts[0], parts[1]
  try:
        dt = datetime.strptime(date_string, "%B %Y")
        return dt.date()
  except ValueError:
        pass
    # Try parsing with "%b %Y" (abbreviated month name)
  try:
        dt = datetime.strptime(date_string, "%b %Y")
        return dt.date()
  except ValueError:
        pass
  if month_part in reverse_mapping:
        full_month = reverse_mapping[month_part]
        try:
            dt = datetime.strptime(f"{full_month} {year_part}", "%B %Y")
            return dt.date()
        except ValueError:
            pass
    
  return None

