import re
from stockutils import get_target_and_recomm


def extract_dolat_report_name(url):
    pattern = r"^https://www\.dolatresearch\.com/Attachment/__Page/(.*?)\s*\(.*\)"
    match = re.match(pattern, url)
    if match:
        return match.group(1).replace('%20', ' ').strip().strip('-').strip()
    else:
        return "XAXXY"



def get_report_details(report_list):
 count=0
 for i in report_list:
  comp=extract_dolat_report_name(i['link'])
  report_list[count]['Company']=comp
  count=count+1

    
