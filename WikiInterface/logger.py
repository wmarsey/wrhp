import logging, inspect
import logging.handlers
from datetime import datetime
from consts import *

DEBUGFILE = BASEPATH + '/debug.log'
INFOFILE = BASEPATH + '/info.log'

dlogger = logging.getLogger('dlogger')
ilogger = logging.getLogger('ilogger')

logging.basicConfig(filename=DEBUGFILE,
                    level=logging.DEBUG, format="%(asctime)-15s %(message)s")
logging.basicConfig(filename=INFOFILE,
                    level=logging.INFO, format="%(asctime)-15s %(message)s")

dhandler = logging.handlers.RotatingFileHandler(
              DEBUGFILE, maxBytes=1000000, backupCount=5)
ihandler = logging.handlers.RotatingFileHandler(
              INFOFILE, maxBytes=1000000, backupCount=5)

dlogger.addHandler(dhandler)
ilogger.addHandler(ihandler)

dlogger.setLevel(logging.DEBUG) 
ilogger.setLevel(logging.DEBUG)

def _string(*strings):
    return " ".join([str(s) for s in strings])

def logDebug(*strings):
    #deal with strings
    string = _string(strings)

    #who has me?
    cframe = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    
    #log
    dlogger.debug(cframe + ":" + string)

def logInfo(*string):
    #deal with strings
    string = _string(strings)

    #who has me?
    cframe = inspect.getouterframes(inspect.currentframe(), 2)[1][3]

    #compile message
    ilogger.info(cframe + ":" + string)

def revidLog(title, pageid, domain):
    import database as db
    d = db.Database()
    
    ilogger.info("CALC SUMMARY FOR " + ", ".join([str(title),str(pageid),str(domain)]))
    weights = d.getrevidlog(pageid, domain)
    for w in weights:
        ilogger.info(" ")
        ilogger.info("-----" + str(w[:1]) + " / " + str(w[-1]) + "-----")
        ilogger.info(w[2:-2])
        ilogger.info(" TOTAL " + str(w[-2]))
    ilogger.info(" ")
    ilogger.info("END-----------------------------------")
    ilogger.info(" ")
