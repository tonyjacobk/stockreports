from datetime import date, timedelta,datetime
from shkhan import shkhan_main 
import logging
from stockutils import get_target_and_recomm,print_table,get_last_report_date,check_if_present,db,update_last_report_date
logger = logging.getLogger(__name__)
    

def shellp_main(brk_tag,main_func,rep_analysis_needed,brokerName,brokerCode):
   reps=[]
   sects=[]
   start_date=get_last_report_date(brk_tag)
   start_date=last_date=last_date-timedelta(days=1)
   reps,sects,last_date=main_func(start_date)  
   res_reps=vent_res_main(start_date)
   reps=check_if_present(reps)
   if rep_anaysis_needed:
     add_target_and_recomm(reps)
   logger.info("Mail: %s Found %s new reports after scrapping",brokerName,len(reps))
   print_table(reps,logger)
   db.insert_into_database(reps,brokerCode)
   logger.info("Mail Sector files from broker - %s",brokerName)
   db.insert_into_sector(sects:)
   update_last_report_date(brk_tag,last_date)
