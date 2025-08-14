import contvar
import logging
logger = logging.getLogger(__name__)

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
