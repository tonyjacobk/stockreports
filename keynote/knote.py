import requests
from bs4 import BeautifulSoup
from datetime import datetime, date

def keynote_main(cutoff_date: date):
    url = "https://keynotecapitals.com/reports/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"id": "tablepress-12"})
    if not table:
        return []

    results = []

    rows = table.find_all("tr")

    for row in rows:
        date_td = row.find("td", class_="column-1")
        company_td = row.find("td", class_="column-2")
        link_td = row.find("td", class_="column-3")

        if not (date_td and company_td and link_td):
            continue

        # Convert date string to datetime.date
        date_str = date_td.get_text(strip=True)

        try:
            report_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
            continue  # skip invalid formats

        # Stop if older than cutoff
        if report_date < cutoff_date:
            break

        company = company_td.get_text(strip=True)

        a_tag = link_td.find("a")
        link = a_tag["href"] if a_tag and a_tag.has_attr("href") else None

        results.append({
            "report-date": report_date,
            "link": link,
            "Company": company,
            "broker": "Keynote Capital",
            "site":"keynote"
        })
    last_date=cutoff_date
    if len(results) >1:
        last_date=results[0]['report-date']
    return results,[],last_date


# Test function
def test_fetch_reports():
    cutoff = date(2026, 1, 1)
    reports = keynote_main(cutoff)

    for r in reports:
        print(r)

