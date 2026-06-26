from datetime import datetime
from datetime import date,time
from dateutil.relativedelta import relativedelta
from .scrape    import parse_mncl_main
import logging
logger = logging.getLogger(__name__)

def get_url_list(itoday, lastday):
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
            current_date += relativedelta(months=1)
            
    return urls


def monarch_main(lastday):
 reps=[]
 itoday = datetime.combine(datetime.now().date(), time.min)
 urls=get_url_list(itoday,lastday)
 for i in urls:
  logger.info("Trying URL %s",i)
  mnth=i.replace('https://www.mnclgroup.com/research-reports?sector=&companyname=&abtcmpny=',"").replace('+', " ")
  replist=parse_mncl_main(i,mnth)
  reps.extend(replist)
 return reps,[],itoday.date()
