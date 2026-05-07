from cntrfiles import controls
from stockutils import get_comp_code,db,MegaMan
import json
import contvar
import re
import ast
import logging
logger = logging.getLogger(__name__)

def find_broker_from_fileName( fname):
    for key, value in controls.brokers.items():
        if  key.lower() in fname.lower():
            return value

    return None

def find_broker_from_text( text):
    for key, value in controls.brokers.items():
        if " "+ key.lower() in text.lower():
            return value

    return None



def get_broker_key_from_broker_Name(brkNam):
  #  key = next(k for k, v in controls.brokers.items() if v == brkNam)
    for key, value in controls.brokers.items():
        if " "+value.lower()+" " in brkNam.lower():
            return key

def is_direct_broker(fname):
     for i in controls.direct_brokers:
        if i.lower() in fname:
            print(i+"  direct broker")
            return True
     return False


def preprocessName(fname):
     # Replace _ and + with single space
    processed = fname.replace('_', ' ').replace('+', ' ')

    # Replace multiple spaces with single space
    processed = re.sub(r'\s+', ' ', processed)
    processed=processed.removesuffix(".pdf")
    pattern = r'(\s*\(\d+\))+$'
    x= re.sub(pattern.strip(), '', processed)
    return(x)


def remove_dates_and_quarters(text):
    patterns = [
        r'(?<!\d)\d{8}(?!\d)',                               # 20251105
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',                # 05/11/2025 etc
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',                  # 2025-11-05
        r'(?<!\d)\d{6}(?!\d)',                               # 260211 (YYMMDD) 
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{1,2}\s?\d{2,4}\b',
        r'\b\d{1,2}\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{2,4}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{2}\b',
        r'\b(?:[1-4]Q|Q[1-4])\s*FY\s*\d{2,4}\b',             # 1Q FY25
        r'\bFY\s*\d{2,4}\b',                                 # FY25
    ]

    combined = re.compile("|".join(patterns), re.IGNORECASE)

    found = combined.findall(text)
    cleaned = combined.sub(" ", text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned, found

def get_correct_nse_code(comp):
 comp,code=get_comp_code(comp)
 return comp,code

def get_correct_broker_and_nsecode(dict_row):
  dict_row["cf"]=dict_row["bf"]=dict_row["valid"]=False
  if dict_row['company'] and dict_row['company']!="None" :
   comp,code=get_comp_code(dict_row['company'])
   if code:
       dict_row["cf"]=True
   dict_row['company']=comp
   dict_row["code"]=code
  if dict_row['broker'] and dict_row["broker"] != "None":
     broker=find_broker_from_fileName(dict_row["broker"])
     if broker:
        dict_row['broker']=broker
        dict_row["bf"]=True
  if dict_row["bf"] and dict_row["cf"]:
     dict_row["valid"]=True


def get_correct_broker_and_nsecode_others(mylist,dict_row):
  print("Mylist ",mylist)
  dict_row["cf"]=dict_row["bf"]=dict_row["valid"]=False
  for i in mylist:
     print( "Element",i)
     broker=find_broker_from_fileName(i)
     print("Found broker",broker)
     if broker:
        dict_row['broker']=broker
        dict_row["bf"]=True
        code=get_broker_key_from_broker_Name(broker)
        print(code, "Brk code")
        if code:
          j=i.lower().split(code.lower())
          print(j)
          mylist.extend(j)
          print(mylist,"Mylist after extension")
          mylist.remove(i)
          print(mylist,"Mylist after removal")
          mylist=[item for item in mylist if item != " "]
          print(mylist)
  for i in mylist:
     if i.strip()=="":
        continue
     comp,code=get_comp_code(i.strip())
     if code !="":
      dict_row['company']=comp
      dict_row["code"]=code
      dict_row["cf"]=True
      break
   

  return dict_row




def extract_target_price_and_recomm(text):
    broker=""
    tp=extract_target_price(text)
    recomm=extract_recommendation(text)
    return tp,recomm

   


def extract_target_price(text):
 pattern = re.compile(
    r"""(?ix)
    \b(?:TP|Target\s+Price)\b         # TP or Target Price
    \s*
    (?:to\s+)?                        # allow 'to'
    (?:[:\-–—]\s*)?
    (?:of\s+)?                        # allow 'of'
    (?:[:\-–—]\s*)?
    (?:(Rs\.?|INR|₹))?\s*             # currency optional (allow attached)
    ((?:\d{1,3}(?:,\s?\d{3})*|\d+))      # capture number with or without commas
    """
 )
 m = pattern.search(text)
 if m:
   return re.sub(r"[ ,]","",m.group(2))
 else:
   return ""

def extract_recommendation(text):

# All supported ratings
 RATINGS = [
    "buy", "sell", "reduce", "hold",
    "accumulate", "neutral", "initiating coverage"
]

# Build alternation pattern (longest first to avoid partial matches)
 ratings_pattern = r"|".join(
    fr"{r}" for r in sorted(RATINGS, key=len, reverse=True)
)

# Pattern 1: Upgrade/Downgrade/Reiterate → extract NEW rating only
 upgrade_pattern = re.compile(
    fr"""(?ix)
        (?:upgrade[d]?|downgrade[d]?|reiterate[d]?)   # action
        \s+to\s+
        (?P<new>{ratings_pattern})                    # NEW rating
    """
)

# Pattern 2: Direct rating lines such as "Rating: BUY", "Rating – Hold"
 direct_pattern = re.compile(
    fr"""(?ix)
        (?:
            rating\s*[:\-–—]?\s*(?P<rate1>{ratings_pattern})      # Rating: BUY
            |
            (?P<rate2>{ratings_pattern})\s+rating                 # BUY rating
            |
            (?:maintain|maintains|maintained
              |retain|retains|retained
              |reiterate|reiterates|reiterated
              |reaffirm|reaffirms|reaffirmed)
            \s+(?:a\s+)?(?P<rate3>{ratings_pattern})              # maintain HOLD / maintain a BUY
        )
    """
)


    # 1. Check upgrade/downgrade type
 m1 = upgrade_pattern.search(text)
 if m1:
        return m1.group("new").upper()

    # 2. Check direct rating
 m2 = direct_pattern.search(text)
 if m2:
  for key in ("rate1", "rate2", "rate3"):
            if m2.group(key):
                return m2.group(key).upper()
 return None



def clean_result_update_file(inputfile,brk):
  cleaned = re.sub(r'[^A-Za-z0-9]', ' ', inputfile)
  inputfile = re.sub(r'\s+', ' ', cleaned).strip()
  inputfile,x=remove_dates_and_quarters(inputfile)
  cleaned = re.sub(r'\b(RU|IC)\b', ' ', inputfile, flags=re.IGNORECASE)
  cleaned = re.sub(r'\s+', ' ', cleaned).strip()
  cleaned = re.sub(r'\b(results?|updates?)\b', ' ', cleaned, flags=re.IGNORECASE)
    # Remove extra spaces
  cleaned = re.sub(r'\s+', ' ', cleaned).strip()
  cleaned=re.sub(r'\b(The|pdf)\b', ' ',cleaned,flags=re.IGNORECASE)
  if brk:
     cleaned = re.sub(re.escape(brk), "", cleaned, flags=re.IGNORECASE).strip()
  return cleaned





def write_dicts_to_file(data,filename):
    """Write a list of dictionaries to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
def write_text_to_file(pdftext,filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read().strip()
        existing_list = ast.literal_eval(content) if content else []

    # Append new list
    existing_list.extend(pdftext)

    # Save back to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(repr(existing_list))

def read_dicts_from_file(filename):
    """Read a list of dictionaries from a JSON file."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)





def add_to_db(dbtype,row):
     print("add to db",dbtype,row)
     if contvar.testtele==1:
      logger.info("Test tele enabled ..Not adding to DB Returning")
      return
     if dbtype=="comp":
          print(" My add to db Comp",dbtype,row)
          db.insert_into_database([row],'tel')
     else:

         print("Adding sector file")
         db.insert_into_sector(row)

def upload_mega_file(fname):
   link="http://mydummyfile.com"
   if contvar.testtele==1:
       pass
   else:
       link=MegaMan.upload_file(fname)
   return link

