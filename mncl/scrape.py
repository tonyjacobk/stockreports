import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_companies(url):
    companies = []
    
    try:
        # Make the GET request
        response = requests.get(url, timeout=10,verify=False)
        response.raise_for_status()  # Raise error for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main container
        resultshow = soup.find('div', class_='resultshow')
        
        if not resultshow:
           logger.error("Warning: div with class 'resultshow' not found.")
           return companies
        
        # Find all item divs under resultshow
        items = resultshow.find_all('div', class_='item')
        
        for item in items:
            # 1. Get company name from class="job-title"
            job_title_elem = item.find(class_='job-title')
            company = job_title_elem.get_text().strip() if job_title_elem else ""
            
            # 2. Get link from class="report-link"
            report_link_div = item.find(class_='report-link')
            if report_link_div:
                a_tag = report_link_div.find('a')
                if a_tag and a_tag.has_attr('href'):
                    link = a_tag['href'] 
            # 3. Append dictionary to list
            if company or link:  # Only add if we found something
                companies.append({
                    "Company": company,
                    "page2-link": link
                })
                
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching URL %s",url)
        print(f"Error fetching URL: {e}")
    except Exception as e:
        logger.error("Error parsing HTML %s",url)
        print(f"Error parsing HTML: {e}")
    
    return companies



def get_second_page(url, dat):
    try:
        response = requests.get(url, timeout=10,verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        report_list = soup.find(class_='report-list')
        if not report_list:
            print("Warning: 'report-list' class not found.")
            report_list= soup.find(class_='blog-dtxt')
            if not report_list:
             logger.error("Warning Could not find blog-dtxt and report-class %s",url)
             return None
        
        # Parse target date for comparison (Month Year format)
        try:
            target_date = datetime.strptime(dat, "%B %Y").date()
        except ValueError:
            print(f"Error: Target date '{dat}' should be in format like 'May 2026'")
            return None
        
        # Go through each <li> one by one
        for li in report_list.find_all('li'):
            # Get the link
            a_tag = li.find('a')
            furl = a_tag['href'] if a_tag and a_tag.has_attr('href') else ""
            
            # Get the report date text from .year-reports
            year_reports_elem = li.find(class_='year-reports')
            rep_date_text = year_reports_elem.get_text().strip() if year_reports_elem else ""
            
            if not rep_date_text:
                continue
                
            # Parse report date
            try:
                report_date = datetime.strptime(rep_date_text, "%B %Y").date()
            except ValueError:
                logger.error("Check date %s",url)
                continue  # Skip if format doesn't match
            
            # Exact match → return the link
            if rep_date_text == dat:
                return furl
            
            # Report is older than target → stop and return None
            if report_date < target_date:
                return None
                
        # No match found
        return None
            
    except requests.exceptions.RequestException as e:
        logger.error("Error fetching URL %s",url)
        print(f"Error fetching URL: {e}")
    except Exception as e:
        logger.error("Error parsing URL %s",url)
        print(f"Error parsing page: {e}")
    
    return None
def get_date(soup):
    date_elem = soup.find(class_='report-date')
    if not date_elem:
        print("Warning: Element with class='report-date' not found.")
        return None

    # Get and clean the text
    date_text = date_elem.get_text().strip()
    if not date_text:
        return None

    try:
        # Parse format like "25 May 2026" → datetime.date
        parsed_date = datetime.strptime(date_text, "%d %b %Y").date()
        return parsed_date
    except ValueError as e:
        print(f"Error parsing date '{date_text}': {e}")
        return None

def get_url(soup):
    img = soup.find('img', alt='MNCL Report Company Update PDF')
    if not img:
        print("Warning: Image with alt='MNCL Report Company Update PDF' not found.")
        return None
    p_tag = img.find_parent('p')
    if not p_tag:
        # If no direct parent p, try finding closest p
        p_tag = img.find_parent().find_parent('p') if img.find_parent() else None

    if not p_tag:
        print("Warning: Could not find <p> tag above the image.")
        return None

    # Find <a> tag inside the <p> and get href
    a_tag = p_tag.find('a')
    if a_tag and a_tag.has_attr('href'):
        return a_tag['href']
    else:
        print("Warning: No <a> tag with href found inside the <p>.")
        return None
def last_page(url):
    try:
        # Fetch the page
        response = requests.get(url, timeout=10,verify=False)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        url=get_url(soup)
        rep_date=get_date(soup)
        # Find the table
        table = soup.find('table', class_='dcf-table')
        if not table:
            print("Warning: Table with class 'dcf-table' not found.")
            logger.error("Table not available in page %s",url)
            return None, None,None,None

        rating = None
        target_price = None

        # Find all rows in the table
        rows = table.find_all('tr')

        for row in rows:
            th = row.find('th')
            if not th:
                continue

            th_text = th.get_text().strip()

            # Find corresponding td
            td = row.find('td')
            td_text = td.get_text().strip() if td else ""

            # Check for Rating
            if "Rating" in th_text:
                rating = td_text
            # Check for Target Price
            if "Target price" in th_text or "Target Price" in th_text:
                target_price = td_text
                target_price=''.join(char for char in target_price if char.isdigit())
        return rating, target_price,url,rep_date

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        logger.error("Error fetching URL %s",url)
    except Exception as e:
        print(f"Error parsing table: {e}")
        logger.error("Error parsing  URL %s",url)
    return None, None,None,None


# Example usage:
# if

def parse_mncl_main(url,month):
 comps=get_companies(url)
 for comp in comps:
  furl=get_second_page(comp['page2-link'],month)
  comp['furl']=furl
  rateing,target,url,repdate=last_page(furl)
  if not url :
      continue
  comp['recommendation']=rateing
  comp['target']=target
  comp['report-date']=repdate
  comp['link']=url
  comp['broker']='MNCL'
 return comps


if __name__ == "__main__":
     url = "https://www.mnclgroup.com/research-reports?sector=&companyname=&abtcmpny=May+2026"
     url2="https://www.mnclgroup.com/sambhv-steel-tubes"
     comps=parse_mncl_main(url,"May 2026")
  #   comps=get_second_page(url2,"May 2026")
     print(comps)
