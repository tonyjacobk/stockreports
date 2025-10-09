import requests
import json
from datetime import datetime
import re
from stockutils import read_first_line,write_first_line,db,print_table,check_if_present

import logging
logger = logging.getLogger(__name__)

def parse_company(json_input, cutoff_date):
    try:
        data = json.loads(json_input)
        result = []
        last_time=""
        found=False
        # Check if data contains the expected structure
        if not isinstance(data, dict) or 'Data' not in data or 'Table' not in data['Data']:
            return [],""
        
        for item in data['Data']['Table']:
            # Convert report date to datetime object
            raw_date = item.get('REP_RELEASE_DTM', '')
            if not raw_date:
                continue
            if not found:
                last_time=raw_date
                found=True

            try:
                report_date = datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%S')
                print(report_date,cutoff_date)
                # Exit loop if report date is older than cutoff_date
                if report_date <= cutoff_date:
                    break
                formatted_date = report_date.strftime('%B %-d, %Y')
            except ValueError:
                formatted_date = ""
                continue
            
            # Clean target price to keep only integers and decimal point
            raw_target = str(item.get('TARGET_PRICE', ''))
            cleaned_target = re.sub(r'[^0-9.]', '', raw_target)
            
            company_dict = {
                "Company": item.get('COM_NAME', ''),
                "recommendation": item.get('RATING_TYPE_NM', ''),
                "target": cleaned_target,
                "broker": "ICICI Direct",
                "report-date": formatted_date,
                "link": item.get('REPORT_PDF_LINK', '')
            }
            result.append(company_dict)
            
        return result,last_time
    except (json.JSONDecodeError, KeyError):
        return [],""


def get_icici_reports():
    url = "https://www.icicidirect.com/cdnresearchapi/callresearchapi"
    payload = "{\"apiName\":\"GetInvestingIdeas\",\"inputJson\":\"{\\\"rating\\\" : \\\"1.0\\\", \\\"timeFrame\\\" : \\\"\\\", \\\"pageNo\\\" : \\\"1\\\", \\\"pageSize\\\" : \\\"16\\\"}\"}"
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'Content-Type': 'application/json;charset=UTF-8',
    }
    
    response = requests.post(url, data=payload, headers=headers)
    
    if response.status_code != 200:
        return -1, []
    
    try:
        response_text = response.text
        return 1, response_text
    except Exception:
        return -1, []
def icici_main():
 try:
   last_comp=read_first_line('./cntrfiles/icici.txt').strip()
   print(last_comp)
   logger.info("Mail: ICICI Direct Searching for reports after %s",last_comp)        
   cutoff=datetime.strptime(last_comp ,"%Y-%m-%dT%H:%M:%S")
   ret,val =get_icici_reports()
   if ret==-1:
     logger.Error("Error:Mail Could not read ICICI Direct Page")
     return
   reps,ldate=parse_company(val,cutoff)
   print_table(reps,logger)
   logger.info("Mail: ICICI Direct Found %s new reports after scrapping ",len(reps))
   if len(reps) ==0:
    return 
   cdets=check_if_present(reps)
   logger.info("Mail: ICICI Direct found %s reports for adding to db",len(cdets))
   print_table(cdets,logger)
   db.insert_into_database(cdets,"icd")
   write_first_line("./cntrfiles/icici.txt",ldate)
 except Exception as e:
  logger.error(f"ICICI Direct had issues {e}")
