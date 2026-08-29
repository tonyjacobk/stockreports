import requests
from bs4 import BeautifulSoup, Comment
import re
import json
from datetime import datetime
import pytz
from .sutils import read_first_line , write_first_line
from stockutils import db,print_table
from stockutils import check_if_present
from .mcontrol_comp import get_real_url
import logging
logger = logging.getLogger(__name__)
last_update=""

from datetime import datetime

def standardize_date(date_str: str) -> str:
    """
    Convert dates like "Jun 01, 2026", "June 1 2026", etc.
    to format: '%B %d, %Y' (e.g., "June 01, 2026")
    """
    # Clean the string
    date_str = date_str.strip().strip('.')
    
    # Try multiple possible formats
    formats = [
        "%b %d, %Y",   # Jun 01, 2026
        "%b %d %Y",    # Jun 01 2026
        "%B %d, %Y",   # June 01, 2026
        "%B %d %Y",    # June 01 2026
        "%b %d,%Y",    # Jun 01,2026 (no space after comma)
        "%B %d,%Y",    # June 01,2026
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%B %d, %Y")
        except ValueError:
            continue
    
    # Fallback: Try with day without leading zero (e.g., "Jun 1, 2026")
    # Replace common variations
    cleaned = date_str.replace(',', ' ').strip()
    parts = cleaned.split()
    
    if len(parts) == 3:
        month, day, year = parts
        # Try parsing with flexible day
        for fmt in ["%b %d %Y", "%B %d %Y"]:
            try:
                dt = datetime.strptime(f"{month} {day} {year}", fmt)
                return dt.strftime("%B %d, %Y")
            except ValueError:
                continue
    
    logger.error("Issue with date %s, using today's date",date_str)
    return datetime.now().strftime("%B %d, %Y")  


def parse_recommendation2(title):
    try:
        parts=title.split(';')
        recommendation = title.split()[0]
        if len(parts) ==1:
            company= title.split(":")[0].split(" ", 1)[1].strip()
        else:
             company = title.split(";")[0].split(" ", 1)[1].strip()
        target_match = re.search(r"target of Rs ([\d,]+(?:\.\d+)?)", title)
        target = float(target_match.group(1).replace(",", "")) if target_match else None
        broker = title.split(":")[-1].strip()
        return {
            "recommendation": recommendation,
            "Company": company,
            "target": target,
            "broker": broker
        }
    except Exception as e:
        logger.error("Error parsing title:", title, "|", e)
        return {}

# URL to fetch
base_url = "https://www.moneycontrol.com/news/tags/recommendations.html"

def parse_recommendation(text):
 pattern = re.compile(
    r'^(?P<recommendation>\w+)\s+'
    r'(?P<company>.+?);?\s*'
    r'target of\s*Rs\s*(?P<target>\d+)\s*:?\s*'
    r'(?P<broker>.+)$',
    re.IGNORECASE
)
 match = pattern.search(text)
 if match:
  company=match.group("company")
  recomm=match.group("recommendation")
  target=match.group("target")
  broker=match.group("broker")
  target=float(target.replace(',',""))
  return {
            "recommendation": recomm,
            "Company": company,
            "target": target,
            "broker": broker
        }
 else:
   return None






def find_published_time(elem):
  published_time=""
  comment = elem.find(string=lambda text: isinstance(text, Comment))
  if comment:
            # Look for <span>...</span> inside comment
            span_match = re.search(r"<span>(.*?)</span>", comment)
            if span_match:
                published_time = span_match.group(1).strip()
            else:
                logger.error("Span element not found .. Not able to find published time")
  else:
      logger.error("Comment element not found .. Not able to find published time")
  return(published_time)



def is_published_newer(saved_date, published_date):
    date_format = "%B %d, %Y %I:%M %p IST"
    ist = pytz.timezone('Asia/Kolkata')

    saved_date_parsed = ist.localize(datetime.strptime(saved_date, date_format))
    published_date_parsed = ist.localize(datetime.strptime(published_date, date_format))
    return published_date_parsed > saved_date_parsed
def scrape_a_table(elements,saved_time,pagecnt):
    global last_update
    print("From scrape_table ",pagecnt)
    # For the first element: extract published-time
    end=False
    results=[]
    if elements:
     if pagecnt==0:
        first_elem = elements[0]
        published_time=find_published_time(first_elem)
        if not published_time:
         logger.error("Could not find published time on first page %s",first_elem)
         return None,None
        last_update=published_time
    # Process each element
    for elem in elements:
       
        # Find the first <p>
        pub_time=find_published_time(elem)
        if not pub_time:
            logger.error("Could not find published time %s",elem)
            continue
        if not is_published_newer(saved_time,pub_time):
            end=True
            break
        p_tag = elem.find("p")
        rep_date = None
        if p_tag:
            text = p_tag.get_text(strip=True)
            match = re.search(r"research report dated\s*(.+)", text, re.IGNORECASE)
            if match:
                rep_date = match.group(1).strip()
                rep_date=standardize_date(rep_date)
        else:
            logger.error("p tag not found %s",elem)
            continue
        # Find the first <a>
        link_tag = elem.find("a")
        if not link_tag:
            logger.error("Link tag could not be found %s",elem)
            continue
        href = link_tag['href'] if link_tag and link_tag.has_attr('href') else None
        if not href:
            logger.error("href tag could not be found %s",elem)
            continue
        if 'moneycontrol-research' in href:
            logger.info("Mail:MC Research %s ",text)
            continue
        h2_tag=elem.find("h2")
        if not h2_tag:
            logger.error("h2 tag could not be found %s",elem)
            continue
        h2text=h2_tag.get_text(strip=True)
        tjson = parse_recommendation(h2text) if h2text else {}
        if not tjson:
            logger.error("Issue with finding recommendation %s",elem)
            continue
        rurl=get_real_url(href)
        sjson = {
            "link": rurl,
            "report-date": rep_date
        }
        combined = {**tjson, **sjson}
        results.append(combined)
    return results,end

def scrape_money_control(saved_time,pagecnt):
 global last_update
 headers = {"User-Agent": "Mozilla/5.0"}
 end=False
 url=base_url
 if pagecnt>0:
     url=base_url+"/page-"+str(pagecnt+1)+"/"
 print("Trying response from ",url)
 response = requests.get(url, headers=headers)


 if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all elements with id starting with 'newslist-'
    elements = soup.find_all(id=re.compile("^newslist-"))
    results,end=scrape_a_table(elements,saved_time,pagecnt)
    logger.info ("MC: After Scrapping page %s  %s \n",pagecnt,json.dumps(results, indent=2))
    return results,end
 else:
    logger.error("Failed to fetch page. Status: %s", response.status_code)
    return None,None


def scrape_all_pages(start_date):
 end=False
 pgcnt=0
 fdets=[]
 while end==False :
  dets,end=scrape_money_control(start_date,pgcnt)
  if not dets :                                     ## second way to ensure no infinite loop 
      return fdets
  fdets.extend(dets)
  pgcnt=pgcnt+1  
 return fdets 
def main_mc():
 try:
  start_date=read_first_line("./cntrfiles/mcontrol.txt").strip()
  logger.info ("Mail: MC Searching for reports newer than %s ",start_date)
  dets=scrape_all_pages(start_date)
  logger.info("Mail: MC Found %s new reports after scrapping",len(dets))
  cdets=check_if_present(dets,"mc")
  print(cdets)
  print("last date is ",last_update)
  write_first_line("./cntrfiles/mcontrol.txt",last_update)
  logger.info  ("Mail: MC Found %s reports for adding to db",len(cdets))
  print_table(cdets,logger)
  db.insert_into_database(cdets,"mc")
 except Exception as e:
  logger.error(f"MC had issues {e}")
