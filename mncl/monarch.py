from datetime import datetime
from datetime import date,time
from dateutil.relativedelta import relativedelta
from .scrape    import parse_mncl_main
import logging
from . import months
logger = logging.getLogger(__name__)

def get_url_listy(itoday, lastday):
    # Ensure inputs are datetime objects
    # Assuming input format is datetime.date or datetime.datetime
    
    urls = []
    base_url = "https://www.mnclgroup.com/research-reports?sector=&companyname=&abtcmpny={}"
    
    # Check if month and year are the same
    if itoday.month == lastday.month and itoday.year == lastday.year:
        # Format: Month+YYYY (e.g., May+2026)
        formatted_date = itoday.strftime("%B+%Y")
        urls.append(base_url.format(formatted_date))
    else:
        # Create a URL for every month between lastday and itoday
        current_date = lastday
        while current_date <= itoday:
            formatted_date = current_date.strftime("%B+%Y")
            urls.append(base_url.format(formatted_date))
            # Increment by one month
            print("about to add")
            current_date += relativedelta(months=1)
            print("affed")
    return urls

def get_url_list(itoday, lastday):
    urls = []
    base_url = "https://www.mnclgroup.com/research-reports?sector=&companyname=&abtcmpny={}"

    current_date = lastday
    while current_date <= itoday:
      full_month = current_date.strftime("%B")
      short_month= current_date.strftime("%b")
      year = current_date.strftime("%Y")
            
      urls.append(base_url.format(f"{full_month}+{year}"))
      urls.append(base_url.format(f"{short_month}+{year}"))
           # Add URLs with all possible abbreviations for this month
      for abbr in months.get_abbr(full_month):
                urls.append(base_url.format(f"{abbr}+{year}"))
            
            # Increment by one month
      current_date += relativedelta(months=1)
    
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    return unique_urls

def monarch_main(lastday):
 reps=[]
 itoday=datetime.now().date()
 print(itoday)
 urls=get_url_list(itoday,lastday)
 for i in urls:
  logger.info("Trying URL %s",i)
  #extracting month part from URL like 'Aug 2025'
  mnth=i.replace('https://www.mnclgroup.com/research-reports?sector=&companyname=&abtcmpny=',"").replace('+', " ")
  replist=parse_mncl_main(i,mnth)
  reps.extend(replist)
 return reps,[],itoday

