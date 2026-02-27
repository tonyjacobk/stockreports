import requests
import json
from datetime import datetime, date
from typing import List, Dict, Tuple, Any
import re
# Define the base URL
BASE_URL = "https://www.hdfcsec.com/api/cmsapi/GetNonCallResearch"

def get_a_page(pageNo: int, lastdate: datetime) -> Tuple[bool, List[Dict[str, Any]]]:
    params = {
        "schemeId": "",
        "compCode": "",
        "bucketId": "1913",
        "pageNo": pageNo,
        "pageSize": "10",
        "fromDate": "",
        "toDate": ""
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API call: {e}")
        return False, [] # Return False and an empty list on failure

    # 2. Convert the data to JSON
    try:
        jdata = response.json()
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
        return False, [] # Return False and an empty list on failure
        
    # Check if the expected keys/structure exist to prevent IndexError
    jdata=json.loads(jdata)
    if not (isinstance(jdata, list) and len(jdata) >= 3 and 
            'data' in jdata[0] and 'data' in jdata[2] and 
            isinstance(jdata[2]['data'], list) and len(jdata[2]['data']) >= 13):
        print("Response structure is unexpected.")
        return False, []
    
    reports_list: List[Dict[str, Any]] = []
    
    # 3. and 4. Loop from 0 to 9 (10 iterations)
    for i in range(10):
        # The structure is defined by the prompt:
        # i is used for jdata[0]['data'][i]['PUBLISHED_ON']
        # start is used in jdata[2]['data'][start+X]
        start = i*4 # Here, i and start are the same for this logic block
        
        try:
            # 4. Extract and Convert the Report Date
            # The format is '21-11-2025 22:08:00' -> %d-%m-%Y %H:%M:%S
            published_on_str = jdata[0]['data'][i]['PUBLISHED_ON']
            
            # Convert the full datetime string to a datetime object, then to a date object
            # dtObject will be of type datetime.date
            dt_object_full: datetime = datetime.strptime(published_on_str, '%d-%m-%Y %H:%M:%S')
            dt_object_date: date = dt_object_full.date()
            
            # Extract Link (jdata[2]['data'][start+3]['OBJECT1'])
            # Note: The indices (start+3) and (start+2) are based *strictly* on the user's request.
            # start runs from 0 to 9. The indices accessed are 3 through 12.
            link_value = jdata[2]['data'][start+3]['OBJECT1']
            
            # Extract Company (jdata[2]['data'][start+2]['OBJECT1'])
            company_value = jdata[2]['data'][start+2]['OBJECT1']

            # 5. Check the Date and Filter
            # If the report date (dt_object_date) is NOT older than lastdate.date()
            # We compare the date parts for consistency.
            if dt_object_date >= lastdate:
                # Report is recent enough: Create dictionary and add to the list
                reports_list.append({
                    "link": link_value,
                    "Company": company_value,
                    "report-date": dt_object_date.strftime("%B %d, %Y"), # Use a standard string format for output
                    "broker":"HDFC Securities"
                })
            else:
                # 6. Report IS older than lastdate: Return True (stop flag) and the list
                return True, reports_list

        except (KeyError, ValueError, IndexError) as e:
            print(f"Error processing item at index {i}: {e}. Skipping this item.")
            continue # Skip to the next item in the loop if data is missing or malformed

    # 7. End of Loop: Return False and the list created
    return False, reports_list

def getreports(lastdate: datetime) -> List[Dict[str, Any]]:

    all_reports: List[Dict[str, Any]] = []
    pageNo = 1

    # Loop indefinitely until explicitly stopped
    while True:
        # Call the helper function
        stop_flag, page_reports = get_a_page(pageNo, lastdate)

        # Append the reports from the current page
        all_reports.extend(page_reports)

        # Check the stop flag
        if stop_flag:
            # The stop flag is True if get_a_page found an old report
            # or hit a critical error/empty response.
            break

        # If no stop signal, increment the page number and continue
        pageNo += 1

        # Add a safeguard to prevent infinite loops in case of unexpected API behavior
        if pageNo > 100:
            print("Reached page limit safeguard (100 pages). Stopping.")
            break

    print("-" * 50)
    print(f"*** Search complete. Total pages checked: {pageNo - 1} ***")
    return all_reports

def clean_reports(final_reports: List[Dict[str, Any]]) -> None:
    
    # Define the companies/reports to exclude
    EXCLUSION_SUBSTRINGS = {"Bharat Barometer", "HSIE Results Daily"}
    
    for i in range(len(final_reports) - 1, -1, -1):
        report = final_reports[i]
        company_name = report.get('Company', '') # Safely get the Company value
        is_excluded = False
        for exclusion in EXCLUSION_SUBSTRINGS:
            # Check if the exclusion string is part of the company name (case-sensitive)
            if exclusion in company_name:
                is_excluded = True
                break
        
        if is_excluded:
            final_reports.pop(i)

        tcom = company_name.split(':')[0].strip()

        tcom = re.sub(r'\s*\([^)]*\)\s*', '', tcom).strip()
        
        report['Company'] = tcom
        report["link"]="https://www.hdfcsec.com/hsl.docs//"+report["link"]

def hdfc_main(LAST_DATE_CUTOFF):
  final_reports = getreports(LAST_DATE_CUTOFF)
  print("Reports from HDFC",len(final_reports))
  last_date=LAST_DATE_CUTOFF
  if  len(final_reports) > 1:
      last_date=datetime.strptime(final_reports[0]["report-date"],"%B %d, %Y")
  clean_reports(final_reports)
  print("After cleaning", len(final_reports))
  return final_reports,[],last_date
