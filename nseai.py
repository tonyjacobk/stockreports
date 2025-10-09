#from mcontrol import main_mc 
import sys
sys.path.append("stockutils")
from stockutils import nse,coddb
from stockutils import db,check_company_with_the_key
from nsecodeagent import call_agent
import json
import logging
logger = logging.getLogger(__name__)


def initialize_logger ():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename='/tmp/myapp.log', level=logging.INFO)
    logger.info('Started Logging from main ')


def clean_and_convert(text: str):
    # Split into lines
    lines = text.strip().splitlines()
    
    # Remove first and last line
    cleaned_lines = lines[1:-1]
    
    # Join back into a string
    cleaned_text = "\n".join(cleaned_lines)
    
    # Convert to JSON
    return json.loads(cleaned_text)



def get_codes_and_company():
  p=db.find_no_code().strip(',')
  logger.info("Found  %s with out code",p)
  if len(p) < 1:
     return 
  u1= call_agent(p)
  print("*************************************************************************************************")
  print( u1)
  u=clean_and_convert(u1)
  for i in u:
    if i["Code"] =="":
      continue
    c=coddb.get_comp(i["Code"])
    if (c):
        print("Already present in DB",i["Code"])
        print(c)
        db.update_name_and_code(i["Name"],c["company"],i["Code"])
        continue
    ret,val=check_company_with_the_key(i["Code"])
    print (ret,val)
    if ret ==0:
        coddb.insert_into_codedb(val[0]['symbol_info'],val[0]['symbol'])
        db.update_name_and_code(i["Name"],val[0]['symbol_info'],val[0]['symbol'])



get_codes_and_company()
