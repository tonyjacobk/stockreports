from telethon.sync import TelegramClient
import asyncio
import re
from telethon.tl.types import MessageMediaDocument
from stockutils import return_text,find_company,db,read_first_line,write_first_line
from cntrfiles import controls
from .comp_and_brok import upload_and_update_sector,get_company_and_dnld_status
import logging
logger = logging.getLogger(__name__)


api_id = '17206937'
api_hash = 'ab2de3d291b1f6317bb422cd23bf1712'
client = TelegramClient('anon', api_id,api_hash)
client.start()
from datetime import date,datetime
hist_date=date.today()
do_download=True
not_needed_reports=["IPO"]

import re

def preprocessName(fname):
     # Replace _ and + with single space
    processed = fname.replace('_', ' ').replace('+', ' ')

    # Replace multiple spaces with single space
    processed = re.sub(r'\s+', ' ', processed)
    return (processed)


def find_broker_from_fileName( fname):

    
    for key, value in controls.brokers.items():
        if key in fname:
            return value
    
    return None
import re

def classify_reports(s: str) -> str:
    s_lower = s.lower()

    # Compile regex patterns
    init_pattern = re.compile(r'^(.+?)initiating coverage on(.+)$', re.IGNORECASE)
    sees_pattern = re.compile(r'^(.+?)sees \d+% (?:up|down)side in(.+)$', re.IGNORECASE)
   
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
    if "daily" in s_lower:
        return "daily"
    # Default fallback
    return "Others"


def get_first_two_words(text):
    if not isinstance(text, str) or not text.strip():
        return ""

    words = text.replace('_', ' ').split()
    if len(words) ==1 :
        return(words)
    return ' '.join(words[:2])




def is_direct_broker(fname):
     for i in controls.direct_brokers:
        if i.lower() in fname:
            print(i+"  direct broker")
            return True
     return False





async def tel_mainy():
    old_message=int(read_first_line('./cntrfiles/equityrr.txt').strip())

    companies=[]
    channel_entity=await client.get_entity('@equitybooksaurresearchreport')
    messages = await client.get_messages(channel_entity) # Get the last 10 messages
    new_message_id=messages[0].id
    if new_message_id==old_message:
        return
    for message in messages:
     if message.id ==old_message:
        write_first_line('./cntrfiles/equityrr.txt',str(new_message_id))
        return 
     try:
      if message.media:
       if isinstance(message.media, MessageMediaDocument):
         fname1=message.media.document.attributes[0].file_name
         fname=preprocessName(fname1)
         rep_date=message.date.date()
         u=classify_reports(fname)
         logger.info("File  %s is of type %s , MessageId %s",fname,u,message.id)
         if u=="compbrok":
            dnld,broker,company=get_company_and_dnld_status(fname)
            if dnld:
              logger.info ("To be downloaded %s",fname)
              await client.download_media(message, file="/tmp/comp.pdf")
           #   process_and_upload(fname1,broker,company,date)
              return
         if u=="Others" or u=="sector" or  u=="thematic":
           logger.info ("To be downloaded %s",fname)
           await client.download_media(message, file="/tmp/sector.pdf")
           upload_and_update_sector(fname1,rep_date,fname) 
     except Exception as e:
         print(f"Unexpected error: {type(e).__name__}: {e} - Skipping this message")
         print (message)
        

def tel_main():
 loop = asyncio.get_event_loop()
 loop.run_until_complete(tel_mainy())
