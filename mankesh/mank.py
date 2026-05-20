import requests
from bs4 import BeautifulSoup
import re
import datetime

import requests
from bs4 import BeautifulSoup
from .manpdf import get_recomm_target
def get_vc_nonce():
    url = "https://www.mangalkeshav.com/research-reports/company-reports/fundamental/"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    # Find element having data-vc-public-nonce
    element = soup.find(attrs={"data-vc-public-nonce": True})

    if element:
        return element["data-vc-public-nonce"]
    return None


def fetch_reports( nonce):
    url = "https://www.mangalkeshav.com/research-reports/wp-admin/admin-ajax.php"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


    data = {
        "action": "vc_get_vc_grid_data",
        "vc_action": "vc_get_vc_grid_data",
        "tag": "vc_masonry_grid",
        "data[visible_pages]": "5",
        "data[page_id]": "5116",
        "data[action]": "vc_get_vc_grid_data",
        "data[shortcode_id]": "1751913951475-8a7f0ba8-2c07-5",
        "data[items_per_page]": "12",
        "data[btn_data][i_icon_monosocial]": "vc_li vc_li-heart",
        "data[tag]": "vc_masonry_grid",
        "vc_post_id": "5116",
        "_vcnonce":nonce
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.text  # or response.json() if JSON
    else:
        print(f"Failed with status code {response.status_code}")
        return None

def clean_text(text: str) -> str:
    # List of phrases to remove (case-insensitive)
    phrases = [
        "Research Report",
        "Initiating Coverage",
        "short research report",  # keeping typo as given
        "IC",
        "Fundamental Analysis Report"
    ]
    pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, phrases)) + r')\b', re.IGNORECASE)
    text = pattern.sub("", text)

    # Remove non-alphanumeric characters (keep spaces)
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)

    # Normalize spaces
    return re.sub(r'\s+', ' ', text).strip()
def get_pdf_from_url(url: str) -> str | None:

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    main_content = soup.find(id="main-content")

    if not main_content:
        print("No element with id='main-content' found.")
        return None

    first_a = main_content.find("a", href=True)

    if not first_a:
        print("No <a> tag found under main-content.")
        return None
    href=first_a["href"]  

    print(href)
    return href

def get_reports(result,lastUrl):
 reps=[]   
 soup = BeautifulSoup(result, "html.parser")
 target_divs = soup.find_all("div", class_="vc_gitem-zone vc_gitem-zone-a vc_gitem-is-link")
 tp=recomm=''
 lurl=None
 for div in target_divs:
        a_tag = div.find("a")
        if a_tag:
            href = a_tag.get("href").strip()
            if not lurl:
             lurl=href
            if href.strip() == lastUrl:
                break
            title = clean_text(a_tag.get("title"))
            real_url=get_pdf_from_url(href)
            if real_url:
                href=real_url
                tp,recomm=get_recomm_target(href)
            row={'link':href,"Company":title, "broker":"Mangal Keshav","site":"mankesh","report-date":datetime.datetime.now().date(),'recommendation':recomm,'target':tp}
            reps.append(row)
 return reps,lurl  
def mankesh_main(lasturl):
    nonce=get_vc_nonce()
    print ("Nonce is ",nonce)
    lurl=lasturl
    result = fetch_reports(nonce)
    if result:
      reps,lurl=get_reports(result,lasturl.strip())
    print(reps)
    return reps,[],lurl

#c,b,i=mankesh_main('https://www.mangalkeshav.com/research-reports/bajaj-finance-limited-fundamental-analysis-report-stock-price-pe-ratio-valuation/')
#print(i)
