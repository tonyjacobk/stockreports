import requests
from typing import Tuple,List,Dict,Optional
from .nse_utils import nse
import re
def choose_only_equity_instruments(datalist):
      filtered_list = []
      for entry in datalist:
        # Check if it's an equity entry
        if entry.get('result_sub_type') == 'equity':
            symbol_info = entry.get('symbol_info', '').lower()
            # Exclude if it's a Mutual Fund or ETF
            if 'mutual fund' not in symbol_info and 'etf' not in symbol_info:
                filtered_list.append(entry)
      return filtered_list

   
def remove_PP_and_RE(data):
    # Create a set of all symbols for quick lookup
     all_symbols = {item['symbol'] for item in data}
    
    # Identify symbols that should be removed
     symbols_to_remove = set()
    
    # Step 1 & 2: Find all symbols ending in -RE or PP and determine their base symbols
     for item in data:
        symbol = item['symbol']
        base_symbol = None
        
        if symbol.endswith('-RE'):
            base_symbol = symbol.replace('-RE', '')
        elif symbol.endswith('PP'):
            base_symbol = symbol.replace('PP', '')
            
        # Step 3: If a base symbol exists in the original list, add the full symbol to the removal set
        if base_symbol and base_symbol in all_symbols:
            symbols_to_remove.add(symbol)
            
    # Step 4: Build a new list containing only the items that are not in the removal set
     filtered_data = [item for item in data if item['symbol'] not in symbols_to_remove]
    
     return filtered_data
def remove_inactive_symbols(symbol_data):
      return [item for item in symbol_data if item['activeSeries']]
    


def extended_tests(symbols: List[Dict]) -> Optional[Dict]:
      if not symbols:
        return None
      symbols=choose_only_equity_instruments(symbols)
      print ("After Equity",symbols)
      if not symbols:
        return None
      if len(symbols) == 1:
        return symbols
      symbols=remove_inactive_symbols(symbols)
      print ("removed Inactive",symbols)
      if not symbols:
        return None
      if len(symbols) == 1:
        return symbols
      symbols=remove_PP_and_RE(symbols)
      print ("PP RE Removed",symbols)
      if not symbols:
        return None
      if len(symbols) == 1:
        return symbols
      return symbols               
 


def process_list(clist,company):
    if not clist:
           return -1,None
    if len(clist)==1 :
      ret,val=is_this_same_company(company,clist[0]['symbol_info'])
      if ret:
          return 0,clist
      return -1,None
    new_list=[]
    for item in clist:
        ret,val=is_this_same_company(company,item['symbol_info'])
        print ( ret,val,company,item['symbol_info'],"same comp")
        if ret:
            new_list.append(item)
    print (new_list,"Search over")        
    if not new_list:
        return -1,None
    if len(new_list) ==1:
        return 0,new_list

    return 1,new_list

     
def is_this_same_company(from_report,from_nse):
      print ("In is_this_same_company")
      report_cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', from_report).lower()
      nse_cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', from_nse).lower()
    # 2. Split the cleaned strings into lists based on spaces
      report_list = report_cleaned.split()
      nse_list = nse_cleaned.split()

    # 3. Remove 'the' from both lists
      report_list = [word for word in report_list if word != 'the']
      nse_list = [word for word in nse_list if word != 'the']
      print ("Report list",report_list)
      print("nse_list",nse_list)
      if len(report_list) > len(nse_list):
        return False ,""
      results = []
      all_match = True
      for i in range(len(report_list)):
        is_substring = report_list[i] in  nse_list[i]
        results.append((report_list[i], nse_list[i], is_substring))
        if not is_substring:
            all_match = False

      return all_match, results

def find_best_match(nse_list):
      smallest=[]
      small_len=100 ## A big number ##
      for item in nse_list:
        nse_name=item['symbol_info']
        cleaned=re.sub(r'[^a-zA-Z0-9\s]', '', nse_name).lower()
        cleaned_list=cleaned.split()
        clist=[word for word in cleaned_list if word != 'the']
        print (len(clist),clist,small_len)
        if len(clist) == small_len:
            smallest.append(item)
        if len(clist) < small_len:
            smallest=[item]
            small_len=len(clist)
      return  smallest

def ask_for_help(text,best):
        print ("Confusion ",text ,best)

def expand_short_forms(raw_name: str) -> str:
    replacements = {
        'corpn': 'Corporation',
        'ltd': 'Limited',
        'amc': 'Asset Management Company',
        'sez': 'Special Economic Zone',
        'inds': 'Industries',
        'hind.': 'Hindustan ',
        'gsk':'GlaxoSmithKline',
        'intl.':'international',
        'natl.':'National',
        'engg.':'Engineering'
    }

    pattern = r'\b(corpn|ltd|amc|sez|inds|gsk)\b|(?i)hind\.|(?i)engg\.|(?i)intl\.|(?i)natl\.'

    return re.sub(
        pattern,
        lambda m: replacements.get(m.group().lower(), m.group()),
        raw_name,
        flags=re.IGNORECASE
    )






def preprocess_text(raw_name):
  raw_name=expand_short_forms(raw_name)
    # Remove leading 'the ' (case-insensitive) and replace with space
  raw_name = re.sub(r'^the\s+', ' ', raw_name, flags=re.IGNORECASE)
    # Remove all other occurrences of 'the ' and replace with space
  raw_name = re.sub(r'\sthe\s+', ' ', raw_name, flags=re.IGNORECASE)
  raw_name = raw_name.replace("."," ") 
  raw_name=re.sub(r'[^a-zA-Z0-9 ]', '', raw_name)
  raw_name=re.sub(r'\s+', ' ', raw_name).strip() ## multi space removal
  return(raw_name)

def remove_unwanted_keys(original_list):
 new_list = [
    {key: value for key, value in d.items() if key in {"symbol", "symbol_info"}}
    for d in original_list
]
 return new_list

def preprocess_list(comp_list):
    for i in comp_list:
        i["symbol_info"]=preprocess_text(i["symbol_info"])
    return (comp_list)



def new_search(text: str):
       text=preprocess_text(text)
       print ("Preprocessed Input:", text)
       start_word = text.split()[0]
       if len(start_word) < 2:
           start_word= start_word+text.split()[1]
       complist=nse.get_companies(start_word)
       print ("from NSE",complist)
       if len(complist)==0:
         return -1,[]
       complist=extended_tests(complist)
       print("After extended tests",complist)
       if  not complist:
         return -1,[]
       complist=remove_unwanted_keys(complist)
       print ("After remove_unwanted keys",complist)
       complist=preprocess_list(complist)
       print("After pre processing",complist)
       ret,val=process_list(complist,text)
       print("After process_list",val)       
       if ret == -1:
           return -1,[]
       if ret==0:
           return 0,val
       best=find_best_match(val)
       print ("Best",best)
       if len(best) ==1:
           return 0,best
       ask_for_help(text,best)
       return 1,best
