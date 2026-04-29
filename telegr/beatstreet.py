from telethon.sync import TelegramClient
import asyncio
import re
import copy
from telethon.tl.types import MessageMediaDocument
from stockutils import return_text,find_company,db,read_first_line,write_first_line,check_in_sector_cache,get_last_ndays_data,mycrony
from cntrfiles import controls
from .comp_and_brok import get_company_and_dnld_status,upload_and_update_sector,check_the_report,check_report_for_dircomp,get_dnld_needed_list,check_report_for_comps,get_dnld_list
import logging
import traceback
from datetime import date, timedelta,datetime
from .tel_utils import remove_duplicate_files,is_direct_broker,preprocessName, read_messids_from_file_json,write_messids_to_file_json,remove_already_processed_ids,read_dicts_from_file,write_dicts_to_file,write_text_to_file
logger = logging.getLogger(__name__)


api_id = '17206937'
api_hash = 'ab2de3d291b1f6317bb422cd23bf1712'
client = TelegramClient('anony', api_id,api_hash)
client.start()

start_day=date.today()-timedelta(days=7)
otherids=[]
company_ids=[]
group_entity = 'BTSReports'
last_id=None
daily_ids=[] # All ids to be processed
pdftext=[]

async def get_other_messages():
   global otherids,daily_ids,pdftext
   logger.info("List of other messages %s",otherids)
   try:
    for i in otherids:
     async for message in client.iter_messages(group_entity,ids=i['messid']):
      fname1=message.media.document.attributes[0].file_name
      filesize=message.file.size
      rep_date=message.date.date()
      if check_in_sector_cache(fname1):
         logger.info("File %s already present ..",fname1)
         remove_a_messid(i['messid'],daily_ids)
         continue
      if filesize >  5 * 1024 * 1024:
         logger.info ("File too huge .. not processing %s",fname1)
         remove_a_messid(i['messid'],daily_ids)
         continue

      await client.download_media(message, file="/tmp/comp.pdf")
      ret=check_the_report(fname1,i,rep_date,pdftext,i['messid'])
      remove_a_messid(i['messid'],daily_ids)
   except Exception as e:
       raise e

async def get_company_messages(idlist):
   global pdftext
   copied_idlist=copy.deepcopy(idlist)
   kmessids=get_dnld_list(copied_idlist) ## Already present reports removed , Nifyids found for companies
   print(kmessids)
   kmessids_list = {item["messid"] for item in kmessids}
   for i in idlist:
       if i['messid'] not in kmessids_list:
        remove_a_messid(i['messid'],daily_ids)
   try:
    for i in kmessids:
     async for message in client.iter_messages(group_entity,ids=i['messid']):
      fname1=message.media.document.attributes[0].file_name
      filesize=message.file.size
      rep_date=message.date.date()
      if filesize >  5 * 1024 * 1024:
         logger.info ("File too huge .. not processing %s",fname1)
         remove_a_messid(i['messid'],daily_ids)
         continue

      await client.download_media(message, file="/tmp/comp.pdf")
      retval=check_report_for_comps(fname1,i,rep_date,pdftext,i['messid'])
      remove_a_messid(i['messid'],daily_ids)
   except Exception as e:
       raise e
def remove_a_messid(remove_id,dict_list):
    for d in dict_list:
     if d["messid"] == remove_id:
        dict_list.remove(d)
        break

async def read_daily():
   global otherids,last_id,company_ids,daily_ids,pdftext
   count =1
   daily_ids=read_dicts_from_file('dailyids.txt')
   copied_ids=copy.deepcopy(daily_ids)
   tobetried=len(daily_ids)
   if len(daily_ids) <=0:
     logger.info("Cron tab removed")
     return
   if len(daily_ids) < 5:
    tobetried=len(daily_ids)

   try:
    while count <=tobetried:
     messid=copied_ids[-1*count]['messid']
     u=copied_ids[-1*count]['type']
     fname=copied_ids[-1*count]['fname']
     logger.info("Chose file Name %s",fname)
     print(messid,u,fname)
     if u=="compbrok":
         company_ids.append({"messid":messid,"fileName":fname,"mtype":"compbrok"})
     if u=="compres":
         company_ids.append({"messid":messid,"fileName":fname,"mtype":"compres"})
     if u=="onreport":
        company_ids.append({"messid":messid,"fileName":fname,"mtype":"onreport"})
     if u=="sector" or u=="thematic":
             message=await client.get_messages(group_entity, ids=messid)
             fname1=message.media.document.attributes[0].file_name
             rep_date=message.date.date()
             logger.info ("To be downloaded %s",fname1)
             await client.download_media(message, file="/tmp/comp.pdf")
             upload_and_update_sector(fname1,rep_date,fname)
             remove_a_messid(messid,daily_ids)
     if u=="others" :
          otherids.append({"messid":messid,"fileName":fname})
     count=count+1
   except Exception as e:
       raise  e
  


def beat_main():
 
 global daily_ids,company_ids
 try:
  get_last_ndays_data(20)
  logger.info("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
  loop = asyncio.get_event_loop()
  loop.run_until_complete(read_daily())
  
  loop.run_until_complete(get_other_messages())
  """
  loop.run_until_complete(get_company_messages(company_brk_ids,'compbrok'))
  loop.run_until_complete(get_company_messages(compresids,'compres'))
  """
  loop.run_until_complete(get_company_messages(company_ids))
 except Exception as e:
  print(f"Unexpected error: {type(e).__name__}: {e} - Skipping this message")
  traceback.print_exc()
 finally:
  print(pdftext)
  write_text_to_file(pdftext,"pdfanalysis")
