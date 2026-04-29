import re
from .tel_utils import find_broker_from_fileName,get_correct_broker_and_nsecode
from stockutils import return_text,db,MegaMan,check_in_dbcache
from cntrfiles import controls
from .tel_utils import extract_target_price,extract_recommendation,remove_dates_and_quarters,preprocessName
from .tel_utils import get_broker_and_company_for_on_reports,extract_broker_and_company_compres,extract_broker_and_company_compbrok
from datetime import date,datetime
from  .pdf_utils import extract_needed_texts
import json
import contvar
import logging
logger = logging.getLogger(__name__)



def get_company_and_broker(fileName,mtype):
 comp_ds={"company":"","broker":"","code":""}
 funcdict={"compres":extract_broker_and_company_compres,"compbrok":extract_broker_and_company_compbrok,"onreport":get_broker_and_company_for_on_reports} 
 comp_ds["company"],comp_ds["broker"] =funcdict[mtype](fileName)
 get_correct_broker_and_nsecode(comp_ds)
 print("After get_correct_broker",comp_ds)
 if comp_ds["cf"] and comp_ds["bf"]:
    print("Checking duplicates")
    pr,url=check_in_dbcache(comp_ds["broker"],comp_ds["code"])
    if pr:
        return -1,comp_ds

 return 1,comp_ds

def download_broker_report_and_get_recomm_target(length,fname,comp_det,date):
  text=return_text('/tmp/comp.pdf',length)
  imptext=extract_needed_texts("/tmp/comp.pdf")
  text=text+" "+imptext
  if not imptext and not comp_det["cf"]:
      return -1, None,None,text
  print(text)
  recomm=extract_recommendation(text)
  tp=extract_target_price(text)
  logger.info("Extracted Recommendation and target %s %s",recomm,tp)
  return 1,recomm,tp,text


def check_report_for_dircomp(fname,comp_det,date):
   print("+++++++++++++++++++++++++++++++++++++++++")
   print(fname)
   print(comp_det)
   retval,recomm,tp,imptxt=download_broker_report_and_get_recomm_target(2000,fname,comp_det,date)
   if retval == -1:
    return 
   logger.info("Extracted Recommendation and target %s %s",recomm,tp)
   row={"Company":comp_det["company"],"broker":comp_det["broker"],"recommendation":recomm,"target":tp,"report-date":date,"code":comp_det['code']}
   print("check_report_for_dircomp",row)
   upload_company_report_and_update_db(row,fname)


    
def upload_mega_file(fname):
   link="http://mydummyfile.com"
   if contvar.testtele==0:
       link=MegaMan.upload_file(fname)
   return link


def check_the_other_report(fname,date,pdftext,messid):
    print("*********************************************************")
    print(fname, "File Name")
    retval,recomm,tp,imptxt=download_broker_report_and_get_recomm_target(100,fname,{"cf":False},date)
    brk=find_broker_from_fileName(fname+imptxt)
    if retval==-1:
      logger.info (" Mail %s No details available .. Classifing as sector file ",fname)
      process_as_sector_file(fname,brk,date)
      return 
    link=upload_mega_file(fname)
    datestr=date.strftime("%Y-%m-%d")
    append_text={"id":messid,"text":fname+imptxt,"link":link,"date":datestr,'recommendation':recomm,'target_price':tp,'broker':brk}
    pdftext.append(append_text)
    logger.info("Need further analysis %s :",append_text)
    return 0

def process_as_sector_file(fname,broker,date):
    print(fname, " is sector file")
    upload_sector_file_and_update_db(fname,date,broker)




def upload_company_report_and_update_db(row,fname):
    logger.info("Mail Data to be inserted into DB %s", row)
    if contvar.testtele==1:
     logger.info("Test tele enanled .. Returning")
     return
    link=MegaMan.upload_file(fname)
    if not link:
       logger.error ("Could not obtain link .. Returning ")
       return
    row["link"]=link
    rlist=[row]
    db.insert_into_database(rlist,'tel')

def upload_sector_file_and_update_db(fileName,date,brok):
    logger.info("Trying to upload %s",fileName)
    link=upload_mega_file(fileName)
    date=date.strftime("%Y-%m-%d")
    if not link:
       logger.error ("Could not obtain link .. Returning ")
       return
    row=[{"broker":brok, "company":fileName,"site":"tel","link":link,"report-date":date}]
    logger.info("Mail Adding to sector reports %s",row)
    print(row)
    if contvar.testtele==0:
     db.insert_into_sector(row)
     
def upload_and_update_sector(fileName,date,desc):
    brok=find_broker_from_fileName(desc)
    upload_sector_file_and_update_db(fileName,date,brok)



