import re
from typing import Optional
from .tel_utils import get_comp_code 
from pypdf import PdfReader
import fitz

def extract_meta_data(file_path):
  try:
   reader = PdfReader(file_path)
   meta = reader.metadata
   return meta
  except exception as e:
   print("Could not extract meta data")
   return None


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
    if match :
        return 1,match.group(1).strip()
    ret,val=get_company_from_Nuvama_metadata()
    print("After Nuvama meta ",ret,val)
    if not ret:
        return None,None
    return ret,val
    


def get_company_from_Nuvama_metadata():
    print("In meta")
    meta=extract_meta_data('/tmp/comp.pdf')
    print("Meta is ",meta)
    try:
      title = meta.get("/Title")
      if not title:
        return None, None
    except  Exception as e:
        return None,None 
    title = title.strip()
    if re.search(r"\bSU\b", title, re.IGNORECASE):
        return 2, title
    m = re.match(r"^(.*?)\s+IN\s+EQUITY\b", title, re.IGNORECASE)
    if m:
        return 1, m.group(1).strip().title()

    return None, None


def get_lines_from_pdfFile(line_numbers,fname):   #using mfitz
    result = []

    with fitz.open(fname) as doc:
        if not doc:
            return result

        page = doc[0]
        flags = fitz.TEXT_DEHYPHENATE | fitz.TEXT_PRESERVE_WHITESPACE
        text = page.get_text("text", flags=flags, sort=True)

        non_empty_lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        for line_number in line_numbers:
            if 1 <= line_number <= len(non_empty_lines):
                result.append(non_empty_lines[line_number - 1])

    return result

def get_company_from_sharekhan(fname):
 lines=get_lines_from_pdfFile([1,2,3,4],fname)
 print(lines)
 return(lines[0]).strip()

def get_company_from_systamatix(fname):
 lines=get_lines_from_pdfFile([1,2,3],fname)
 print(lines)
 company=None
 if 'Systematix' not in lines[0]:
  return None
 if len(lines) > 2:
   m = re.search(r'\d{1,2} [A-Za-z]+ \d{4}', lines[2])
   if not m:
        return [s.strip()] if s.strip() else []

   part1 = lines[2][:m.start()].strip()
   part2 = lines[2][m.end():].strip()
   if part1 and part2:
    return None
   return part1+part2

def get_company_from_choice(fname):
 lines=get_lines_from_pdfFile([1,2,3],fname)
 company=None
 if 'Institutional Equities' in  lines[0] or 'Initiating Coverage'  in lines[0]:
  company=lines[1].split(':')[0]
  return company



def get_company_from_reports(broker,text):
 print("get_company_from_reports ",broker)
 company=comp=code=""
 if "Sharekhan" in broker:
  company=get_company_from_sharekhan('/tmp/comp.pdf')
 if "Systematix" in broker:
  company=get_company_from_systamatix('/tmp/comp.pdf')
 if "Choice" in broker:
  company=get_company_from_choice('/tmp/comp.pdf')

 if "Edelweiss" in broker:
  print("Report from Nuvama")
  typ, company=extract_company_nuvama(text)
  print("Company is ",company)
  if typ==2:
     return company,"sector"
  if not type:
     return None, None
 if not company:
     return None,None
 comp,code=get_comp_code(company)
 if code:
     return comp,code
 return company,None
