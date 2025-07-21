from bs4 import BeautifulSoup
import ast
import json
from datetime import datetime
from collections import Counter
from stockutils import row_exists_no_comp,insert_into_database
from stockutils import check_if_present,normalize_broker_name,print_table
import logging
logger = logging.getLogger(__name__)


recent_table=[]
old_table=[]
new_entries=[]
def parse_row(html_row):
    """
    Parses a given HTML table row to extract Company, broker, URL, and target price.

    Args:
        html_row (str): The HTML string of a table row.

    Returns:
        dict: A dictionary containing the extracted information.
              Returns an empty dictionary if parsing fails.
    """

    data = {}
    try:
        # Extract Company Name
        # The Company name is within an <a> tag inside the first <td>
        Company_tag = html_row.find('td').find('a')
        if Company_tag:
            # Clean up the Company name, removing leading/trailing whitespace and potentially "Healt"
            Company_name = Company_tag.get_text(strip=True)
            data["Company"] = Company_name.strip()
        else:
            data["Company"] = None
        recommendation_tag = html_row.find_all('td')[1]
        if recommendation_tag:
            # Clean up the Company name, removing leading/trailing whitespace and potentially "Healt"
            recommendation = recommendation_tag.get_text(strip=True)
            data["recommendation"] = recommendation
        else:
            data["recommendation"] = None

        # Extract Broker
        # The broker name is in the fourth <td> tag
        broker_tag = html_row.find_all('td')[3]
        if broker_tag:
            data["broker"] = normalize_broker_name(broker_tag.get_text(strip=True))
        else:
            data["broker"] = None
        date_tag = html_row.find_all('td')[4]
        if date_tag:
            date_string=date_tag.get_text(strip=True)
            formatted_date=datetime.strptime(date_string, "%d-%b-%Y").strftime("%B %d, %Y")
            data["report-date"] = formatted_date
        else:
            data["report-date"] = None

        # Extract URL
        # The URL is in the href attribute of the <a> tag within the last <td>
        url_tag = html_row.find_all('td')[-1].find('a')
        if url_tag:
            data["link"] = url_tag.get('href')
        else:
            data["link"] = None

        # Extract Target Price
        # The target price is in the third <td> tag, which has class "span-right"
        target_price_tag = html_row.find_all('td')[2]
        if target_price_tag:
            # Remove currency symbols and commas, then convert to float
            target_price_str = target_price_tag.get_text(strip=True).replace(',', '')
            data["target"] = float(target_price_str)
        else:
            data["target"] = None

    except Exception as e:
        logger.error (f"Error parsing below HTML row: {e}")
        logger.info(html_row)
        return {} # Return empty dict on error

    return data


def is_within_10_days(f, s):
    date_format = "%B %d, %Y"
    f_date = datetime.strptime(f, date_format)
    s_date = datetime.strptime(s, date_format)
    return (f_date - s_date).days < 10

def find_last_10_days_data():
 with open("./bs/bs.txt", "r") as file:
    content = file.read()
 soup = BeautifulSoup(content, 'html.parser')

# Find the table with the specified class
 table = soup.find('table', class_='cmpnydatatable_cmpnydatatable__Cnf6M')
# Extract all rows from the table
 start_date=""
 rows = table.find_all('tr') if table else []
 for i in rows :
     c=parse_row(i)
     if c :
        start_date=c['report-date']
        break 
 logger.info("Report date from first row start_date, %s" ,start_date)
 for i in rows:
  c=parse_row(i)
  if c:
      if is_within_10_days(start_date,c['report-date']):
       recent_table.append(c)
      else:
          logger.info ("Reports less than 10 days old - Recent table\n")
          print_table(recent_table,logger)
          return 

def upload_old_data():
  global old_table
  with open("./bs/data.json", "r") as f:
   old_table = json.load(f)

def save_new_data():
    with open("./bs/data.json", "w") as f:
     json.dump(recent_table, f)

def count_reports_per_date(list_of_dicts):
    date_values = []
    for d in list_of_dicts:
        # Assuming every dictionary indeed has a 'date' key as per the prompt
        if "report-date" in d: # Added a check for robustness, though prompt implies it's always there
            date_values.append(d["report-date"])

    # Use collections.Counter to efficiently count occurrences
    return dict(Counter(date_values))
def find_dates_with_changes():
    old_str=count_reports_per_date(old_table)
    new_str=count_reports_per_date(recent_table)
    logger.info ("new keys")
    u=new_str.keys()
    logger.info (u)
    logger.info("old keys")
    logger.info (old_str.keys())
    new_dates = list(new_str.keys() - old_str.keys())
    logger.info("New dates %s",new_dates)
# Keys in both old and new but with different values
    different_values = [key for key in old_str.keys() & new_str.keys() if old_str[key] != new_str[key]]
    logger.info("Reports with old dates %s ",different_values)
    return (new_dates,different_values)

def find_reports_for_a_date(date,table):
   reports= [x for x in table if x.get("report-date")==date]
   return(reports)

def check_if_report_present_in_list(report,replist):
  keys_to_compare = ["Company", "broker", "target", "report-date","recommendation"]
  for s in replist:
    same=True
    for key in keys_to_compare:
     if s[key] != report[key]:
      same=False
    if same==True:
         return True
  return False

def update_old_dates(changed):
    for i in changed:
     old_reports=find_reports_for_a_date(i,old_table)
     new_reports=find_reports_for_a_date(i,recent_table)
     for s  in new_reports:
        k= check_if_report_present_in_list(s,old_reports)
        if not k:
          new_entries.append(s)
"""def update_db():
 for i in new_entries:
  if row_exists_no_comp("""
def main_bs():
 p=find_last_10_days_data()
 upload_old_data()
 logger.info  ("Old data",old_table)
 new_dates,changed=find_dates_with_changes()

 for i in  new_dates:
  reps=find_reports_for_a_date(i,recent_table)
  new_entries.extend(reps)
 update_old_dates(changed)
 logger.info ("New reports found \n")
 print_table (new_entries,logger)
 with open("./bs/mita.json", "w") as f:
     json.dump(new_entries, f)

 u=check_if_present(new_entries)
 logger.info("Reports to be inserted to DB\n")
 print_table(u,logger)
# insert_into_database(u,"bs")

save_new_data()
