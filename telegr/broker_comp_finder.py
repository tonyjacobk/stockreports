from .tel_utils import get_correct_broker_and_nsecode_others,get_correct_broker_and_nsecode,find_broker_from_fileName
import re
date_patterns = [
    r'(?<!\d)\d{8}(?!\d)',                               # 20251105
    r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',                # 05/11/2025 etc
    r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',                  # 2025-11-05
    r'(?<!\d)\d{6}(?!\d)',                               # 260211 (YYMMDD)
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{1,2}\s?\d{2,4}\b',
    r'\b\d{1,2}\s?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{2,4}\b',
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{2}\b',
    r'\b(?:[1-4]Q|Q[1-4])\s*FY\s*\d{2,4}\b',             # 1Q FY25
    r'\b\d{2}\s\d{2}\s\d{4}\b' ,                          # 02 03 2025
    r'\bFY\s*\d{2,4}\b',                                 # FY25
]


def get_broker_and_company(fname,mtype):
 comp_ds={"company":"","broker":"","code":""}
 if mtype=="Others":
   mylist=extract_broker_and_company_other(fname)
   print("From ***********get_broker_and_company list of words",mylist)
   get_correct_broker_and_nsecode_others(mylist,comp_ds)
   print("From ***********get_broker_and_company",comp_ds)
 else: 
   print("In else")
   funcdict={"compres":extract_broker_and_company_compres,"compbrok":extract_broker_and_company_compbrok,"onreport":get_broker_and_company_for_on_reports}
   comp_ds["company"],comp_ds["broker"] =funcdict[mtype](fname)
   get_correct_broker_and_nsecode(comp_ds)
 return comp_ds

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
# fileName=preprocessName(fileName)
 broker =find_broker_from_fileName(fileName)
 company =get_company_name_from_on_fileNames(fileName)
 if not company:
     return None,None
 return company,broker

def extract_broker_and_company_compbrok(name):
     print ("file name is ",name)
#     name=preprocessName(name)
     comp={}
     init_pattern = re.compile(r'^(.+?)Initiating Coverage on(.+)$',re.IGNORECASE)
     sees_pattern = re.compile(r'^(.+?)sees \d+%? (?:UP|DOWN)SIDE in(.+)$',re.IGNORECASE)

     init_match = init_pattern.match(name)
     if init_match:
       cleaned= init_match.group(2).strip("-")
       cleaned= " ".join(cleaned.split()[:2])
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
                  'company': " ".join(sees_match.group(2).strip("_").split()[0:2])
               }

          print("compp is ",comp)
          return   comp['company'],comp['broker']
     return None,None

def extract_broker_and_company_compres(name):
  print("In compres")
  brk=find_broker_from_fileName(name)
  print("broker", brk)
  cleaned=clean_result_update_file(name,brk)
  print(cleaned)
  comp=" ".join(cleaned.split()[:2])
  print(comp)
  return comp,brk

def remove_dates_and_quarters(text):
    print("In remove",text)
    combined = re.compile("|".join(date_patterns), re.IGNORECASE)
    found = combined.findall(text)
    cleaned = combined.sub(" ", text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned
def clean_result_update_file(inputfile,brk):
  print("clean_result_update_file",inputfile,brk)
  cleaned = re.sub(r'[^A-Za-z0-9]', ' ', inputfile)
  inputfile = re.sub(r'\s+', ' ', cleaned).strip()
  print(inputfile)
  inputfile=remove_dates_and_quarters(inputfile)
  print(inputfile)
  cleaned = re.sub(r'\b(RU|IC)\b', ' ', inputfile, flags=re.IGNORECASE)
  cleaned = re.sub(r'\s+', ' ', cleaned).strip()
  cleaned = re.sub(r'\b(results?|updates?)\b', ' ', cleaned, flags=re.IGNORECASE)
    # Remove extra spaces
  cleaned = re.sub(r'\s+', ' ', cleaned).strip()
  cleaned=re.sub(r'\b(The|pdf)\b', ' ',cleaned,flags=re.IGNORECASE)
  if brk:
     cleaned = re.sub(re.escape(brk), "", cleaned, flags=re.IGNORECASE).strip()
  return cleaned


def extract_broker_and_company_other(fname):
 print("in extractother")
 fname=x = re.sub(r'\s+', ' ', fname.replace('-', ' ')).strip() ## _ and + are already removed , removing - also
 phrases = [
    "Research Report",
    "Initiating Coverage",
    "short reasearch report",  # typo kept as given
    "IC",
    "Initiates coverage",
    "Event update",
    "company update",
    "Fundamental Analysis Report"
]
 phrase_pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, phrases)) + r')\b', re.IGNORECASE)

 date_pattern = re.compile("|".join(date_patterns), re.IGNORECASE)
 phrase_parts = phrase_pattern.split(fname)
 result = []
 for part in phrase_parts:
        part = part.strip()
        if not part:
            continue

        # Now split each part on dates
        last_end = 0
        for match in date_pattern.finditer(part):
            before = part[last_end:match.start()].strip()
            if before:
                result.append({"text": before })
            last_end = match.end()
        after = part[last_end:].strip()
        if after:
            result.append({"text": after})
 print ("After removing dates and strings",result)
 mylist=[mytext['text'] for mytext in result]
 cresult=[re.sub(r'[^a-zA-Z0-9 ]', ' ', text) for text in mylist]
 print(cresult)
 return cresult

