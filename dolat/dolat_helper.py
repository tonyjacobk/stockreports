import re
from stockutils import get_target_and_recomm

def extract_dolat_report_name(url):
    pattern = r"^https://www\.dolatresearch\.com/Attachment/__Page/(.*?)\(Q[1-4]FY\d{2}(?:%20|\s)Result(?:%20|\s)Update\).*"
    match = re.match(pattern, url)
    if match:
        # group(1) refers to the content inside the first set of parentheses (.*?)
        return match.group(1).replace('%20', ' ').strip().strip('-').strip()
    else:
        return "XAXXY"
def get_report_details(report_list):
 count=0
 for i in report_list:
  comp=extract_dolat_report_name(i['link'])
  report_list[count]['Company']=comp
  count=count+1


