import contvar
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
brk_dict={"IDBI":"./cntrfiles/idbi.txt","Axis":"./cntrfiles/axis.txt","geojit":"./cntrfiles/geojit.txt"}

def read_first_line(filename):
    try:
        with open(filename, 'r') as file:
            first_line = file.readline()
        return first_line
    except FileNotFoundError:
        return f"The file {filename} does not exist."
    except Exception as e:
        return f"An error occurred: {e}"

def write_first_line(filename, text):
    if contvar.testruncn==1:
        logger.info("testruncn=1,Not saving ..")
        return
    try:
        with open(filename, 'w') as file:
            file.write(text + '\n')
        return f"The file {filename} has been created with the first line as '{text}'."
    except Exception as e:
        return f"An error occurred: {e}"

def get_last_report_date(brokerName):
 start_date_stri=read_first_line(brk_dict[brokerName]).strip()
 logger.info ("Mail: %s Searching for reports newer than %s ", brokerName,start_date_stri)
 start_date= datetime.strptime(start_date_stri,"%B %d, %Y").date()
 return(start_date)

def update_last_report_date(brk,idate):
  write_first_line(brk_dict[brk],idate.strftime('%B %d, %Y'))

