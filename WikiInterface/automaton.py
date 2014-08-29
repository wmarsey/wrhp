from __future__ import division ##for float-returning divisor
import sys,os#, errno
import re
#import sys
#import math as m
#from wikipedia import search
from dataplotter import Plotter
#from interface import WikiAnalyser
from interactiveplotter import IPlot 
from consts import *
import datetime
from copy import copy

def print_help():
    with open("../README", "r") as helpfile:
        print helpfile.read()

##PRINTS OUT DICTIONARY
## ### NEED TO ADD CONDITIONALS ACCORDING TO FLAGS
def echo_params(flags, params):
    print "---- PARAMETERS ----"
    for key, val in flags.iteritems():
        if val:
            print "mode:\t\t", key
    for key, val in params.iteritems():
        print key, ":\t", val

def intstring(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

##HANDLES COMMAND-LINE ARGUMENTS
def _arg_sanity(params):
    a = sys.argv[1:]
    foptions = [('--domain','domain',False),
                ('--pageid','pageid',True),
                ('--newrevid','newrevid',True),
                ('--oldrevid','oldrevid',True),
                ('--title','title',False),
                ('--scrapemin', 'scrapemin',True),
                ('--username', 'user',False),
                ('--plotpath', 'plotpath',False)]
    if "--help" in a:
        print_help()
        return None
    if "--version" in a:
        print "Version:", VERSION_NUMBER
        return None
    for o in foptions:
        if o[0] in a:
            val = a[a.index(o[0]) + 1]
            if o[2]:
                val = int(val)
            print "setting parameter", o[1], "=", val
            params[o[1]] = val
            a.pop(a.index(o[0]) + 1)
            a.pop(a.index(o[0]))
        
    return params

def _flag_sanity(flags):
    foptions = [('s','scrape'),
                ('p', 'plot'),
                ('i', 'iplot'),
                ('v', 'launch'),
                ('r', 'dbrepair')]

    for arg in sys.argv:
        if re.search("^-[A-Za-z]$", arg):
            for ch in arg[1:]:
                for o in foptions:
                    if ch == o[0]:
                        print "setting flag", o[1]
                        flags[o[1]] = True
        if arg == "--trundle":
            flags['trundle'] = True

    return flags

def _config_check(params, flags):
    if (params['title'] or params['pageid'] or params['user'] \
            or params['revid'] or params['oldrevid']) \
            and not params['domain']:
        print "With these arguments you must supply a domain."
        return False
    
    if (params['title'] or params['pageid'] or flags['launch']) and flags['trundle']:
        print "-t argument is incompatible here."
        return False
        
    if (params['revid'] or params['oldrevid'] or params['user']) and not flags['view']:
        print "--revid, --oldrevid or --username params only used with -v option."
        return False
    
    return True
 
def main():
    params = {'title': None,
              'revid': 0,
              'userid': 0,
              'domain':None,
              'weights':None, ##need a better solution for this
              'user':None,
              'oldrevid':None,
              'pageid':None,
              'revid':None,
              'scrapemin':50,
              'plotpath':None}
    flags = {'scrape': False,
             'trundle':False,
             'view':False,
             'plot':False,
             'iplot':False,
             'launch':False,
             'dbrepair':False}

    params = _arg_sanity(params) ##ARGUMENT HANDLING
    if not params:
        sys.exit(-1)
    flags = _flag_sanity(flags) ##FLAG SANITY
    if not _config_check(params, flags):
        sys.exit(-1)
    
    if flags['launch']:
       import launch
       wl = launch.WikiLaunch()
       #print "---------------VIEW MODE---------------"
       if params['revid']:
           if params['oldrevid']:
               wl.showdiff(params['oldrevid'], 
                           params['revid'], 
                           params['domain'])
           else:
               wl.shorev(params['revid'], 
                         params['domain'])
       elif params['pageid']:
           wl.showpage(params['pageid'], 
                       params['domain'])
       else:
           wl.showuser(params['user'],
                       params['domain'])
       sys.exit()

    import wikiScraper as wk
    from interface import WikiAnalyser
    if flags['dbrepair']:
        dbrepair()
        sys.exit(0)

    while True:
        while True:
            print "---------FETCHING WIKIPEDIA PAGE------------"
            scraper = wk.WikiRevisionScrape(title=params['title'],
                                            domain=params['domain'],
                                            scrapemin=params['scrapemin'])
            title, pageid, domain = scraper.scrape()
            
            if title and pageid and domain:
                break
            elif (params['title'] or params['pageid']):
                sys.exit(-1) ##if you asked but didnt get. terminate
                             ##instead of trying again
    
        print
        print "-----------------ANALYSING------------------"    
        analyser = WikiAnalyser(title,pageid,domain)
        results = analyser.analyse()
        if not results:
            sys.exit(-1)
        
        if flags['plot']:
            print
            print "--------------------PLOT--------------------"
            import dataplotter as dpl
            plotter = dpl.Plotter(os.path.abspath(params['plotpath']) if params['plotpath'] else None)
            plotted = plotter.plot(title, pageid, domain)
            print len(plotted), "plotted"

        if not flags['trundle']:
            break
    sys.exit(0)

def dbrepair():
    import database as db
    import wikiScraper as wk
    from interface import WikiAnalyser
    dtb = db.Database()
    fetch = dtb.getallfetched()
    
    piddoms = dtb.getallscraped()

    print "Checking", len(piddoms), "pageids for complete details"

    for t in piddoms:
        scraper = wk.WikiRevisionScrape(pageid=t[0],
                                        domain=t[1],
                                        scrapemin=0)
        title, pageid, domain = scraper.scrape()

    print "Checking", len(fetch), "fetched entries for analyses"

    for f in fetch:
        analyser = WikiAnalyser(*f)
        results = analyser.analyse()
        if not results:
            sys.exit(-1)
        

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nKeyboard Interrupt"
        sys.exit(0)
