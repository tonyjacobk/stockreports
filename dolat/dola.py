import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import logging
from .dolat_helper import get_report_details
logger = logging.getLogger(__name__)
def get_dolat_page_soup(dolurl) -> BeautifulSoup:
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(dolurl, headers=headers, timeout=12)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Mail:Could not read %s",dolurl)
        raise RuntimeError(f"Failed to fetch page: {e}")
        
    soup = BeautifulSoup(response.text, "html.parser")
    return soup




def extract_new_reports(soup: BeautifulSoup, lastdate: datetime) -> list[dict]:
    rows = []
    # Try the requested table first
    table = soup.find("table", id="ctl00_ContentPlaceHolder1_GridView4")
    
    if table:
        # Classic GridView parsing
        for tr in table.find_all("tr")[1:]:  # skip header
            tds = tr.find_all("td")
            if len(tds) >= 3:
                # second <td> → date text
                date_str = tds[1].get_text(strip=True)
                # third <td> → link:
                a_tag = tds[2].find("a")
                link = a_tag["href"] if a_tag else None
                
                if not link:
                    continue
                # Make absolute if relative
                if not link.startswith("http"):
                    link = "https://www.dolatresearch.com/" + link.lstrip("/")
                # Parse date (adjust format if needed)

                try:
                    # Common Indian format: DD/MM/YYYY or DD/MM/YY or with time
                    idate2 = datetime.strptime(date_str.split()[0], "%d/%m/%Y").date()
                except ValueError:
                    try:
                        idate2 = datetime.strptime(date_str, "%d/%m/%Y %H:%M").date()
                    except ValueError:
                        continue  # skip unparsable
                if idate2 > lastdate:
                    rows.append({"report-date": idate2, "link": link,'broker':"Dolat Capital Market"   ,"site":"dolat"})
                else :
                    return rows
        return rows    
    else:
        # FALLBACK: current page structure (text date + link to PDF)
        logger.error("Mail: Table ctl00_ContentPlaceHolder1_GridView4 not found → using fallback parsing")
        
        # Find all <a> tags pointing to PDFs in /Attachment/
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "Attachment" in href and href.lower().endswith(".pdf"):
                # Try to get date from previous text sibling
                prev = a.previous_sibling
                date_str = ""
                if prev and prev.strip():
                    date_str = prev.strip()
                elif a.parent and a.parent.previous_sibling:
                    date_str = a.parent.previous_sibling.strip()
                
                if not date_str:
                    continue
                
                # Clean and parse date (most are DD/MM/YYYY)
                date_match = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', date_str)
                if not date_match:
                    continue
                    
                date_part = date_match.group(0)
                try:
                    idate2 = datetime.strptime(date_part, "%d/%m/%Y").date()
                except ValueError:
                    try:
                        idate2 = datetime.strptime(date_part, "%d/%m/%y").date()
                    except ValueError:
                        continue
                
                # Make absolute link
                link = href if href.startswith("http") else "https://www.dolatresearch.com/" + href.lstrip("/")
                
                if idate2 > lastdate:
                   rows.append({"report-date": idate2, "link": link,'broker':"Dolat Capital Market"   ,"site":"dolat"})

    
    # Optional: sort by date descending (newest first)
    rows.sort(key=lambda x: x["date"], reverse=True)
    
    return rows







 
def get_reports_from_page(id_do,last_checked):
    durl="https://www.dolatresearch.com/report_sector.aspx?id="+str(id_do)
    bf1 = get_dolat_page_soup(durl)
    new_reports = extract_new_reports(bf1, last_checked)
    logger.info("Found %s reports from id %s",len(new_reports),id_do)   
    return(new_reports)
def dolat_main(last_checked):
 last_date=last_checked
 report_list=[]
 pages=[1, 4, 5, 6, 12, 13, 15, 18, 20, 23, 24, 25, 30, 34, 41, 52, 78, 99, 100, 105, 111, 118, 136, 139, 141]
 for i in pages:
   try:   
    reps= get_reports_from_page(i,last_checked)
    logger.info("Total reports with id %s : %s",i,len(reps))
    report_list.extend(reps)
    if len(reps)>1:
      print(reps)
      logger.info("Last report for id %s is on  %s:" ,i ,reps[0]["report-date"])
      if reps[0]["report-date"] > last_date:
       last_date=reps[0]["report-date"]
   except Exception as e:
     logger.error("Mail Issues with id %s %s",i,e)

 get_report_details(report_list)
 print(report_list)
 if len(report_list)>1:
     if report_list[0]["report-date"] > last_date:
         last_date=report_list[0]["report-date"]
 return(report_list,[],last_date)
