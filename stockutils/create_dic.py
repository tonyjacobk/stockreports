import re
name_dict={}
key_dict={}
from .ticker import preprocess_list,preprocess_text, new_search
from .codedb import coddb
import logging
logger = logging.getLogger(__name__)

def add_company_to_dict(name,key):
   first_word = name.split()[0].upper() if name else ''
   if first_word=="THE":
      first_word = name.split()[1].upper()
   if first_word:
                if first_word not in name_dict:
                    name_dict[first_word] = []
                name_dict[first_word].append([name, key])

def create_name_dictionary():
 key_dict=coddb.create_dictionary()
 print("Keys",len(key_dict.keys()))
 for key in key_dict.keys():
   name=key_dict[key]
   add_company_to_dict(name,key)   


def find_correct_company_from_list(raw_name,comp_list):
 for i in comp_list:
    i[0]=preprocess_text(i[0])
 print ("After preprocessing",comp_list)
 ss = raw_name.lower().split()  # Split `st` into words: ["hello", "world"]
 print (ss)
 print ("Comp list",comp_list) 
 # Find all x in ll where for each i, ss[i] is a substring of x[i]
 result = [
    x  for x in comp_list 
    if all(
        ss_i in x_i 
        for ss_i, x_i in zip(ss, x[0].lower().split())
    )
]

 return (result)

def combine_single_letters(input_str):
    parts = input_str.split()
    if not parts:
        return input_str

    # Check if the first part is a single letter
    if len(parts[0]) == 1 and parts[0].isalpha():
        combined = []
        i = 0
        # Keep combining while parts are single letters
        while i < len(parts) and len(parts[i]) == 1 and parts[i].isalpha():
            combined.append(parts[i])
            i += 1
        # If more than one single letter at the beginning, combine them
        if len(combined) > 1:
            return ''.join(combined) + (' ' + ' '.join(parts[i:]) if i < len(parts) else '')

    return input_str  # No combining needed



def misc_check_company(input_string):
    input_lower = input_string.lower()
    print("from misc check",input_lower) 
    if input_lower.startswith("j k cement"):
        return ["JK Cement Limited", "JKCEMENT"]
    elif input_lower.startswith("j kumar infra"):
        return ["J.Kumar Infraprojects Limited", "JKIL"]
    elif input_lower.startswith("heidelberg"):
        return ["HeidelbergCement India Limited","HEIDELBERG"]
    elif input_lower.startswith("macrotech devel"):
        return ["Lodha Developers Limited","LODHA"]
    elif input_lower.startswith("rural electrification"):
        return ["REC Limited", "RECLTD"]
    elif input_lower.startswith("mahindra and mahindra fin") or input_lower.startswith("mahindra fin") or input_lower.startswith("m&m fin") or input_lower.startswith("m & m fin") or input_lower.startswith("m and m fin") or  input_lower.startswith("m m fin"):
        return ["Mahindra & Mahindra Financial Services Limited", "M&MFIN"]
    elif input_lower in ["mahindra and mahindra", "m & m", "m and m"]:
        return ["Mahindra & Mahindra Limited", "M&M"]
    elif input_lower.startswith("dr reddys"):
        return["Dr.Reddy's Laboratories Limited","DRREDDY"]
    elif input_lower.startswith("dr lal path"):
        return["Dr. Lal Path Labs Ltd.","LALPATHLAB"]
    elif input_lower.startswith("gr infra"):
        return["G R Infraprojects Limited","GRINFRA"]
    elif input_lower.startswith("creditacc"):
        return ["CREDITACCESS GRAMEEN LIMITED","CREDITACC"]
    elif input_lower.startswith("j b chem"):
        return ["JB Chemicals & Pharmaceuticals Limited","JBCHEPHARM"]
    elif input_lower.startswith("v i p indus"):
        return ['VIP Industries Limited','VIPIND']
    elif input_lower.startswith("cpcl"):
        return ['Chennai Petroleum Corporation Limited',"CHENNPETRO"]
    elif input_lower.startswith("K E C"):
        return ['KEC International Limited',"KEC"]
    elif input_lower.startswith("hpcl"):
        return ['Hindustan Petroleum Corporation Limited',"HINDPETRO"]
    elif input_lower=="sbi":
        return ['State Bank of India',"SBIN"]
    else:
        return []



def find_company_easy(raw_name):
  print(raw_name ,"from find_company_asy")
  for i in key_dict.keys():
      print(i)
  name=key_dict.get(raw_name.strip()) # Checking if code is given in report instead of Name #
  u=key_dict.get("BPCL")
  print(u)
  if name:
      return 0, [name,raw_name]
  first_name=raw_name.strip().split()[0]
  print(first_name)
  name_list=name_dict.get(first_name.upper())
  if not name_list:
      print("Key not found")
      return -1,None
  if len(name_list)==0:
      return -1,None
  p=find_correct_company_from_list(raw_name,name_list)
  if len(p)==0:
       return -1,None
  if len(p) == 1:
   return 0,p[0]
  return 1,p


def find_company(raw_name):
 raw_name=preprocess_text(raw_name)
 ret,val=find_company_easy(raw_name)
 if ret!=-1:
     return ret,val
 val= misc_check_company(raw_name)
 print(val,"After Misc")
 if val:
     return 0,val
 else:
   new_name=combine_single_letters(raw_name)
   ret,val=find_company_easy(new_name)
   if ret==0:
     return 0,val
   else:
     val= misc_check_company(new_name)
     print(val,"After Misc2")
     if val:
       return 0,val
     else:
         return -1,[]
          
  

def get_comp_code(name):
 ret,val=find_company(name)
 if ret==0:
     return val
 if ret == -1:
   ret,val = new_search(name)
   if ret==0:
       logger.info("Mail:Added to codeDB %s  %s",val[0]['symbol_info'],val[0]['symbol'])
       coddb.insert_into_codedb( val[0]['symbol_info'],val[0]['symbol'])
       add_company_to_dict(val[0]['symbol_info'],val[0]['symbol'])
       return val[0]['symbol_info'],val[0]['symbol']
   else:
       logger.info("Mail:Could not find NSECode for %s",name)
       return name,''








create_name_dictionary()
