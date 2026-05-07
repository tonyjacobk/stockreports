import re
from typing import Optional
from .tel_utils import get_comp_code 
def extract_company_nuvama(text: str) -> Optional[str]:
    print("extract_company_nuvama")
    pattern = re.compile(
        r"""
        india\ equity\ research
        .{0,50}?   # up to 50 chars before date

        \b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|
           May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|
           Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b
        \s+\d{1,2},\s+\d{4}

        (.{0,50}?)   # <-- capture ONLY text after date (max 50 chars)

        (?=company\ update|result\ update)
        """,
        re.IGNORECASE | re.DOTALL | re.VERBOSE
    )

    match = pattern.search(text)
    return match.group(1).strip() if match else None
def get_company_from_sharekhan(text):
    match = re.search(r'NSE code:\s*(\S+)', text)
    return match.group(1) if match else None

def get_company_from_reports(broker,text):
 print("in func")
 company=comp=code=""
 if "sharekhan" in broker:
  company=get_company_from_sharekhan(text)
 if "Edelweiss" in broker:
  print("here")
  company=extract_company_nuvama(text)
 print("Company is ",company)
 if company:
    comp,code=get_comp_code(company)
 if code:
     return comp,code
 return company,None
