from bs4 import BeautifulSoup
import ast
import json
from datetime import datetime
from collections import Counter
#from stockutils import row_exists_no_comp,insert_into_database
from stockutils import db
from stockutils import check_if_present,normalize_broker_name,print_table,read_first_line,write_first_line
import logging
logger = logging.getLogger(__name__)


recent_table=[]

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

def find_new_reports(start_date):
 new_start_date=start_date
 with open("./bs.txt", "r") as file:
    content = file.read()
 soup = BeautifulSoup(content, 'html.parser')

# Find the table with the specified class
 table = soup.find('table', class_='cmpnydatatable_cmpnydatatable__Cnf6M')
# Extract all rows from the table
 rows = table.find_all('tr') if table else []
 new_start_date=""
 for i in rows :
     c=parse_row(i)
     if c :
        new_start_date=c['report-date']
        break 
 logger.info("BS Report date from first row start_date, %s" ,new_start_date)
 for i in rows:
  c=parse_row(i)
  if c:
      report_date=datetime.strptime(c['report-date'],"%B %d, %Y")
      print(c['report-date'])
      if report_date > start_date:
        recent_table.append(c)
      else:
        break
 return (new_start_date)

def main_bs():
 try:
  start_date_stri=read_first_line("./cntrfiles/bs.txt").strip()
  logger.info ("Mail: BS Searching for reports newer than %s ",start_date_stri)
  start_date= datetime.strptime(start_date_stri,"%B %d, %Y")
  new_start_date=find_new_reports(start_date)
  logger.info("Mail: BS Found %s new reports after scrapping",len(recent_table))
  print_table(recent_table,logger)
  cdets=check_if_present(recent_table)
  logger.info("Mail: BS Found %s reports for adding to db",len(cdets))
  print_table(cdets,logger)
  db.insert_into_database(cdets,"bs")
  write_first_line("./cntrfiles/bs.txt",new_start_date)
 except Exception as e:
  logger.error(f"BS: had issues  {e}")
