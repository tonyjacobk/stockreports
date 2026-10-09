import requests
import json
import contvar
import os
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)

load_dotenv()

url='https://www.business-standard.com/markets/research-report'
username = 'tonyjacobk'
apiKey =os.getenv("key_scrapingbot").strip()

apiUrl = "http://api.scraping-bot.io/scrape/raw-html"
options = {
    "useChrome": True,#set to True if you want to use headless chrome for javascript rendering
    "premiumProxy": False, # set to True if you want to use premium proxies Unblock Amazon,Google,Rakuten
    "proxyCountry": None, # allows you to choose a country proxy (example: proxyCountry:"FR")
    "waitForNetworkRequests":False # wait for most ajax requests to finish until returning the Html content (this option can only be used if useChrome is set to true),
                                   # this can slowdown or fail your scraping if some requests are never ending only use if really needed to get some price loaded asynchronously for example
}

payload = json.dumps({"url":url,"options":options})
headers = {
    'Content-Type': "application/json"
}
def scrape_bs_bot():
 response = requests.request("POST", apiUrl, data=payload, auth=(username,apiKey), headers=headers)
 if response.status_code !=200:
     logger.error("Mail Error BS could not read report site with api.scraping-bot.io ")
     logger.info(response.text)
     return -1
 with open("bs.txt", "w") as file:
    file.write(response.text)
 return 1

def get_text():
 payload = { 'api_key': os.getenv('key_scraperapi').strip(), 'url': 'https://www.business-standard.com/markets/research-report' }
 response = requests.get('https://api.scraperapi.com/', params=payload)
 print("Scraperapi.com is being tried")
 logger.info("Scraperapi.com is being tried")
 if response.status_code !=200:
     logger.error("Mail Error BS could not read report site scraperapi.com")
     logger.info(response.text)
     return -1
 with open("bs.txt", "w") as file:
    file.write(response.text)  # Write the string and add a newline
 return 1

def get_zyte():
 zyte_url="http://"+os.getenv('key_zyte').strip()+":@api.zyte.com:8011/"
 print(zyte_url)
 response = requests.get(
    "https://www.business-standard.com/markets/research-report",
    verify=False,
    proxies={
        scheme: zyte_url for scheme in ("http", "https")
    },
)
 if response.status_code !=200:
     logger.error("Mail Error BS could not read report site zyte.com")
     logger.info(response.text)
     return -1

 http_response_body: bytes = response.content
 c=http_response_body.decode()
 with open("bs.txt", "w") as file:
    file.write(c)  # Write the string and add a newline
 return 1


def scrape_bs():
 if contvar.testrunbs ==1:
   logger.info ("testrunbs=1 , Returning ..")
   return 0
 funcs=[scrape_bs_bot,get_text,get_zyte]
 for func in funcs:
  result=func()
  if result == 1:
     return 1
 logger.error(" Mail Error Could not Scrape BS site ")
 return -1


