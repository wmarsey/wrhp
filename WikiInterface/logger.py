import logging, inspect
from datetime import datetime
from consts import *

logging.basicConfig(filename=BASEPATH + '/debug.log', filemode='w',
                    level=logging.DEBUG, format="%(asctime)-15s %(message)s")
logging.basicConfig(filename=BASEPATH + '/error.log', filemode='w',
                    level=logging.ERROR, format="%(asctime)-15s %(message)s")

def _string(*strings):
    return " ".join([str(s) for s in strings])

def logDebug(*strings):
    #deal with strings
    string = _string(strings)

    #who has me?
    cframe = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    
    #log
    logging.debug(cframe + ":" + string)

def logWarning(*string):
    #deal with strings
    string = _string(strings)

    #who has me?
    cframe = inspect.getouterframes(inspect.currentframe(), 2)[1][3]

    #compile message
    logging.info(cframe + ":" + string)
