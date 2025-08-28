#from mcontrol import main_mc 
import sys
sys.path.append("stockutils")
from raxis import axis_main
from geojit import geojit_main
from idb import idbi_main
import logging
logger = logging.getLogger(__name__)
#reports=["geojit"]
reports=["raxis","geojit","idbi"]
def initialize_logger ():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename='/tmp/myapp.log', level=logging.INFO)
    logger.info('Started Logging from Axmain ')
def add():
  initialize_logger()
  if "geojit" in reports:
    geojit_main()
  if "raxis" in reports:
      axis_main()
  if "idbi" in reports:
      idbi_main()
add()
