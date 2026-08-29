from telethon.sync import TelegramClient
import asyncio
import re
from telethon.tl.types import MessageMediaDocument
from cntrfiles import controls
from .comp_and_brok import is_report_present,do_second_round_analysis,process_sector_file
import logging
from datetime import date, timedelta,datetime
logger = logging.getLogger(__name__)
from .tel_utils import is_direct_broker,preprocessName, write_text_to_file,analyze_recs
from stockutils import read_first_line,write_first_line,get_last_ndays_data
api_id = '17206937'
api_hash = 'ab2de3d291b1f6317bb422cd23bf1712'

client = TelegramClient('mornin', api_id,api_hash)
client.start()
group_entity = 'BTSReports'

fileNames=set([])
lastid=None
pdftext=[]
reps=[]


RE_INIT = re.compile(r'initiating coverage on', re.IGNORECASE)
RE_SEES = re.compile(r'sees \d+%? (?:up|down)side in', re.IGNORECASE)

DAILY_KEYWORDS = (
    "morning", "amp ", "daily", "technical", "derivatives", "exencial", 
    "first call", "weekly", "wpi", "rollover report", "oi report"
)

DONT_CARE = [
    "crypto", "vontobel", "mckinsey", "standard chartered", "tiger research",
    "dbs bank", "kotak neo", "investment outlook", "banca", "amundi", "allianz",
    "adb ", "boj ", "banque ", "binance ", "stablecoin", "ddw", "global outlook",
    "oecd ", "imf ", "blockchain", "bridgewise", "socgen", "barclays", "zurich",
    "deutsche bank", "coinbase", "macro", "bcg ", "boe ", "boston", "wharton",
    "payments infrastructure","channel check","isda","bank of england","gsx","bca","gs brian garrett","ajzal","bis","hedge fund","black rock","ifc","mufg","merics","wisdom tree","wisdomtree","newyork life","new york life","blackrock","capco","bundesbank","harvard"
]

def classify_reports(s: str) -> str:

    s_clean = s.strip()
    s_lower = s_clean.lower()

    # Priority 1: Immediate Exclusions (Fastest check first)
    if any(item in s_lower for item in DONT_CARE):
        return "NI"

    # Priority 2: High-level classification
    if is_direct_broker(s_lower):
        return "dirbrk"

    # Priority 3: Complex Patterns (Regex)
    if RE_INIT.search(s_lower) or RE_SEES.search(s_lower):
        return "compbrok"

    # Priority 4: Keyword Logic
    if "thematic" in s_lower:
        return "thematic"
    
    # Combined Result/Earnings Logic
    if any(k in s_lower for k in ("result", "earnings")) and \
       any(k in s_lower for k in ("review", "preview")):
        return "sectres"
    
    if "result" in s_lower and "update" in s_lower:
        return "compres"

    if any(k in s_lower for k in DAILY_KEYWORDS):
        return "daily"

    # Simple Single Keyword Checks
    mapping = {
        "ipo": "IPO",
        "strategy": "strategy",
        "sector": "sector",
        "economic": "econ"
    }
    for key, label in mapping.items():
        if key in s_lower:
            return label

    # Special Multi-keyword cases
    if "update on" in s_lower or "report on" in s_lower or "note on" in s_lower:
        return "onreport"
    
    if ("greed" in s_lower and "fear" in s_lower) or \
       ("clsa" in s_lower and "bit" in s_lower and "pieces" in s_lower):
        return "sector"

    return "Others"


async def handle_single_message(message,tc):
  global reps
  global fileNames
  print("In handle single nessage %s",message.id)
  try:
      if message.media:
       if isinstance(message.media, MessageMediaDocument):
         fname1=message.media.document.attributes[0].file_name
         fname=preprocessName(fname1)
         rep_date=message.date.date()
         if fname in fileNames:
          logger.info("Report date %s Messageid %s: %s already present ", message.date.date(),message.id,fname1)
          return tc
         fileNames.add(fname)        
         filesize=message.file.size
         if filesize >  7 * 1024 * 1024:
           logger.info ("File too huge .. not processing  %s %s",fname,message.id1)
           return tc 
         tc =tc+1
         u=classify_reports(fname)
         logger.info("Report date %s  Messageid %s : %s is of type %s",message.date.date(),message.id,fname,u)
   #      return tc
         if u in ["compbrok","compres","onreport","Others"]:
          await handle_single_company_broker_report(message,fname,u,reps,rep_date)
         if u=="sector" or u=="thematic":
          await client.download_media(message, file="/tmp/comp.pdf")
          print("Sector file downloaded")
          process_sector_file(fname,None,rep_date)
         return tc 
      return tc
  except Exception as e:
       print(message)
       return tc

async def handle_single_company_broker_report(message,fname,u,reps,rep_date):
  global pdftext
  ret, ds=is_report_present(fname,u)
  if ret == -1:
      return 
  await client.download_media(message, file="/tmp/comp.pdf")
  do_second_round_analysis(ds,u,fname,rep_date,reps,pdftext,message.id)





async def tel_old_200():
    count=0
    old_message=int(read_first_line('./cntrfiles/ibeat.txt').strip())
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
       print(f"Unexpected error: {type(e).__name__}: {e} - Skipping this message")

async def read_new_messages(fullread=True,mc=25):
    total_count=0
    global lastid
    old_message=int(read_first_line('./cntrfiles/ibeat.txt').strip())
    lastid=old_message
    print(lastid, " Lastid")
    async for message in client.iter_messages(group_entity,min_id=old_message,reverse=True):
     if not fullread and total_count >= mc:
         return
     total_count= await handle_single_message(message,total_count)
     lastid=message.id
     print("Last id is ", lastid)

async def read_single_message(messid):
 message=await client.get_messages(group_entity, ids=messid)
 await handle_single_message(message,0)

async def handle_direct_upload(messid):
  message=await client.get_messages(group_entity, ids=messid)
  try:
      if message.media:
       if isinstance(message.media, MessageMediaDocument):
         fname1=message.media.document.attributes[0].file_name
         fname=preprocessName(fname1)
         rep_date=message.date.date()
         await client.download_media(message, file="/tmp/comp.pdf")
         print("Sector file downloaded")
         process_sector_file(fname,None,rep_date)
  except Exception as e:
       print(f"Unexpected error: {type(e).__name__}: {e} - Skipping this message")



async def read_file_load():
    messids=[]
    with open('/tmp/messids', 'r') as file:
     for line in file:
        # line.strip() removes the trailing newline character (\n)
      messids.append(line.strip())
      print(line)
      await read_single_message(int(line.strip()))


def beat_morning(param,id=""):
 global fileNames,lastid,fromfile
 try:
  get_last_ndays_data(20)
  loop = asyncio.get_event_loop()
  if param=="DOONE":
    loop.run_until_complete(read_single_message(id))
  if param=="FROMFILE":
      loop.run_until_complete(read_file_load())
  if param=="DOALL":
      tel_old_200()
      loop.run_until_complete(read_new_messages(True,100))
  if param=="DOSOME":
     tel_old_200()
     loop.run_until_complete(read_new_messages(False,50))
  if param=="DIRECT":
      loop.run_until_complete(handle_direct_upload(id))
 except Exception as e:
  print(f"Unexpected error: {type(e).__name__}: {e} - Skipping this message")
  return
 finally:
  if not lastid:
      logger.error("lastid missing")
  else:
    write_first_line('./cntrfiles/ibeat.txt',str(lastid))
  analyze_recs.write_analyaze_records()
 
