import requests
from bs4 import BeautifulSoup
from datetime import datetime,timedelta

def read_data():
    """
    Reads the Sharekhan reports page and returns the BeautifulSoup object.
    """
    url = "https://research.sharekhan.com/research-reports/fundamental/stock-update"
    response = requests.get(url)
    response.raise_for_status()  # Ensure request was successful
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

def get_reports(soup, last_date):
    """
    Extracts report data from the table with class 'sortable table'.
    Stops when a report date is older than last_date.
    
    Parameters:
        soup (BeautifulSoup): Parsed HTML from read_data()
        last_date (datetime): Cutoff date; rows older than this stop processing.
    
    Returns:
        list of dicts: Each dict contains Company, link_text, rep_date, type
    """
    reports = []
    table = soup.find("table", {"class": "reports-table desktop-table"})
    if not table:
        print("Table not found!")
        return reports
    
    tbody = table.find("tbody")
    for row in tbody.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 3:
            continue
        
        # First <td>: Company name (inside <strong>) and link-text (second <li>)
        company_tag = cols[0].find("strong")
        company = company_tag.get_text(strip=True) if company_tag else None
        
        link_text = None
        li_tags = cols[0].find_all("li")
        if len(li_tags) >= 2:
            second_li = li_tags[1]
            a_tag = second_li.find("a")
            if a_tag and a_tag.has_attr("href"):
                link_text = a_tag["href"]
        
        # Second <td>: Report date
        date_str = cols[1].get_text(strip=True)
        try:
            rep_date = datetime.strptime(date_str, "%b %d, %Y").date()
        except ValueError:
            rep_date = None
        
        # Break loop if rep_date is older than last_date
        if rep_date and rep_date < last_date:
            break
        
        # Third <td>: Type
        report_type = cols[2].get_text(strip=True)
        
        reports.append({
            "Company": company,
            "link": link_text,
            "report-date": rep_date,
            "type": report_type,
            "broker":"Mirae Asset Sharekhan",
            "site":"shkhan"
        })
    
    return reports


def classify_reports(reports):
    stocks = []
    sector = []
    
    for report in reports:
        # Make a shallow copy so we can safely modify
        r = dict(report)
        report_type = r.pop("type", None)
        
        if report_type in ("Stock Update", "Viewpoint"):
            stocks.append(r)
        else:
            r['company']=r['Company']
            r.pop("Company",None)
            sector.append(r)
    
    return stocks, sector

def shkhan_main(start_date):
 print(start_date)
 k=read_data()
 reps=get_reports(k,start_date)
 stks,sect=classify_reports(reps)
 last_date=start_date
 if len(reps) > 1:
     last_date=reps[0]['report-date']
 return stks,sect,last_date

"""
today = datetime.now().date()

# Subtract one day using a timedelta
yesterday = today - timedelta(days=1)
a,b,c=shkhan_main(yesterday)
print(a)
print(b)
"""
