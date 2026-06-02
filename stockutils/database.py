import pymysql
from datetime import datetime
from datetime import date
from . import  aiven
from .create_dic import get_comp_code
import json
import logging
from cntrfiles import controls

logger = logging.getLogger(__name__)
db_cache={}
sector_cache=[]
def upload_old_data():
  global table
  with open("mita.json", "r") as f:
   table = json.load(f)
import re

def compare_strings(str1, str2):
    # Split strings into lists using space and period as delimiters
    list1 = re.split(r'[.\s]+', str1.strip())
    list2 = re.split(r'[.\s]+', str2.strip())
    
    # Remove empty strings from lists
    list1 = [x for x in list1 if x]
    list2 = [x for x in list2 if x]
    
    # Find the smaller list
    smaller_list = list2 if len(list2) <= len(list1) else list1
    larger_list = list1 if len(list2) <= len(list1) else list2
    
    # Compare elements
    results = []
    for i in range(len(smaller_list)):
        if smaller_list[i] == larger_list[i]:
            results.append(f"'{smaller_list[i]}' equals '{larger_list[i]}'")
        elif smaller_list[i] in larger_list[i]:
            results.append(f"'{smaller_list[i]}' is a substring of '{larger_list[i]}'")
        elif larger_list[i] in smaller_list[i]:
            results.append(f"'{larger_list[i]}' is a substring of '{smaller_list[i]}'")
        else:
           return (False) 
    return (True)

# Example usage

def normalize_broker_name(brkr_name: str) -> str:
 for key, value in controls.brokers.items():
        if key.lower() in brkr_name.lower():
            return value

 return brkr_name



def valid_broker(brk,brk_check=True):
    if not brk_check:
      return True
    brk_list=["Geojit","HDFC","Axis"]
    for word in brk_list:
        if word in brk:
            return False
    return True 

def check_if_present_no_code(table):
 tobeadded=[]
 for i in table: ## list of new entries
  if i['code']:
      tobeadded.append(i)
      continue
  try: 
   report_date_str = i['report-date']
   try:
    datetime_object = report_date_str
   except ValueError as e:
     logger.error ("Error with datetime conversion {e} ")
     continue
   logger.info("Trying to add %s %s %s ",i["broker"],i["recommendation"],i["target"])
   c= aiven.db.row_exists_no_comp(i["broker"],i["recommendation"],i["target"])
   logger.info("Found %s entries",len(c))
   if not c:
       logger.info("Not in Db. Adding")
       tobeadded.append(i)
       continue
   mustbeadded=True
   for entry in c:
    logger.info("found in DB %s",entry)

    diff= abs(datetime_object-entry["report_date"]).days
    if diff <5:  ## May be same entry as in DB , must check the company name 
     logger.info("Report with same broker, recomm and target , must check name  ")
     if  compare_strings(i["Company"],entry["company"]):
      logger.info("Mail:Not adding . Page: %s , DB:%s \n",i,entry)
      mustbeadded=False
      break      
   if mustbeadded:
    logger.info("Adding this .... ")
    tobeadded.append(i)
 
  except Exception as e:
      logger.error("check if present :Error with ",str(e))
 return(tobeadded) 


def check_if_present(table,src,brk_check=True):
  new_table=[]
  add_codes_to_reports(table)
  for row in table:
   brk=normalize_broker_name(row['broker'])
   row['broker']=brk
  for data in table:
   print(data)
   if not valid_broker(data['broker'],brk_check):
       logger.info("Mail:Not adding  .Dropping as broker known %s, new Source: %s",data['broker'],src)
       continue
   if data['code']:
    val,url=check_in_dbcache(data['broker'],data['code'])
    if not val :
     new_table.append(data)
    else:
        logger.info("Mail:Not adding . %s %s %s present,new Source :%s",data['broker'],data['code'],url,src)
   else:
     new_table.append(data)
  return new_table 

def add_codes_to_reports(table):
 for data in table:
   realname,code=get_comp_code( data['Company'])
   print(realname,code)
   if code:
       data['Company']=realname
       data['code']=code
   else:
       data['code']=''

def get_last_ndays_data(days):
    date1 = date.today()
    dict_list=aiven.db.get_last_n_day_data(days,date1)
    for entry in dict_list:
        nsekey = entry["NSEKEY"]
        if nsekey not in db_cache:
            db_cache[nsekey] = []
        db_cache[nsekey].append(entry)
def get_last_ndays_sector_date():
 date1 = date.today()
 dict_list=aiven.db.get_last_ndays_sector_data(24,date1)
 for entry in dict_list:
  rep_name=entry['company']
  sector_cache.append(rep_name)


def check_in_dbcache(broker,nsekey):
    # Check if NSEKEY exists in the dictionary
    if nsekey in db_cache:
        # Check if any entry in the list has the matching broker
        for entry in db_cache[nsekey]:
            if entry['broker'].strip() == broker.strip():
                logger.info("Mail broker %s  and NSEKEY %s present in DB with URL %s",broker,nsekey,entry['URL'])
                return True,entry['URL']
    return False,""
def check_in_sector_cache(repName):
    if repName in sector_cache:
        return True
    return False
#get_last_ndays_data()
get_last_ndays_sector_date()
