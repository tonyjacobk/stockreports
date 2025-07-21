#from mcontrol import main_mc 
from bs import main_bs,scrape_bs
from mc import main_mc
from shareindia import share_main
import logging
import sys
sys.path.append("stockutils")
logger = logging.getLogger(__name__)
reports=["bs","mc"]
def initialize_logger ():
    logging.basicConfig(filename='/tmp/myapp.log', level=logging.INFO)
    logger.info('Started Logging')
def add():
  initialize_logger()
  if "mc" in reports:
    main_mc()
  if "bs" in reports:
    scrape_bs()
    main_bs()
  if "share" in reports:
      share_main()
add()
