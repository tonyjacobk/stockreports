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



# Function to parse the title
def parse_recommendation(title):
    try:
        parts=title.split(';')
        recommendation = title.split()[0]
        if len(parts) ==1:
            company= title.split(":")[0].split(" ", 1)[1].strip()
        else:
             company = title.split(";")[0].split(" ", 1)[1].strip()
        target_match = re.search(r"target of Rs (\d+)", title)
        target = int(target_match.group(1)) if target_match else None
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
url = "https://www.moneycontrol.com/news/tags/recommendations.html"

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
def scrape_money_control(saved_time):
 headers = {"User-Agent": "Mozilla/5.0"}
 response = requests.get(url, headers=headers)

# List to hold all results
 results = []

 if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all elements with id starting with 'newslist-'
    elements = soup.find_all(id=re.compile("^newslist-"))

    # For the first element: extract published-time
    if elements:
        first_elem = elements[0]
        published_time=find_published_time(first_elem)
        write_first_line("./cntrfiles/mcontrol.txt",published_time)
    # Process each element
    for elem in elements:
        # Find the first <p>
        pub_time=find_published_time(elem)
        if not is_published_newer(saved_time,pub_time):
            break
        p_tag = elem.find("p")
        rep_date = None
        if p_tag:
            text = p_tag.get_text(strip=True)
            match = re.search(r"research report dated\s*(.+)", text, re.IGNORECASE)
            if match:
                rep_date = match.group(1).strip()

        # Find the first <a>
        link_tag = elem.find("a")
        href = link_tag['href'] if link_tag and link_tag.has_attr('href') else None
        if 'moneycontrol-research' in href:
            logger.info("Mail:MC Research %s ",text)
            continue
        title = link_tag['title'] if link_tag and link_tag.has_attr('title') else None
        rurl=get_real_url(href)
        tjson = parse_recommendation(title) if title else {}
        sjson = {
            "link": rurl,
            "report-date": rep_date
        }

        # Merge dictionaries
        combined = {**tjson, **sjson}
        results.append(combined)
 else:
    logger.error("Failed to fetch page. Status: %s", response.status_code)

# Print all JSONs
 logger.info ("MC: After Scrapping  %s \n",json.dumps(results, indent=2))
 return results

def main_mc():
 try:
  start_date=read_first_line("./cntrfiles/mcontrol.txt").strip()
  logger.info ("Mail: MC Searching for reports newer than %s ",start_date)
  dets=scrape_money_control(start_date)
  logger.info("Mail: MC Found %s new reports after scrapping",len(dets))
  cdets=check_if_present(dets)
  logger.info  ("Mail: MC Found %s reports for adding to db",len(cdets))
  print_table(cdets,logger)
  db.insert_into_database(cdets,"mc")
 except Exception as e:
  logger.error(f"MC had issues {e}")
