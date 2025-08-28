import requests
from bs4 import BeautifulSoup
import datetime
from stockutils import read_first_line,write_first_line,get_target_price,get_recomm_and_target
from stockutils import print_table,db
import logging
import urllib.parse
logger = logging.getLogger(__name__)

smifs_results=[]
def get_ic(subsec):
    url = "https://www.smifs.com/static/research.aspx/GetResearchData"
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json; charset=UTF-8",
        "origin": "https://www.smifs.com",
        "priority": "u=1, i",
        "referer": "https://www.smifs.com/static/research.aspx?sec=fundamental&subsec=icr",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    cookies = {
        "ASP.NET_SessionId": "d1yqj5ppqhxjkftiiwedz2ou",
        "_gid": "GA1.2.1849264219.1753418216",
        "_gcl_au": "1.1.1185253032.1753418216",
        "_fbp": "fb.1.1753418216241.523804046682382208",
        "_ga": "GA1.2.1871133570.1753418216",
        "_gat_gtag_UA_185361892_1": "1",
        "_ga_0P3Y57Q6YZ": "GS2.1.s1753418216$o1$g1$t1753421493$j54$l0$h0",
        "_ga_20MSJW6P12": "GS2.1.s1753421277$o2$g1$t1753421493$j54$l0$h0"
    }
    data = {
        "section": "fundamental",
        "subsec": subsec,
        "pageno": "1",
        "pagesize": "12"
    }
    try:
        response = requests.post(url, headers=headers, cookies=cookies, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None

def parse_research_data(lastdate,recomm,subsec):
    # Get the API response
    data = get_ic(subsec)
    if not data:
        logger.error ("No data received from SMIFS API %s",subsec)
        return lastdate

    # Assuming the HTML content is in a key like 'd' in the JSON response
    html_content = data.get('d', '')  # Adjust key if needed

    if not html_content:
       logger.error("No HTML content found in response")
       return lastdate

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all elements with class="col-md-3 col-sm-4"
    columns = soup.find_all('div', class_='col-md-3 col-sm-4')
    if not columns:
       logger.error("No elements with class='col-md-3 col-sm-4' found for %s",subsec)
       return lastdate

    # List to store smifs_results

    # Iterate through each column and extract required information
    found=False
    for col in columns:
        result = {
            "Company": "",
            "target": 0,
            "link": "",
            "report-date": "",
            "recommendation": "",
            "broker": "SMIFS"
        }

        # Find <a> tag and its href
        a_tag = col.find('a')
        if a_tag and a_tag.get('href'):
            result["link"] = a_tag['href']

        # Find <span> tag for report-date
        span_tag = col.find('span')
        if span_tag:
            sdate=span_tag.get_text(strip=True)
            ddate=datetime.datetime.strptime(sdate,"%d-%b-%Y").date()
            if ddate <= lastdate:
                break
            result["report-date"] =ddate.strftime("%B %d, %Y")


        # Find <p> tag and split its text
        p_tag = col.find('p')
        if p_tag:
            p_text = p_tag.get_text(strip=True)
            p_parts = p_text.split('-')
            part=-1 if recomm=="pickmonth" else 0
            if p_parts:
                result["Company"] = p_parts[0].strip()
                # Join remaining parts for recommendation
                result["recommendation"] = recomm
        if subsec in ["icr","result"]:
            print(subsec)
            result["target"], result["recommendation"]=get_recomm_and_target((result["link"]))
        smifs_results.append(result)
        found=True
    nlastdate=lastdate
    if found:
      nlastdate=datetime.datetime.strptime(smifs_results[0]["report-date"],"%B %d, %Y").date()
    return nlastdate
def smifs_main():
   try:  
    logger.info("\nLogging Start ... SMIFS")
    ldate_string=read_first_line("./cntrfiles/smifs.txt").strip()
    oldate=datetime.datetime.strptime(ldate_string, "%B %d, %Y").date()
    logger.info("Mail: SMIFS Checking for reports newer than %s",ldate_string)
    nldate2 = parse_research_data(oldate,"Initiating Coverage","icr")
    logger.info("\nNew reports after checking  Initiating Coverage tab\n")
    logger.info("Mail: SMIFS Found %s new reports after Initiating Coverage",len(smifs_results))
    print_table(smifs_results,logger)
    nldate3 = parse_research_data(oldate,"Pick of Month","pickmonth")
    logger.info("New reports after checking  Pick of Month tab")
    logger.info("Mail: SMIFS Found %s new reports after Pick of Month",len(smifs_results))
    print_table(smifs_results,logger)
    nldate1 = parse_research_data(oldate,"","result")
    logger.info("New reports after checking results tab\n")
    logger.info("Mail: SMIFS Found %s new reports after Results",len(smifs_results))
    print_table(smifs_results,logger)

    latest=max([nldate1,nldate2,nldate3])
    db.insert_into_database(smifs_results,"smifs")
    write_first_line('./cntrfiles/smifs.txt', latest.strftime("%B %d, %Y"))
   except Exception as e:
     logger.error(f"SMIFS issue {e}")
