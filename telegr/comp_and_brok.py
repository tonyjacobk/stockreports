import re
from datetime import date,datetime
import json
import contvar
import logging
logger = logging.getLogger(__name__)
from .broker_comp_finder import get_broker_and_company
from stockutils import check_in_dbcache,db,MegaMan,check_in_sector_cache
from .broker_specific import get_company_from_reports
from .tel_utils import extract_target_price_and_recomm,find_broker_from_fileName,upload_mega_file,add_to_db,find_broker_from_text
from .pdf_utils import extract_text_from_pdf

def is_report_present(fileName,mtype):
 comp_ds=get_broker_and_company(fileName,mtype)
 logger.info("comd_ds in is_report_present %s",comp_ds)
 if comp_ds["cf"] and comp_ds["bf"]:
    pr,url=check_in_dbcache(comp_ds["broker"],comp_ds["code"])
    if pr:
        return -1,comp_ds
 logger.info("%s,%s not present",comp_ds["broker"],comp_ds["code"]) 
 return 1,comp_ds

def do_second_round_analysis(ds,u,fname,rep_date,reps,pdftext,messid):
 text=extract_text_from_pdf('/tmp/comp.pdf',2000)
 tp,recomm=extract_target_price_and_recomm(text) 
 print("Target price , Recomm from do_second_round_analysis",tp,recomm)
 if u=="Others":
  retval,ds=do_second_round_for_Others(text,tp,recomm,ds)
  print("Retval ,ds Others  After second round", retval,ds)
 else:
      retval,ds=classify_reports(ds,tp,recomm)
 match retval:
     case -1:
         return -1,None
     case 1:
       row={"Company":ds["company"],"broker":ds["broker"],"recommendation":recomm,"target":tp,"report-date":rep_date,"code":ds['code']} 
       upload_company_report_and_update_db(row,fname,reps)
     case 2:
         process_sector_file(fname,ds["broker"],rep_date)
     case 3:
           create_analyze_data(rep_date,ds,fname,messid,tp,recomm,text,pdftext)

def do_second_round_for_Others(text,tp,recomm,ds):
 needCheck=False
 if not (ds['bf']):
     brk=find_broker_from_text(text)
     print("Broker is brk",brk)
     if brk:
         ds['broker']=brk
         ds['bf']=True
         needCheck=True
 if not ds['cf'] and ds['bf'] :
  comp,code=get_company_from_reports(ds['broker'],text)
  if code:
      ds['cf']=True
      ds['code']=code
      ds['company']=comp
      needCheck=True
 if ds["cf"] and ds["bf"] and needCheck:
    print("Checking duplicates")
    pr,url=check_in_dbcache(ds["broker"],ds["code"])
    if pr:
        return -1,ds # Already present 
 ret,val= classify_reports(ds,tp,recomm)
 return ret,val

def classify_reports(ds,tp,recomm):
 if ds['code']=="" and not( tp or recomm):  # No company Info and details --> sector
      return 2,ds
 if ds["code"] =="" and (tp or recomm):   # Ds code is not there but details present--> Analysis
      return 3,ds
 if ds['cf'] and ds["bf"] : #Broker, company  --> Add
      return 1, ds
 return 3,ds



def process_sector_file(fname,brk,date):
   if check_in_sector_cache(fname):
       logger.info("Mail Sector file %s already present",fname)
       return
   if not brk:
       brk=find_broker_from_fileName(fname)
   upload_sector_files(fname,brk,date)



def upload_company_report_and_update_db(row,fname,reps):
  if {row['code'], row['broker']} in reps:
      logger.info("Mail broker %s  and NSEKEY %s present in DB with URL %s",row['broker'],row['code'],"https://telegram/now")
      return 
  logger.info("Mail Data to be inserted into DB %s", row)
  link=upload_mega_file(fname)
 # link=" https://mega.co.nz/#!GMkHWJST!5fnYP4PCRucyvCnG4vc6cJ3k6jEDisvTfsZkDx7SlyM"
  row["link"]=link
  reps.append(row)
  add_to_db("comp",row)

def upload_sector_files(fname,broker,date):
    link=upload_mega_file(fname)
    row=[{"broker":broker, "company":fname,"site":"tel","link":link,"report-date":date}]
    logger.info("Mail Adding to sector reports %s",row)
    add_to_db("sect",row)

def create_analyze_data(date,ds,fname,messid,tp,recomm,text,pdftext) :
   link=upload_mega_file(fname)
   datestr=date.strftime("%Y-%m-%d")
   append_text={"id":str(messid),"text":text,"link":link,"date":datestr,'recommendation':recomm,'target_price':tp,'broker':ds["broker"]}
   logger.info("Need further analysis %s :",append_text)
   pdftext.append(append_text) 
