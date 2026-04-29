#from mcontrol import main_mc 
import sys
import asyncio
sys.path.append("stockutils")
sys.path.append("cntrfiles")
from cntrfiles import controls
from telegr import beat_morning 
import logging
logger = logging.getLogger(__name__)


def initialize_logger ():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',filename='/tmp/telg.log', level=logging.INFO)
    logger.info('Started Logging from main ')


initialize_logger()
beat_morning(False,None)
#beat_morning(True,50252,True)

