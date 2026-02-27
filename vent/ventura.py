import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from datetime import date, timedelta,datetime
from .vent_res import vent_res_main
import logging
from stockutils import get_target_and_recomm,print_table,get_last_report_date,check_if_present,db,update_last_report_date
logger = logging.getLogger(__name__)
def scrape_ventura_table(html_content,last_date):
    """
    Parses the raw HTML content, finds the target table, applies filtering rules,
    converts the date, and collects the results into a list of dictionaries.

    Args:
        html_content: The raw HTML content (bytes) returned by fetch_content.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the filtered data.
    """
    target_table_id = "ContentPlaceHolder1_NewsRpt"
    expected_td_prefix = "ContentPlaceHolder1_NewsRpt_"
    date_format = "%d-%b-%y"
    last_date=last_date-timedelta(days=1)
    first_report_date: Union[date, str, None] = None
    # List to store the final structured data
    valid_rows: List[Dict[str, Any]] = []

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the target table by its ID
    table = soup.find('table', id=target_table_id)

    if not table:
        print(f"Error: Could not find table with ID '{target_table_id}'.")
        return valid_rows

    print(f"-> Found table. Extracting and filtering data from rows...")

    # Iterate through all rows (<tr>) in the table body (or the entire table)
    for row in table.find_all('tr'):
        # Find the first <td> in the current row
        first_td = row.find('td')

        if first_td:
            # Check if the <td> has an 'id' attribute that starts with the required prefix
            td_id = first_td.get('id')
            
            if td_id and td_id.startswith(expected_td_prefix):
                # 1. Find ALL <span> elements
                span_tags = first_td.find_all('span')
                
                # Check for required number of spans (at least 3)
                if len(span_tags) < 3:
                    print(f"Skipping row (ID: {td_id}): Expected at least 3 spans, found {len(span_tags)}.")
                    continue

                span1_text = span_tags[0].get_text(strip=True)
                span2_text = span_tags[1].get_text(strip=True)
                span3_text = span_tags[2].get_text(strip=True)
                

                report_date: Optional[date] = None
                try:
                    # Convert '25-Nov-25' to a date object
                    report_date = datetime.strptime(span3_text, date_format).date()
                    if not first_report_date:
                      first_report_date=report_date
                    if report_date < last_date:
                      return valid_rows,first_report_date

                except ValueError as e:
                    print(f"Warning (ID: {td_id}): Failed to parse date '{span3_text}'. Data will be stored as raw string.")
                    report_date = span3_text # Store the raw string if parsing fails
                # Filter 1: Ignore if span1 contains "weekly" or "daily" (case-insensitive)
                if any(word in span1_text.lower() for word in ["weekly", "daily"]):
                    print(f"Skipping row (ID: {td_id}): Span 1 ('{span1_text}') contains 'weekly' or 'daily'.")
                    continue

                # Filter 2: Ignore if span2 contains "IPO" (case-insensitive)
                if "ipo" in span2_text.lower():
                    print(f"Skipping row (ID: {td_id}): Span 2 ('{span2_text}') contains 'IPO'.")
                    continue

                anchor_tag = first_td.find('a')
                href_link = anchor_tag.get('href') if anchor_tag else None

                # --- Create Structured Dictionary (Filters passed) ---
                data_point = {
                    "Company": span1_text,
                    "broker": "Ventura Securities",
                    # Store the date object (or the raw string if parsing failed)
                    "report-date": report_date,
                    "link": href_link
                }
                
                valid_rows.append(data_point)
                print(f"Row ACCEPTED (ID: {td_id}): '{span1_text}' added.")

    print(f"Scraping and filtering complete. Total valid rows collected: {len(valid_rows)}")
    return valid_rows,first_report_date


def send_post_request(url):
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
    params={}
    try:
        response = requests.post(url, data=params,headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error (f"IDBI Issue with send Requests: {e}")
        return None

def add_target_and_recomm(reps):
    for i in reps:
     i['recommendation']=''
     i['target']=''
     recomm,c=get_target_and_recomm(i["link"],2000)
     i['recommendation']=recomm
     i['target']=c
     print(i)
     


def get_all_reports(last_date,url):
    reports=[]
    url = "https://www.ventura1.com/Research/StockIdeaPg.aspx"
    post_response = send_post_request(url)
    html=post_response
    if post_response:
     p=scrape_ventura_table(post_response,last_date)  
     print(p)
     return p
def vent_main(start_date):
   reps=[]
   result_url="https://www.ventura1.com/Research/Recommendation.aspx"
   idea_url="https://www.ventura1.com/Research/StockIdeaPg.aspx"
   reps_idea,last_date_idea= get_all_reports(start_date,idea_url)
   res_reps=vent_res_main(start_date)
   reps.extend(res_reps)
   reps.extend(reps_idea)
   print(reps)
   last_res_date=res_reps[0]['report-date'] if len(res_reps)>0 else start_date
   last_date=max(start_date,last_res_date,last_date_idea)
   return(reps,[],last_date)
