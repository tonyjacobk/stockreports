from telethon.sync import TelegramClient
import asyncio
import re
from telethon.tl.types import MessageMediaDocument
from stockutils import return_text,find_company,db,read_first_line,write_first_line,check_in_sector_cache,get_last_ndays_data,mycrony
from cntrfiles import controls
from .comp_and_brok import get_company_and_dnld_status,upload_and_update_sector,check_the_report,check_report_for_dircomp,get_dnld_needed_list,check_report_for_comps,get_dnld_list
import logging
from datetime import date, timedelta,datetime
from .tel_utils import write_dicts_to_file
from .tel_utils import remove_duplicate_files,is_direct_broker,preprocessName ,remove_already_processed_ids,read_dicts_from_file,write_dicts_to_file
logger = logging.getLogger(__name__)


api_id = '17206937'
api_hash = 'ab2de3d291b1f6317bb422cd23bf1712'

client = TelegramClient('mornin', api_id,api_hash)
client.start()

start_day=date.today()-timedelta(days=7)
group_entity = 'BTSReports'
usefulIds=[]
fromfile=[]
fileNames=set([])
lastid=None
def classify_reports(s: str) -> str:
    s_lower = s.lower()

    # Compile regex patterns
    init_pattern = re.compile(r'^(.+?)initiating coverage on(.+)$', re.IGNORECASE)
    sees_pattern = re.compile(r'^(.+?)sees (\d+)%? (?:up|down)side in(.+)$', re.IGNORECASE)
   
    if is_direct_broker(s_lower):
        return "dirbrk"
    # Check regex patterns first
    if init_pattern.match(s) or sees_pattern.match(s):
        return "compbrok"
    
    # Check other conditions
       
    if "thematic" in s_lower:
        return "thematic"
    if "result" in s_lower and ("review" in s_lower or "preview" in s_lower):
        return "sectres"
    if "earnings" in s_lower and ("review" in s_lower or "preview" in s_lower):
        return "sectres"
    if "morning" in s_lower or "amp " in s_lower or "daily" in s_lower or "technical" in s_lower or "derivatives" in s_lower or "exencial" in s_lower or "first call" in s_lower or "weekly" in s_lower or "wpi" in s_lower:
        return "daily"
    if "result" in s_lower and "update" in s_lower:
        return "compres"
    if "ipo" in s_lower:
        return "IPO"
    if "strategy" in s_lower:
        return "strategy"
    if "sector" in s_lower:
        return "sector"
    if "economic" in s_lower:
        return "econ"
    if "update on" in s_lower or "report on" in s_lower or "note on" in s_lower:
        return "onreport"
    if "daily" in s_lower or "rollover report" in s_lower or "oi report" in s_lower:
        return "daily"
    if "greed" in s_lower and "fear" in s_lower:
        return "sector"
    # Default fallback
    return "Others"





def is_direct_broker(fname):
     for i in controls.direct_brokers:
        if i.lower() in fname:
            print(i+"  direct broker")
            return True
     return False

async def tel_old_200():
    count=0
    old_message=int(read_first_line('./cntrfiles/beatstreet.txt').strip())
    async for message in client.iter_messages(group_entity,min_id=old_message-200,reverse=True):
     count=count+1
     if message.id > old_message:
         logger.info("200 over")
         return 
     try:
      if message.media:
       if isinstance(message.media, MessageMediaDocument):
         fname1=message.media.document.attributes[0].file_name
         fname1=preprocessName(fname1)
         fileNames.add(fname1)
         logger.info("Date %s Message id: %s, FileName:%s",message.date.date(),message.id ,fname1)
     except Exception as e:
         logger.info("Skipping this message %s for exception ",message,e)

async def tel_main():
    global lastid
    old_message=int(read_first_line('./cntrfiles/beatstreet.txt').strip())
    lastid=old_message
    async for message in client.iter_messages(group_entity, offset_date=start_day,min_id=old_message):
     lastid=message.id
     break
    async for message in client.iter_messages(group_entity, offset_date=start_day,min_id=old_message):
     try:
      if message.media:
       if isinstance(message.media, MessageMediaDocument):
         fname1=message.media.document.attributes[0].file_name
         fname=preprocessName(fname1)
         if fname in fileNames:
          logger.info("Report date %s Messageid %s: %s already present ", message.date.date(),message.id,fname1)
          continue
         u=classify_reports(fname)
         logger.info("Report date %s  Messageid %s : %s is of type %s",message.date.date(),message.id,fname,u)
         if u=="compbrok":
             usefulIds.append({"messid":message.id,"type":"compbrok","fname":fname1})
             fileNames.add(fname)
         if u=="compres":
             usefulIds.append({"messid":message.id,"type":"compres","fname":fname1})
             fileNames.add(fname)
         if u=="sector" or u=="thematic":
             usefulIds.append({"messid":message.id,"type":"sector","fname":fname1})
             fileNames.add(fname)
         if u=="Others" :
             usefulIds.append({"messid":message.id,"type":"others","fname":fname1})
             fileNames.add(fname)
         if u=="onreport":
             usefulIds.append({"messid":message.id,"type":"onreport","fname":fname1})
             fileNames.add(fname)

     except Exception as e:
       print(message) 
def beat_morning():
 global fileNames,lastid,fromfile
 try:
  loop = asyncio.get_event_loop()
  loop.run_until_complete(tel_old_200())
  loop.run_until_complete(tel_main())
  fromfile=read_dicts_from_file('dailyids.txt')
  print ("Total entries in from file ",len(fromfile))
  print(lastid," is the last id")
  usefulIds.extend(fromfile)
  write_dicts_to_file(usefulIds,"dailyids.txt")
  write_first_line('./cntrfiles/beatstreet.txt',str(lastid))
 except Exception as e:
  print(f"Unexpected error: {type(e).__name__}: {e} - Skipping this message")
  return

