import re
from .tel_utils import find_broker_from_fileName,get_correct_broker_and_nsecode,clean_and_convert,modify_with_correct_broker_and_nsecodes
from stockutils import return_text,find_company,db,MegaMan,get_comp_code,check_in_dbcache,get_last_ndays_data,ceramain
from cntrfiles import controls
import contvar
from .tel_utils import extract_target_price,extract_recommendation,remove_dates_and_quarters,clean_result_update_file,get_broker_part_from_fileName,preprocessName,extract_broker_and_company_compres,extract_broker_and_company_compbrok
from datetime import date,datetime
from .tel_utils import get_broker_and_company_for_on_reports
from nsecodeagent import call_report_agent
from .check import extract_needed_texts
import json
import logging
from .mylist import plist
logger = logging.getLogger(__name__)


def get_dnld_list(mylist):
 
 funcdict={"compres":extract_broker_and_company_compres,"compbrok":extract_broker_and_company_compbrok,"onreport":get_broker_and_company_for_on_reports}
 for i in mylist:
  func=funcdict[i["mtype"]]
  logger.info("Getting broker and company from %s",i['fileName'])
  comp,brok =func(i['fileName'])
  i['company']=comp
  i['broker']=brok

 logger.info("Broker Company found  %s",mylist)
 modify_with_correct_broker_and_nsecodes(mylist)
 logger.info("After processing %s",mylist)
 remove_already_present(mylist)
 logger.info ("After removing %s",mylist)
 return(mylist)

def get_dnld_needed_list(mylist):
 for i in mylist:
  brk=get_broker_part_from_fileName(i['fileName'])
  inputfile=i['fileName']
  cleaned=clean_result_update_file(inputfile,brk)
  i['company']=" ".join(cleaned.split()[:2])
  i['broker']=brk
 logger.info("Result updates found %s",mylist)
 modify_with_correct_broker_and_nsecodes(mylist)
 logger.info("After processing %s",mylist)
 remove_already_present(mylist)
 logger.info ("After removing %s",mylist)
 return(mylist)


def get_company_and_dnld_status(fname):
 dnld=True
 det =extract_broker_and_company(fname)
 logger.info("Extracted broker %s and company %s from file %s",det["broker"],det["company"],fname) 
 get_correct_broker_and_nsecode(det)
 logger.info("Added company code %s",det)
 if (det['valid']):
  ret=check_in_dbcache(det['broker'],det['code'])
  if ret :
      print(det['broker'],det['company'], " Present in DB")
      dnld=False
 return dnld,det

get_broker_and_company_for_on_reports

def check_report_for_dircomp(fname,comp_det,date):
   print("+++++++++++++++++++++++++++++++++++++++++")
   print(fname, "File Name")
   print(comp_det)
   text=return_text('/tmp/comp.pdf',2000)
   imptext=extract_needed_texts("/tmp/comp.pdf")
   if not imptext and not comp_det["cf"]:
      logger.info (" Mail %s No details available .. Classifing as sector file ",fname)
      process_as_sector_file(fname,comp_det,date)
      return
   text=text+" "+imptext
   print(text)
   recomm=extract_recommendation(text)
   tp=extract_target_price(text)
   logger.info("Extracted Recommendation and target %s %s",recomm,tp)
   row={"Company":comp_det["company"],"broker":comp_det["broker"],"recommendation":recomm,"target":tp,"report-date":date,"code":comp_det['code']}
   print("check_report_for_dircomp",row)
   upload_report_and_db(row,fname)

def check_report_for_comps(fname,comp_det,date,pdftext,messid):
    retval=1  # File needs no further processing #
    if comp_det['valid']:
      check_report_for_dircomp(fname,comp_det,date)
    else:
     retval= check_the_report(fname,comp_det,date,pdftext,messid)
    return retval        
def check_report_for_on_reports(fname):
    brok,comp=get_broker_and_company_for_on_reports(fname)
    

def check_the_report(fname,comp_det,date,pdftext,messid):
    comp_det["bf"]=False
    comp_det["cf"]=False
    comp_det["broker"]=""
    print("*********************************************************")
    print(fname, "File Name")
    print(comp_det)
    text=return_text('/tmp/comp.pdf',100)
    text=fname+"||"+text
    print(text)
    imptext=extract_needed_texts("/tmp/comp.pdf")
    print("-----------------------------------------------------")
    print(imptext)
    if not imptext :
      logger.info( "%s is a sector file ..after PDF analysis",fname)
      process_as_sector_file(fname,comp_det,date)
      return 1
    link=MegaMan.upload_file(fname)
    datestr=date.strftime("%Y-%m-%d")
    recomm=extract_recommendation(text+imptext)
    tp=extract_target_price(text+imptext)
    brk=find_broker_from_fileName(text+imptext) 
    pdftext.append({"id":messid,"text":text+imptext,"link":link,"date":datestr,'recommendation':recomm,'target_price':tp,'broker':brk})
    logger.info("Need further analysis %s :",pdftext)
    return 0

def process_as_sector_file(fname,comp_det,date):
    print(fname, " is sector file")
    broker="Unknown"
    if comp_det["broker"]:
      broker=comp_det["broker"]
      
    upload_sector_file_and_update_db(fname,date,broker)

def get_report_details_withAI(fname,text,comp_det,mdate):
    bf=comp_det["bf"]
    cf=comp_det["cf"]
    logger.info("Text send to GenAI %s",text)
    res=call_report_agent(text)
    details=clean_and_convert(res)
    if not details:
     logger.info("AI did not return proper details .. Treating as Sector file %s",fname)
     process_as_sector_file(fname,comp_det,mdate)
     return{}
    print(details)
    if "Sector" in details:
      process_as_sector_file(fname,comp_det,mdate)
      logger.info("%s is a Sector Report after AI analysis",fname)
      return {}
    if "Others" in details:
      process_as_sector_file(fname,mdate)
      logger.info("Could not classify file %s",fname)
      return {}
    logger.info("Details from GENAI %s",details)
    try:
       idate=datetime.strptime(details["date"],"%d %B ,%Y").date()
    except Exception:
         idate=mdate
    fdate=idate.strftime("%B %d, %Y")
    if not comp_det["cf"]:  # company name from fileName not valid try AI provided Name
      comp,code=get_comp_code(details["Company"].strip())
      if code:
       cf=True
    else:  ## company Valid ,Find the Name as only NSE code available
      comp=comp_det["company"]
      code=comp_det["code"]
    if not comp_det["bf"]:
      brk=find_broker_from_fileName(details["Broker"].strip())
      if brk:
       broker=brk
       bf=True
      else:
         broker=comp_det["broker"] 
    else:
      broker=comp_det["broker"]

    row={"Company":comp,"broker":broker,"recommendation":details["Recommendation"],"target":details["Target Price"],"report-date":fdate,"code":code}
    return(row)



def upload_report_and_db(row,fname):
    if contvar.testtele==1:
     logger.info("Test tele enanled .. Returning")
     return
    link=MegaMan.upload_file(fname)
    if not link:
       logger.error ("Could not obtain link .. Returning ")
       return
    row["link"]=link
    rlist=[row]
    logger.info("Mail Data to be inserted into DB %s", row)
    db.insert_into_database(rlist,'tel')

def upload_sector_file_and_update_db(fileName,date,brok):
    logger.info("Trying to upload %s",fileName)
    link=MegaMan.upload_sector_file(fileName)
    date=date.strftime("%Y-%m-%d")
    if not link:
       logger.error ("Could not obtain link .. Returning ")
       return
    row=[{"broker":brok, "company":fileName,"site":"tel","link":link,"report-date":date}]
    logger.info("Mail Adding to sector reports %s",row)
    print(row)
    db.insert_into_sector(row)
def upload_and_update_sector(fileName,date,desc):
    brok=find_broker_from_fileName(desc)
    upload_sector_file_and_update_db(fileName,date,brok)




def remove_already_present(clist):
  pops=[]
  for i in range(len(clist)):
     if clist[i]["cf"] and clist[i]["bf"]:
      pr,url=check_in_dbcache(clist[i]["broker"],clist[i]["code"])
      if pr:
          pops.append(i)
  for i in sorted(pops, reverse=True):
        del clist[i]
  return clist

