import requests
import urllib.parse
import json
import re
from urllib.parse import urlparse,parse_qs
import logging
logger = logging.getLogger(__name__)

myURL="https://smifs.com/api/result-updates?pagination%5Bpage%5D=1&pagination%5BpageSize%5D=6&sort=publish_date%3Adesc&populate=*"
last_scrape_tool=0
timOut=6

def write_to_file(report_list,fname):
  with open(fname, "w") as file:
   for item in report_list:
        file.write(f"{item}\n")

def write_json_to_file(data,fname):
 json_string = json.dumps(data, indent=4)
 with open(fname, "w", encoding="utf-8") as file:
    file.write(json_string)
def read_json(fname):
 try:
  with open(fname, "r", encoding="utf-8") as file:
    data = json.load(file) 
  return data
 except Exception as e:
    logger.error("Could not find file %s",fname)
    return None 

def get_api_info(url):
 parsed = urlparse(url)
 api_path = parsed.path.split("/api/", 1)[1]
 params = parse_qs(parsed.query)
 page = params.get("pagination[page]", [None])[0]
 return api_path, page


def find_tool(fName):
    obj=read_json(fName)
    print(obj)
    if not obj:
        return None
    if "success" in obj and "data" in obj:
        return "fire_crawl"

    if "meta" in obj and "data" in obj:
        return "scrape_do"

    if "config" in obj and "context" in obj and "result" in obj:
        return "scrape_fly"

    if "results" in obj and 'content' in obj["results"][0] and "data" in obj["results"][0]['content']:
        return "decodo"
       
    return None 

def make_request(messType,url,headers,payload,fName):
 print("in make_request",messType,url,headers,payload,fName)
 retval=None
 try:
    if messType=="post": 
      response = requests.post(url, json=payload,headers=headers,timeout= timOut)
      print(response.text,"Response")
    else:
      print(url,payload,"from make_req")
      response =requests.get(url,params=payload,timeout=timOut)
      print(response.text,"Response")
    response.raise_for_status()
    if response.status_code==204 or not response.content:
     logger.error("Empty response %s",url)    
    retval= response.json()

 except requests.exceptions.HTTPError as http_err:
    # Captures 4xx/5xx status codes
    logger.error(f"HTTP error occurred: {http_err} (Status: {response.status_code})")
    return None
 except requests.exceptions.ConnectionError as conn_err:
    # Captures DNS failures, refused connections
    logger.error(f"Connection error occurred: {conn_err}")
    return None
 except requests.exceptions.Timeout as timeout_err:
    # Captures requests that exceeded the timeout duration
    logger.error(f"Timeout error occurred: {timeout_err}")
    return None
 except requests.exceptions.RequestException as req_err:
    # Ambiguous exception catch-all for the requests library
    logger.error(f"An error occurred: {req_err}")
    return None
 try:
   write_json_to_file(retval,fName)
 except Exception as e:
   logger.error("Writing to file fName failed")
 return retval

def scrape_do(getUrl,fName):
 print("Hi Here")
 token = "6b3c2837d0f641f7aa93a3eeb331765e272e285d98b"
 targetUrl = urllib.parse.quote(getUrl)
 url = "http://api.scrape.do/?token={}&url={}".format(token, targetUrl)
 print("Scrape_do URL",url)
 retval=make_request("get",url,None,None,fName)
 return retval


def fire_crawl(myURL,fname):
    print("In fire crwawl")
    api_url = "https://api.firecrawl.dev/v2/scrape"

    headers = {
        "Authorization": "Bearer fc-e11e9da53afe400aa9c0e334101b788a",
        "Content-Type": "application/json"
    }

    data = {
        "url": myURL,
        "onlyMainContent": True,
        "maxAge": 172800000,
        "parsers": ["pdf"],
        "formats": ["markdown", "html"]
    }
    print("Here I am")
    retval=make_request("post",api_url,headers,data,fname)
    return retval

def scrapefly(myURL,fName):
    url = "https://api.scrapfly.io/scrape"
    params = {
        "key": "scp-live-77c6a38ac2ea439e91e22f8f2d66ab93",
        "url": myURL,
        "render_js": "true",
        "asp": "true"
    }

   # response = requests.get(url, params=params)
    response=make_request("get",url,None,params,fName)
    return response

def decodo(myURL,fName):

 url = "https://scraper-api.decodo.com/v2/scrape"

 payload = {
      "url": myURL,
      "proxy_pool": "standard",
}

 headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Basic VTAwMDA0OTA5ODA6UFdfMTZhNDNlYWI0YWM3MzBiNDE5ZDMzMjRmZTk2ODg2N2Q1"
}
 response=make_request("post",url,headers,payload,fName)
 return response

def process_scrap_do(data):
    return data["data"]

def process_fire_crawl(json_content):
  if not json_content['success']:
      return None
  mkdown=json_content['data']['markdown']
  match = re.search(r"```json\s*(.*?)\s*```", mkdown, re.DOTALL)
  if not match:
      return None
  json_string = match.group(1)
  try:
        # 3. Convert the extracted string into a Python dictionary
        json_object = json.loads(json_string)['data']
        return(json_object)

  except json.JSONDecodeError as e:
        print(f"Extracted text was found, but it is not valid JSON. Error: {e}")
        return None

def process_scrape_fly(json_content):
 try: 
     json_report=json.loads(json_content['result']['content']) 
     reps=json_report['data']
     
 except Exception as e:
      print("Could not convert to Json")
      reps=None
 return reps 

def process_decodo(json_content):
 print("In process_decodo")
 reps=None
 try:
     json_report=json.loads(json_content['results'][0]['content'])
     reps=json_report['data']
 except Exception as e:
        print("Could not convert to Json")
 return reps

def get_reports(myURL,fetchNeeded):
 print("In get_reports",fetchNeeded,myURL)
 global last_scrape_tool
 tools_dir={"fire_crawl":process_fire_crawl,"scrape_do":process_scrap_do,"scrape_fly":process_scrape_fly,"decodo":process_decodo}
 urltype,page=get_api_info(myURL)
 fname=urltype+str(page)+".txt"
 print(fname)
 if fetchNeeded:
  print("Fetching reports from ",myURL)
  print(page,urltype)
  tools=[scrape_do,fire_crawl,decodo,scrapefly]
  tool_loop=1
  while tool_loop<5:
   curr_tool=tools[last_scrape_tool]
   print ("Using the tool ",curr_tool)
   last_scrape_tool=(last_scrape_tool+1)%4
   logger.info("Fetching %s to %s using %s",myURL,fname,curr_tool.__name__)
   resp=curr_tool(myURL,fname) 
   if not resp:
       tool_loop=tool_loop+1
   else:
       break
 tool=find_tool(fname)
 if not tool:
     return None
 json_obj=read_json(fname)
 if not json_obj:
  print("Could not read ",fname)
  return None
 process_func=tools_dir[tool]
 logger.info("Reading file %s using tool %s",fname,tool)
 print(process_func)
 rep_list=process_func(json_obj)
 return rep_list


