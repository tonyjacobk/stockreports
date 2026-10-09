import hashlib
import os
import ast
from datetime import datetime, timezone
from typing import Any, Dict, List,Optional

from supabase import create_client, Client
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)

# This explicitly loads the variables from your .env file into the system environment
load_dotenv() 
# -------------------------
# Configuration
# -------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")      # e.g. "https://xxxxx.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")      # anon or service_role key
TABLE_NAME = "Details"                # replace with your actual table name
print(SUPABASE_URL)

#supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# -------------------------
# Helpers
# -------------------------
class SupaClass:
 def __init__(self):
    self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
     
 def compute_hash_from_text(self,text: str) -> str:
    print("Compute Hash")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


 def _build_row(self,
         tid:int, publish_date: datetime,company:str,recommendation: str,target: str,text: str,link: str,broker: str,Deleted:bool,sector:bool,action:str
) -> Dict[str, Any]:
    if action=="Upsert":
        return {
                "id":tid,"publish_date": publish_date,"company": company,"Recommendation": recommendation,"Target": target,"link": link,"broker": broker,"Deleted": Deleted,"sector":sector,
         }
    if publish_date.tzinfo is None:
        publish_date = publish_date.replace(tzinfo=timezone.utc)
    text1=text.replace("\x00","")
    return {
            "id":tid,"publish_date": publish_date.isoformat(),"Recommendation": recommendation,"Target": target,"text": text1,"link": link,"broker": broker,"Deleted": False,"sector":sector ,"company":company,
        "Hash": self.compute_hash_from_text(text),
    }



 def upsert_report(self,
    id_value: int,
    publish_date: datetime,
    company:str,recommendation: str,target: str, link: str,broker: str,deleted:bool,sector:bool
) -> Dict[str, Any]:
    row = self._build_row(
       id_value, publish_date=publish_date,company=company, recommendation=recommendation,target=target,text=None,link=link,broker=broker,Deleted=deleted,sector=sector,action="Upsert")
    row["id"] = id_value
    response =self.supabase.table(TABLE_NAME).upsert(row, on_conflict="id").execute()
    return response.data[0] if response.data else {}


 def insert_report(self,
         tid:int,    publish_date: datetime,company:str, recommendation: str,target: str,text: str,link: str,broker: str,sector:bool =False,
) -> Dict[str, Any]:
    pub_date = datetime.strptime(publish_date, "%Y-%m-%d")
    print("From supa insert")
    print("From insert_report",sector,company)
    row = self._build_row(
        tid=tid,publish_date = pub_date,company=company,recommendation=recommendation,target=target,link=link,broker=broker,text=text,Deleted=False,sector=sector,action="insert"
    )
    print("Row is ",row)
    response = self.supabase.table(TABLE_NAME).insert(row).execute()
    return response.data[0] if response.data else {}



 def get_active_recommendations(self) -> List[Dict[str, Any]]:
    response = (self.supabase.table(TABLE_NAME).select("*").eq("row_deleted", False).execute())
    return response.data or []
 def get_reports_set_for_delete(self)-> List[Dict[str, Any]]:
    response = (self.supabase.table(TABLE_NAME).select("*").eq("row_deleted", False).eq("Deleted", True).execute())
    return response.data or []
 def get_reports_marked_as_sector(self)-> List[Dict[str, Any]]:
    response = (self.supabase.table(TABLE_NAME).select("*").eq("row_deleted", False).eq("sector", True).execute())
    return response.data or []
 def get_reports_marked_as_company(self)-> List[Dict[str, Any]]:
     response = (self.supabase.table(TABLE_NAME).select("*").eq("row_deleted", False).eq("sector", False).eq("Deleted", False).execute())
     return response.data or []
 def delete_logically_ids(self,idlist):
     response=(self.supabase.table(TABLE_NAME).update({"row_deleted": True}).in_("id",idlist ).execute())
     return response.data or []

 def delete_recommendation_by_id(self,id_value: int) -> Optional[Dict[str, Any]]:
    response = (self.supabase.table(TABLE_NAME).delete().eq("id", id_value).execute())
    return response.data[0] if response.data else None

 def text_exists_in_db(self,text: str,rtype="comp") -> bool:
    print("In supa text exists",len(text))
    print(text)
    hash_value = self.compute_hash_from_text(text)
    print(hash_value)
    response = (
        self.supabase.table(TABLE_NAME).select("text","id","company").eq("Hash", hash_value).execute())
    rows = response.data or []
    for row in rows:
        print("Saved row",len(row.get("text")))
        if row.get("text") == text:
         print("Texts are same")
         if rtype=="comp":
            return True,row['id'],None
         else:
            print("Text exists from sector")
            return True,row['company'],row['id']

    return False,None,None

 def replace_id(self,old_id: int, new_id: int) -> bool:
    if int(old_id) >= int(new_id):
     logger.info ("Not replacing Id as existing Id %s is newer than %s",old_id,new_id)
     return False
    response = (self.supabase.table(TABLE_NAME).select("*").eq("id", old_id).execute())
    rows = response.data or []
    if not rows:
        logger.info("No rows with id %s .. Replacement failed",old_id)
        return False  
    row = rows[0]
    new_row = {**row, "id": new_id}
    insert_response = (self.supabase.table(TABLE_NAME).insert(new_row).execute())
    if not insert_response.data:
        logger.error("Insertion Failed for %s",new_id)
        return False  
    delete_response = (self.supabase.table(TABLE_NAME).delete().eq("id", old_id).execute())
    return bool(delete_response.data)
 


 def read_data(self,file_path):
    """
    Reads a file containing a Python list of dictionaries
    and returns it as a Python object.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return ast.literal_eval(content) if content else []

sb=SupaClass()


if __name__ == "__main__":
  sb=SupaClass()
 # sb.update_all_rows_text_and_hash()
  text='Internet September 2026 Sector Report Travel Plaorms—Going Places Nuvama Institutional Equities Parth Ghiya PARTH.GHIYA@nuvama.com Vibhor Singhal VIBHOR.SINGHAL@nuvama.com INTERNET Nuvama Research is also available on www.nuvamaresearch.com, Bloomberg - NUVA, Thomson Reuters, and Factset Nuvama Institutional Equities Contents Executive Summary ................................................................................................. 2 Travel platforms – Going places .............................................................................. 4 Global Travel and Tourism Industry ........................................................................ 5 Trends in Hospitality Industry ................................................................................. 7 Emergence of Online Travel Agents ........................................................................ 9 Indian Travel Buyers’ Market ................................................................................ 10 Recommendations ................................................................................................ 11 Initiating Coverage TBO TEK .......................................................................................................... 13 The Story in Charts ......................................................................................... 15 Executive Summary ....................................................................................... 16 Business Overview ......................................................................................... 18 Investment Rationale .................................................................................... 20 Acquisitions ................................................................................................... 32 Financial Outlook ........................................................................................... 34 Valuations .........................................................'
 # a,b,c=sb.text_exists_in_db(text,"comp")
 # print(a,b,c)
  response = ( sb.supabase.table(TABLE_NAME).select("id,text").execute())
  for row in response.data:
    text_len = len(row["text"]) if row.get("text") else 0
    print(f"id={row['id']}, length={text_len}")
  """
  tabs=sb.read_data("../jikkatext")
  for i in tabs:
     print("Trying ",i["id"])
     response = (sb.supabase.table(TABLE_NAME).select("id", count="exact").eq("id", i["id"]).execute())
     if response.count > 0:
         print("Id is present",i["id"])
         continue
     print(i)
     sb.insert_report(i["id"],i["date"],"",i["recommendation"],i["target_price"],i["text"],i["link"],i["broker"])
  """
