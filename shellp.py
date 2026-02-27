from datetime import date, timedelta,datetime
from shkhan import shkhan_main 
from hdfc import hdfc_main
from vent import vent_main
from dolat import dolat_main
import logging
import sys
from stockutils import get_target_and_recomm,print_table,get_last_report_date,check_if_present,db,update_last_report_date,check_if_present_no_code
logger = logging.getLogger(__name__)

def initialize_logger ():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename='/tmp/myapp.log', level=logging.INFO)
    logger.info('Started Logging from main ')


def shellp_main(brk_tag,main_func,rep_analysis_needed,brokerName,brokerCode):
 try:
   reps=[]
   sects=[]
   start_date=get_last_report_date(brk_tag)
   start_date=start_date-timedelta(days=1)
   reps,sects,last_date=main_func(start_date)  
   reps=check_if_present(reps,brokerCode,False)
   if rep_analysis_needed:
     for i in reps:
      recomm,target=get_target_and_recomm(i['link'])
      i['recommendation']=recomm
      i['target']=target
   reps=check_if_present_no_code(reps)
   logger.info("Mail: %s Found %s new reports after scrapping",brokerName,len(reps))
   print_table(reps,logger)
   db.insert_into_database(reps,brokerCode)
   logger.info("Mail Sector files from broker - %s",brokerName)
   db.insert_into_sector(sects)
   update_last_report_date(brk_tag,last_date)
 except Exception as e:
   print(f"Unexpected error: {type(e).__name__}: {e} - Skipping this broker..")

def get_reports(brk_list):
 initialize_logger()
 print(brk_list)
 if "shkhan" in brk_list:
  shellp_main("shkhan",shkhan_main,True,"ShareKhan","shkhan")
 if "hdfc" in brk_list:
  shellp_main("hdfc",hdfc_main,True,"HDFC Sec","hdfc`")
 if "vent" in brk_list:
  shellp_main("vent",vent_main,True,"Ventura Securities","vent")
 if "dolat" in brk_list:
  shellp_main("dolat",dolat_main,True,"Dolat Securities","dolat")
if len(sys.argv) > 1:
    mylist=sys.argv[1:]
    print(mylist)
    get_reports(mylist)

