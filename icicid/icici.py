import requests
from bs4 import BeautifulSoup
import re
from stockutils import get_data_and_recomm_icicid,read_first_line,write_first_line,db,print_table,check_if_present

import logging
logger = logging.getLogger(__name__)

def fetch_icici_equity_data(lastName):
    url = "https://www.icicidirect.com/research/equity"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    l1 = []
    firstName = ""

    investing_ideas = soup.find(id="InvestingIdeas")
    if not investing_ideas:
        return l1, firstName

    p = investing_ideas.find("div", class_="slider researchSlider positional-slider")
    if not p:
        return l1, firstName

    boxes = p.find_all("div", class_="box")

    for box in boxes:
        # Step 1: Extract title from <a>
        a_tag = box.find("a")
        title = a_tag.get("title") if a_tag else ""
        if not firstName:
            firstName = title
        if title == lastName:
            return l1, firstName

        # Step 2: Extract target price
        label = box.find("label", string="Target Price")
        h5 = label.find_next("h5") if label else None
        target_raw = h5.text.strip() if h5 else ""
        target = re.sub(r"[^\d.]", "", target_raw)

        # Step 3: Extract link from box-footer
        box_footer = box.find("div", class_="box-footer")
        one_div = box_footer.find("div") if box_footer else None
        a_footer = one_div.find("a") if one_div else None
        URL = a_footer.get("href") if a_footer else ""

        # Step 4: Create dictionary
        data = {
            "Company": title,
            "recommendation": "",
            "target": target,
            "broker": "ICICI Direct",
            "report-date": "",
            "link": URL
        }

        # Step 5: Append to list
        l1.append(data)

    return l1, firstName
def get_date_and_recomm(reps):
 for i in reps:
    print("Trying ....",i)
    c=get_data_and_recomm_icicid(i["link"])
    i["report-date"]=c["date"]
    i["recommendation"]=c["recommendation"]
def fill_missing_report_dates_with_first_valid(data_list):
    if not data_list:
        return data_list

    # Find the first valid date
    first_valid_date = None
    first_valid_index = -1
    for i, d in enumerate(data_list):
        if d.get('report-date') not in (None, ""):
            first_valid_date = d.get('report-date')
            first_valid_index = i
            break

    # If a valid date was found, fill all preceding empty dates with it
    if first_valid_date:
        for i in range(first_valid_index):
            data_list[i]['report-date'] = first_valid_date

    # Now, use the existing logic to fill subsequent dates
    for j in range(1, len(data_list)):
        if data_list[j].get('report-date') in (None, ""):
            data_list[j]['report-date'] = data_list[j-1].get('report-date')

    return data_list


def icici_main():
 try:   
  last_comp=read_first_line('./cntrfiles/icici.txt').strip()
  print(last_comp)
  logger.info("Mail: ICICI Direct Searching for reports after %s",last_comp)
  reps,first=fetch_icici_equity_data(last_comp)
  logger.info("Mail: ICICI Direct Found %s reports after scrapping ",len(reps))
  get_date_and_recomm(reps)
  print_table(reps,logger)
#  updated_list = fill_missing_report_dates_with_first_valid(reps)
#  print(updated_list)
#  cdets=check_if_present(updated_list)
#  logger.info("Mail: ICICI Direct Found %s reports for adding to DB",len(cdets))
#  print_table(cdets,logger)
#  db.insert_into_database(cdets,"icd")
  print("First is  ",first)
  write_first_line("./cntrfiles/icici.txt",first)
 except Exception as e:
  logger.error(f"ICICI Direct had issues {e}")




