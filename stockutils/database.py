import pymysql
from datetime import datetime

from . import  aiven
import json
import logging
logger = logging.getLogger(__name__)

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
    if "Choice" in brkr_name:
        return "Choice Equity Broking"
    elif "Emkay" in brkr_name:
        return "Emkay Global Financial"
    return brkr_name

def check_if_present(table):
 tobeadded=[]
 for i in table: ## list of new entries
  logger.info("\nTrying to add %s",i)
  try: 
   report_date_str = i['report-date'].rstrip('.') # Remove trailing dot
   print(i)
   try:
    datetime_object1 = datetime.strptime(report_date_str, "%B %d, %Y").strftime("%Y-%m-%d")
    datetime_object = datetime.strptime(datetime_object1, "%Y-%m-%d").date()
   except ValueError :
     print ("Error ")
     continue
   c= aiven.row_exists_no_comp(i["broker"],i["recommendation"],i["target"])
   if not c:
       print("Not in Db")
       tobeadded.append(i)
       continue
   for entry in c:
    logger.info("found in DB %s",i)
    print(datetime_object,entry["report_date"])

    diff= abs(datetime_object-entry["report_date"]).days
    print(diff)
    print(datetime_object,entry["report_date"])
    if diff <5:  ## May be same entry as in DB , must check the company name 
     logger.info("Not adding as rows are same  ")
     logger.info ("from Page %s",i)
     logger.info(" from DB  %s",entry)
    else:
      tobeadded.append(i)
      continue
    if  compare_strings(i["Company"],entry["company"]): #name is same ,need not be added
     logger.info("Not adding as rows are same  \n")
     logger.info ("from Page ",i)
     logger.info("\n from DB ",entry)
 
    else:
      tobeadded.append(i)
  except Exception as e:
      logger.error  ("check if present :Error with ",str(e))
 return(tobeadded) 

