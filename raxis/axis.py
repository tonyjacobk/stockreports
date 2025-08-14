import requests
from bs4 import BeautifulSoup
import re

from datetime import datetime
from typing import List, Dict,Tuple

from stockutils import get_target_price
import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def extract_report_information(rtext, ids=None):
    if ids is None:
        ids = []
        
    results = []
    
    soup = BeautifulSoup(rtext, 'html.parser')
    li_elements = soup.find_all('li', class_='shadow-panel search_ids')
    
    for li in li_elements:
        li_id = li.get('id')
        h5_tag = li.find('h5', class_='pro-name report-proname')
        p_time_tag = li.find('p', class_='reports-time')
        panel_footer = li.find('div', class_='panel-footer')
        a_tag = panel_footer.find('a') if panel_footer else None
        
        # Check required fields
        if not h5_tag or not p_time_tag or not a_tag or not a_tag.get('href'):
            logging.warning(f"Skipping LI (id={li_id}) due to missing required fields.")
            continue
        
        ids.append(li_id) if li_id else logging.warning("LI element has no ID")
        
        company = h5_tag.get('title')
        time = p_time_tag.get_text(strip=True)
        
        div_video_tag = li.find('div', class_='reports-video')
        text = div_video_tag.get_text(strip=True) if div_video_tag else None
        if not text:
            logging.info(f"No video text for company '{company}' (id={li_id})")
        
        href = a_tag.get('href')
        link = f"https://simplehai.axisdirect.in{href}" if href.startswith("/") else href
        
        results.append({
            'Company': company,
            'time': time,
            'text': text,
            'link': link
        })
        logging.info(f"Added report for {company} (id={li_id})")
    
    logging.info(f"Total reports extracted: {len(results)}")
    return results, ids


def get_recommendation(text: str) -> str:
    keywords = ["HOLD", "BUY", "SELL", "NOT RATED", "UNDER REVIEW", "NO STANCE"]
    pattern = r'\b(?:' + '|'.join(map(re.escape, keywords)) + r')\b'
    text_upper = text.upper()
    matches = re.findall(pattern, text_upper)
    print ("From recommendation", text) 
    if len(matches) == 1:
        return matches[0]
    elif len(matches) >= 2:
        # Check for contextual phrases around "to" or "from"
        for i in range(len(matches) - 1):
            a, b = matches[i], matches[i + 1]
            # Extract surrounding phrase and check for known patterns
            phrase = re.search(f'{a}\\s+(to|from)\\s+{b}', text_upper)
            if phrase:
                direction = phrase.group(1)
                return b if direction == "to" else a
        return matches[1]
    else:
        return ""

def extract_target_price(text):
    """
    Extract target price from a string containing patterns like:
    - "target price of Rs 365"
    - "TP of Rs 600"
    
    Args:
        text (str): Input string containing target price information
        
    Returns:
        int/float: Extracted target price, or empty string if not found
    """
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Pattern to match various target price formats
    patterns = [
        r'target\s+price\s+of\s+rs\.?\s*([\d,]+\.?\d*)',  # "target price of Rs 365" or "target price of Rs 3,850"
        r'tp\s+of\s+rs\.?\s*([\d,]+\.?\d*)',              # "TP of Rs 600" or "TP of Rs 3,850"
        r'target\s+price\s*:\s*rs\.?\s*([\d,]+\.?\d*)',   # "target price: Rs 365"
        r'tp\s*:\s*rs\.?\s*([\d,]+\.?\d*)',               # "TP: Rs 600"
        r'target\s*-\s*rs\.?\s*([\d,]+\.?\d*)',           # "target - Rs 365"
        r'tp\s*-\s*rs\.?\s*([\d,]+\.?\d*)',               # "TP - Rs 600"
        r'tp\s+of\s+([\d,]+\.?\d*)',                     # "TP of 385" or "TP of 3,850"
        r'target\s+price\s+of\s+([\d,]+\.?\d*)',         # "target price of 385" or "target price of 3,850"
    ] 
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            price = match.group(1)
            # Return as integer if it's a whole number, otherwise as float
            return price
    
    return ""




def transform_data( lastdate,A1: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], bool] :
    B1 = []
    lastfound=False
    prefix_map = ('Result Update:', 'Axis Punch:', 'Company Update:', 'Pick of the Week:','Axis Annual Analysis','Initiating Coverage')
    target_map= ( 'Axis Punch:','Pick of the Week:','Axis Annual Analysis','Initiating Coverage','Company Update')
    for A in A1:
        company_raw = A.get("Company", "").strip()
        if company_raw.startswith("Daily Fundamental View"):
            continue

        B = {}
        # Report Date
        report_date_obj = datetime.strptime(A["time"], "%d %b %Y" )
        if report_date_obj> lastdate:
         B["report-date"] = report_date_obj.strftime("%B %d, %Y")
         B["broker"] = "Axis Securities"
         B["link"] = A.get("link", "")
         B["target"]=" " 
         # Company Name and Recommendation
         if any(company_raw.startswith(prefix) for prefix in prefix_map):
            for prefix in prefix_map:
                if company_raw.startswith(prefix):
                    print ("here")
                    B["Company"] = company_raw.split(":", 1)[-1].strip()
                    break
            B["recommendation"] = get_recommendation(A.get("text", ""))
         else:
            B["Company"] = company_raw
            B["recommendation"] = ""
         if any(company_raw.startswith(prefix) for prefix in target_map):
            B["target"]=extract_target_price(A.get("text",""))
         if company_raw.startswith("Result Update:"):
             print ("Result Update")
             B["target"]=get_target_price(B["link"])
        else:
            lastfound=True
            break
        B1.append(B)
      
    return B1,lastfound





