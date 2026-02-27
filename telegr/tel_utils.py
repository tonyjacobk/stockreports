from cntrfiles import controls
from stockutils import get_comp_code
import json
import re
import ast
def find_broker_from_fileName( fname):
    for key, value in controls.brokers.items():
        if  key.lower() in fname.lower():
            return value

    return None

def get_company_name_from_on_fileNames(fileName):
    pattern = re.compile(
        r'\b(?:report|notes?|update)\s+on\s+(\w+)\s+(\w+)',
        re.IGNORECASE
    )

    match = pattern.search(fileName)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return None


def get_broker_and_company_for_on_reports(fileName):
 fileName=preprocessName(fileName)
 broker =find_broker_from_fileName(fileName)
 if not broker :
     return None,None
 company =get_company_name_from_on_fileNames(fileName)
 if not company:
     return None,None
 return company,broker


def get_broker_part_from_fileName(fname):
    for key, value in controls.brokers.items():
        if key.lower() in fname.lower():
            return key

    return None

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

def modify_with_correct_broker_and_nsecodes(clist):
 for i in range(len(clist)):
  print(clist[i])
  get_correct_broker_and_nsecode(clist[i])
 return(clist)

def clean_and_convert(text: str):
   try:
    lines = text.strip().splitlines()
    cleaned_lines = lines[1:-1]
    cleaned_text = "\n".join(cleaned_lines)
    json_text=json.loads(cleaned_text)
    return json_text
   except:
    return None

def get_first_two_words(text):
    print("Two words",text)
    if not isinstance(text, str) or not text.strip():
        return ""

    words = text.replace('_', ' ').split()
    if len(words) ==1 :
        return(words[0])
    return ' '.join(words[:2])


def extract_broker_and_company_compbrok(name):
     print ("file name is ",name)
     name=preprocessName(name)
     comp={}
     init_pattern = re.compile(r'^(.+?)Initiating Coverage on(.+)$',re.IGNORECASE)
     sees_pattern = re.compile(r'^(.+?)sees \d+%? (?:UP|DOWN)SIDE in(.+)$',re.IGNORECASE)

     init_match = init_pattern.match(name)
     if init_match:
       cleaned=get_first_two_words( init_match.group(2).strip("-"))
       print("Cleaned",cleaned)
       comp= {
                        'broker': init_match.group(1).strip(),
                        'company':cleaned,
                    }
       return  comp['company'],comp['broker']
                # Check for sees_X%_UPSIDE_in pattern
     sees_match = sees_pattern.match(name)
     print("sees matched",sees_match)
     if sees_match:
          comp={ 'broker': sees_match.group(1).strip(),
                 'company':get_first_two_words( sees_match.group(2).strip("_")),
               }

          print("compp is ",comp)
          return   comp['company'],comp['broker']
     return None,None

def extract_broker_and_company_compres(name):
  brk=get_broker_part_from_fileName(name)
  cleaned=clean_result_update_file(name,brk)
  comp=" ".join(cleaned.split()[:2])
  return comp,brk
   


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


def remove_duplicate_files(data):
    from collections import defaultdict

    # Track occurrences per filename (list of indices)
    filename_indices = defaultdict(list)
    for idx, item in enumerate(data):
        filename_indices[item["fileName"]].append(idx)

    # Collect indices to remove: the *second* occurrence (i.e., index 1 in the list) if it exists
    to_remove = set()
    for indices in filename_indices.values():
        if len(indices) >= 2:
            # Remove only the *second* occurrence (indices[1])
            to_remove.add(indices[1])

    # Build result: keep items whose index is NOT in to_remove
    result = [item for idx, item in enumerate(data) if idx not in to_remove]
    return result

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


def write_messids_to_file_json(data_list):
    try:
        with open("messid.txt", 'w') as file:
            json.dump(data_list, file)
        print(f"Successfully wrote messidlist list to ")
    except IOError as e:
        print(f"Error writing messid list to file")

def read_messids_from_file_json(mylist):
    try:
        with open("messid.txt", 'r') as file:
            mylist = json.load(file)
        print(f"Successfully read messageid list ",len(mylist))
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading file: {e}")
        mylist=[]



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



def remove_already_processed_ids(messids,idlist):
    ids_to_remove = set(idlist)
    L3 = [entry for entry in messids if entry['messid'] not in ids_to_remove]
    return L3
k,l=extract_broker_and_company_compbrok("PL Capital sees 5 DOWNSIDE in Tata Elxsi-.pdf")
print(k,l)
