#from mcontrol import main_mc 
import sys
sys.path.append("stockutils")

from bs import main_bs,scrape_bs
from mc import main_mc
from shareindia import share_main
from smifs import smifs_main
import logging
logger = logging.getLogger(__name__)
#reports=["smifs","mc","bs","share"]
reports=["smifs"]

def initialize_logger ():
    logging.basicConfig(filename='/tmp/myapp.log', level=logging.INFO)
    logger.info('Started Logging from main ')
def add():
  initialize_logger()
  if "mc" in reports:
    main_mc()
  if "bs" in reports:
    scrape_bs()
    main_bs()
  if "share" in reports:
      share_main()
  if "smifs" in reports:
      smifs_main()

add()
