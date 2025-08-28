import requests
from bs4 import BeautifulSoup
from datetime import datetime
import codecs
import logging
from stockutils import print_table
from stockutils import db
from stockutils import get_last_report_date,update_last_report_date

logger = logging.getLogger(__name__)

def decode_unicode_string(encoded_str):
    # Split the string into chunks of 4 characters
    chunks = [encoded_str[i:i+4] for i in range(0, len(encoded_str), 4)]
    # Convert each hex code to its character
    decoded_chars = [chr(int(hex_code[:2], 16)) for hex_code in chunks]
    # Join the characters to form the final string
    return ''.join(decoded_chars)






def find_new_reports(fromdate):
    latest_date=fromdate
    url = 'https://gcc.geojit.net/aspx/ResearchDesk/ShowResearchTips.aspx'
    L = []

    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all elements with id starting with 'tsrcid'
        tsrcid_elements = soup.find_all(id=lambda x: x and x.startswith('tsrcid'))

        # Iterate over each found element
        for element in tsrcid_elements:
            # Find the company name td
            company_td = element.find('td', title='Company name')
            # Find the last update td
            last_update_td = element.find('td', title='Lastupdateon')
            target_td= element.find('td', title='Target Price')
            rating_td= element.find('td', title='Rating')
            if company_td and last_update_td:
                company_name = company_td.find('span', title='Company name').get_text(strip=True)
                last_update_str = last_update_td.get_text(strip=True)
                target=target_td.get_text(strip=True)
                rating=rating_td.get_text(strip=True)
                # Extract the encoded URL from onclick
                onclick = company_td.get('onclick', '')
                if onclick.startswith("openwin('") and onclick.endswith("')"):
                    encoded_url = onclick[len("openwin('"):-2]
                    # Decode the URL (hex encoded)
                    decoded_url=decode_unicode_string(encoded_url)
                # Convert last_update_str to date object
                try:
                    last_update_date = datetime.strptime(last_update_str, "%d-%m-%Y").date()
                except ValueError:
                    continue  # Skip if date format is invalid

                # Add to list if last_update_date is greater than fromdate
                if last_update_date > fromdate:
                  c=  {
            "recommendation": rating,
            "Company": company_name,
            "target": target,
            "broker": "Geojit Financial Services",
            "report-date":last_update_date,
            "link":decoded_url

        }

                  L.append(c)
                  if last_update_date > latest_date:
                      latest_date=last_update_date
    else:
        logger.error(f"Geojit:Failed to retrieve the page. Status code: {response.status_code}")

    return L,latest_date

def geojit_main():
 try:
  start_date=get_last_report_date("geojit") 
  recent_table,new_start_date=find_new_reports(start_date)
  logger.info("Mail: Geojit Found %s new reports after scrapping",len(recent_table))
  print_table(recent_table,logger)
  db.insert_into_database(recent_table,"geojith")
  update_last_report_date("geojit",new_start_date)
 except Exception as e:
  logger.error(f"Geojit: had issues  {e}")


