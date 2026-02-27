import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from datetime import datetime,date
from typing import List, Tuple
from stockutils import get_last_report_date,update_last_report_date
from stockutils import db,print_table,add_codes_to_reports
from stockutils import get_target_price_recomm_idbi
import logging
logger = logging.getLogger(__name__)


def get_hidden_inputs(html,pageNo):
    try:
        # Send GET request

        # Parse HTML content
        soup = BeautifulSoup(html, 'html.parser')
        hinputs= ['__EVENTTARGET','__EVENTARGUMENT','__VIEWSTATE','__VIEWSTATEGENERATOR','__VIEWSTATEENCRYPTED','__EVENTVALIDATION']
        idata = {}
        for f in hinputs:
          tag = soup.find("input", {"id": f})
          if tag and tag.has_attr("value"):
            idata[f] = tag["value"]
          else:
            idata[f] = ""
        idata['ctl00$ContentPlaceHolder1$grdreports$ctl13$ddlPageSelector']=pageNo 
        query_string = urlencode(idata)
        return query_string

    except requests.RequestException as e:
        logger.error (f"IDBI : Issue with Hidden inputs : {e}")

        return None


def send_post_request(url, params):
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(url, data=params,headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error (f"Ventura Issue with send Requests: {e}")
        return None




def get_reports(html, last_date):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='ContentPlaceHolder1_grdreports')
    results = []
    is_end=False
    if not table:
        logger.info ("Error Venture Result:Table with id 'ContentPlaceHolder1_grdreports' not found")
        return results

    rows = table.find_all('tr')[1:]  # Skip header row
    for row in rows:
        cells = row.find_all('td')

        if len(cells) < 5:
            continue  # Skip rows that don't have enough cells

        # Extract second td (Company name)
        company_name = cells[1].get_text(strip=True)

        # Extract third td (Date string)
        date_str = cells[2].get_text(strip=True)

        # Convert date string to datetime object (date only, no time)
        try:
            # Parse date string like "17-Nov-25 23:18" or "17-Nov-2025 23:18"
            # Extract just the date part before the space
            date_part = date_str.split()[0]

            # Handle different date formats
            # Try parsing with 2-digit year
            try:
                report_date = datetime.strptime(date_part, '%d-%b-%y')
            except ValueError:
                # Try parsing with 4-digit year
                try:
                    report_date = datetime.strptime(date_part, '%d-%b-%Y')
                except ValueError:
                    print(f"Could not parse date: {date_part}")
                    continue

            # Keep only the date part (remove time)
            report_date = report_date.date()

            # Check if report_date is older than last_date
            # If last_date is datetime, convert to date for comparison
            last_date_date = last_date.date() if isinstance(last_date, datetime) else last_date

            if report_date < last_date_date:
                # Stop processing further rows if date is older than last_date
                is_end=True
                break

        except (ValueError, IndexError) as e:
            print(f"Error parsing date '{date_str}': {e}")
            continue

        # Extract href from the 5th td
        fifth_td = cells[4]
        href = None
        anchor = fifth_td.find('a')

        if anchor and anchor.has_attr('href'):
            href = anchor['href']

        # Create dictionary for this row
        row_dict = {
            "Company": company_name,
            "broker": "Ventura",
            "report-date": report_date,
            "link": href
        }

        # Add to results
        results.append(row_dict)


    return results,is_end
def vent_res_main(oldDate):
    reports=[]
    url = "https://www.ventura1.com/Calltracking/Recommendation/ResultAnalysisRecommendations.aspx"
    endof=False
    hidden_input_params=""
    pgno=0
    while not endof:
      pgno=pgno+1
      post_response = send_post_request(url, hidden_input_params)
      html=post_response
      if post_response:
       hidden_input_params=get_hidden_inputs(html,pgno)
       reps,endof=get_reports(html,oldDate)
       reports.extend(reps)
    return(reports)
