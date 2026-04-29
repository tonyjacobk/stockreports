import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import re
import logging
logger = logging.getLogger(__name__)
from stockutils import print_table

comp_url = "https://barodaetrade.com/research-Details/SSR"
sect_url="https://barodaetrade.com/research-Details/STR"

def bob_page(starting_date,url,issect):
 reports=[]
 response = requests.get(url)
 soup = BeautifulSoup(response.content, "html.parser")


 month_map = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
    "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
    "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
}

 blocks = soup.find_all("div", class_="col-sm-12")
 cnt=0
 for block in blocks:
    # Extract date text
    row={}
    date_tag = block.find(class_="dateNtime1")
    if not date_tag:
        continue

    repdate = date_tag.get_text(strip=True)  # e.g. 13-AUG-20

    try:
        # Convert to datetime.date
        day, mon, yr = repdate.split("-")
        month = month_map[mon.upper()]
        year = int(yr)
        year += 2000 if year < 100 else 0

        rep_date = date(int(year), month, int(day))
        
    except Exception as e:
        logger.error("Date parsing failed for:", repdate)
        continue
    row["report-date"]=rep_date 
    # Stop condition
    if rep_date < starting_date:
        print("Stopping: reached older records ->", rep_date)
        break

    # Extract news heading
    news_tag = block.find(class_="newsheading")
    if not news_tag:
        continue
    reptitle = news_tag.find(text=True, recursive=False).strip()
    print(reptitle)
    if not issect:
       k=process_title(reptitle)
       row=row|k
    else:
        row["company"]=reptitle
    # Extract URL
    a_tag = news_tag.find("a")
    row["link"] = "https://barodaetrade.com/"+a_tag["href"] if a_tag and a_tag.has_attr("href") else None
    row["broker"]="BOB Capital"
    row["site"]="bob"
    reports.append(row)
 last_date=starting_date
 if len(reports) >0:
        last_date=reports[0]['report-date']
 return(reports,last_date)
def process_title(title: str):
    if not isinstance(title, str) or not title.strip():
        return {"Company": None, "recommendation": None}

    # Find recommendation pattern
    pattern = re.search(r'\((BUY|SELL|HOLD|NOT RATED)\)\s*:', title, re.IGNORECASE)

    if not pattern:
        return {"Company": None, "recommendation": None}

    recommendation = pattern.group(1).upper()
    
    # Extract company
    company = title[:pattern.start()].strip()
    company = company.rstrip(" -:|")

    # Check for [Initiation]
    if company.upper().startswith("[INITIATION]"):
        company = company[len("[Initiation]"):].strip()
        company = company.lstrip(" -:|")  # clean leading junk after removal
        recommendation = "INITIATING"

    return {
        "Company": company if company else None,
        "recommendation": recommendation
    }
def bob_main(starting_date):
 comp,lastdate=bob_page(starting_date,comp_url,False)
 print_table(comp,logger)
 sect,sdate=bob_page(starting_date,sect_url,True)
 print_table(sect,logger)
 if sdate > lastdate:
     lastdate=sdate
 
 return (comp,sect,lastdate)
