import requests
from bs4 import BeautifulSoup
from datetime import datetime
from stockutils import read_first_line,write_first_line
from stockutils import print_table,db
import logging 
logger = logging.getLogger(__name__)

reponse=''
reps=[]
def read_page():
    global response
    url = "https://www.shareindia.com/about-us/research"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return -1, response.text
    return 0,response
def get_reports(lastdate,ids,reps):
    found_first=False
    tlastdate=None
    print ("Checking for ",ids,lastdate)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find the div with id "tab-content-long-term-stock"
    long_term_stock_div = soup.find('div', id=ids)

    if not long_term_stock_div:
       logger.error ("Could not find the specified div %s .",ids)
       return -1

    # Iterate over each row div under the specified div
    rows=long_term_stock_div.find_all('div', class_='col-lg-4')
    for row in rows:
        k={"broker":"Share india","target":0,"recommendation":""}
        # Extract <a> tag
        a_tag = row.find('a')
        if a_tag:
         k["link"] = a_tag['href'] 
        else:
          logger.error ("Could not find href under %s  %s",ids,row)
          continue
        # Extract <p> tag
        p_tag = row.find('p')
        if p_tag:
          xdate = p_tag.get_text(strip=True) 
          from_page_date=datetime.strptime(xdate, "%d-%m-%Y")
          if from_page_date <=lastdate:
              break
          else:
              k['report-date']=from_page_date.strftime("%B %d, %Y")
        else: 
          logger.error ("Could not find date under %s %s",ids,row)
          continue
         
        # Extract <h5> tag
        h5_tag = row.find('h5')
        if h5_tag:
         k['Company'] = h5_tag.get_text(strip=True) 
        else:
         logger.error ("Could not find Company under %s %s",ids,row)
         continue
        reps.append(k)
        # Print or store the extracted information
        if not found_first:
            tlastdate=k['report-date']
            found_first=True
    return(tlastdate)
# Call the function
def ishare_main():

 logger.info("Logging Start ... ShareIndia")
 ldate_string=read_first_line("./cntrfiles/shareindia.txt").strip()

 lastdate=datetime.strptime(ldate_string, "%Y-%m-%d")
 nlastdate=lastdate
 print ("Inside ",lastdate)
 read_page()
 for i in ['tab-content-long-term-stock','tab-content-short-term-stock','tab-content-thematic-stocks','tab-content-special-reports']:
  nlast_date=None
  nlast_date=get_reports(lastdate,i,reps)
  logger.info ("after %s ",i)
  logger.info(reps)
  if nlast_date:
    nl=datetime.strptime(nlast_date,"%B %d, %Y")
    nlastdate= nl if nl>nlastdate else nlastdate
 write_first_line('./cntrfiles/shareindia.txt', nlastdate.strftime('%Y-%m-%d')) 
 logger.info("Final list of reports from ShareIndia %s",len(reps))
 print_table(reps,logger)
 db.insert_into_database(reps,"shareindia")
 nlast_string=datetime.strftime(nlastdate,"%Y-%m-%d")
 write_first_line("./cntrfiles/shareindia.txt",nlast_string)
 return (reps)

def share_main():
 try:
   return( ishare_main())
 except Exception as e:
   logger.error ("ShareIndia issue {e}")
  
