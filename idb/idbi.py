import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from datetime import datetime
from stockutils import get_last_report_date,update_last_report_date
from stockutils import db,print_table
from stockutils import get_target_price_recomm_idbi
import logging
logger = logging.getLogger(__name__)


def get_hidden_inputs(html):
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
            print(f,tag["value"])
          else:
            idata[f] = ""

        idata['__EVENTTARGET']="ctl00$ContentPlaceHolder1$dtpgrGain$ctl02$ctl00"
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
        logger.error (f"IDBI Issue with send Requests: {e}")
        return None




def get_reports(html, olddate):
    reports = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_="gainer_loser_table")
        if not table:
            logger.error("IDBI: Could not find gainer loser table")
            return False, reports

        tbody = table.find('tbody')
        if not tbody:
            logger.error("IDBI:No tbody found")
            return False, reports

        for row in tbody.find_all('tr'):
            rr=False
            tds = row.find_all('td')
            if len(tds) >= 3:
                link = tds[1].find('a')
                if not link:
                    continue

                text = link.get_text(strip=True)
                if "technical pick" in text.lower():
                    continue  # ignore these rows
                if "result review" in text.lower():
                  rr=True
                # Extract company name before ':' (if any)
                company = text.split(":", 1)[0].strip()

                href = link.get('href', '').strip()

                # Convert 3rd TD (date string) to datetime.date
                date_str = tds[2].get_text(strip=True)
                try:
                    mydate = datetime.strptime(date_str, "%d-%b-%Y").date()
                except ValueError:
                    continue  # skip invalid dates

                report = {
                    "Company": company,
                    "link": "https://www.idbidirect.in"+href,
                    "report-date": mydate,
                    "broker":"IDBI Capital",
                    "RR":rr
                }

                # If this date is older than olddate, stop and return True
                if mydate <= olddate:
                    return True, reports
                reports.append(report)
        # Finished all rows without finding older date
        return False, reports

    except Exception as e:
        print(f"An error occurred: {e}")
        return False, reports

def add_target_and_recomm(reps):
    for i in reps:
     i['recommendation']=''
     i['target']=''
     if i["RR"]:
      c,recomm=get_target_price_recomm_idbi(i["link"])
      i['recommendation']=recomm
      i['target']=c
def get_all_reports(oldDate):
    reports=[]
    url = "https://www.idbidirect.in/Researchreports.aspx?Option=investment"
    endof=False
    hidden_input_params=""
    while not endof:
      post_response = send_post_request(url, hidden_input_params)
      html=post_response
      if post_response:
       hidden_input_params=get_hidden_inputs(html)
       endof,reps=get_reports(html,oldDate)
       reports.extend(reps)
    return(reports)
def idbi_main():
   start_date=get_last_report_date("IDBI") 
   reps= get_all_reports(start_date)
   add_target_and_recomm(reps) 
   logger.info("Mail: IDBI Found %s new reports after scrapping",len(reps))
   print_table(reps,logger)
   db.insert_into_database(reps,"idbi")
   if len(reps) >0:
     last_date=reps[0]['report-date']
     update_last_report_date("IDBI",last_date)
