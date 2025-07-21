import requests
import json

url='https://www.business-standard.com/markets/research-report'
username = 'tonyjacobk'
apiKey = 'cu6SYxYgWZuDc5hDUnTVWSyER'

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
def scrape_bs():
 response = requests.request("POST", apiUrl, data=payload, auth=(username,apiKey), headers=headers)

 with open("bs.txt", "w") as file:
    file.write(response.text)
