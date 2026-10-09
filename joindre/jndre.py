from datetime import datetime
from urllib.parse import urljoin
import certifi
import urllib3
import requests
from bs4 import BeautifulSoup
import os
import re
from stockutils import generic_target_price, generic_recommendation,get_lines_from_pdfFile
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def get_reports(last_date):
    """
    Parameters
    ----------
    last_date : datetime.date

    Returns
    -------
    list[dict]
        [
            {
                "company": "...",
                "report-date": date(...),
                "link": "https://joindre.com/pdfs/..."
            },
            ...
        ]
    """
    url = "https://joindre.com/Fundamental-Reports?page=1"
    try:
     response = requests.get(
        url,
        verify=False,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30,
    )
    except requests.exceptions.SSLError as e:
     pass
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", id="irtable")
    if not table:
        return []

    reports = []

    # Iterate through rows, skipping header row if present
    for row in table.find_all("tr"):
        tds = row.find_all("td")

        if len(tds) < 4:
            continue

        company = tds[2].get_text(strip=True)

        report_date_str = tds[1].get_text(strip=True)
        print(report_date_str,"Report date")
        report_date = datetime.strptime(
            report_date_str, "%d-%b-%Y"
        ).date()

        # Stop as soon as an older date is encountered
        if report_date < last_date:
            return reports

        a_tag = tds[3].find("a", href=True)
        if not a_tag:
            continue

        link = urljoin("https://joindre.com/pdfs/", a_tag["href"])
        company,target,recomm=get_details(link)
        reports.append({
            "Company": company,
            "report-date": report_date,
            "link": link,
            "recommendation":recomm,
            "target":target,
            "broker":"Joindre"
        })

    return reports
def get_details(link):
  print("link",link)
  text=get_lines_from_pdfFile(link,200)
  company=text[3]
  raw_text=result_flat = " ".join(text)
  recomm=generic_recommendation(raw_text)
  target=generic_target_price(raw_text)
  return company,target,recomm

def jndre_main(last_date):
 reps=get_reports(last_date)
 ldate=last_date
 if len(reps)>0:
    ldate=reps[0]['report-date']
 return reps,[],ldate
