from datetime import datetime, date
import requests
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger(__name__)


def get_reports(last_date: date):

    url = "https://www.cdresearch.in/research-report.php"

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    if not table:
        return None, []

    reports = []
    latest_report_date = None

    for row in table.find_all("tr"):
        tds = row.find_all("td")

        if len(tds) < 3:
            continue

        company = tds[0].get_text(strip=True)
        report_date_str = tds[1].get_text(strip=True)

        try:
            report_date = datetime.strptime(
                report_date_str,
                "%d/%m/%Y"
            ).date()
        except ValueError:
            logger.error("CD Research issue with date %s",report_date_str)
            continue

        # Save date from first valid row
        if latest_report_date is None:
            latest_report_date = report_date

        link_tag = tds[2].find("a", href=True)
        link = link_tag["href"] if link_tag else None

        if link and not link.startswith("http"):
            link = requests.compat.urljoin(url, link)

        # Table is assumed to be sorted newest->oldest
        if report_date < last_date:
            break

        reports.append({
            "Company": company,
            "report-date": report_date,
            "link": link,
            'recommendation':None,
            'target':None,
            'broker':"CD Research"
        })

    return reports,[],latest_report_date

def cde_main(lastday):
 return ( get_reports(lastday)) 
