from __future__ import division ##for float-returning divisor
import sys#, errno
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
    a = copy(sys.argv[1:])
    foptions = [('--domain','domain'),
                ('--pageid','pageid'),
                ('--newrevid','newrevid'),
                ('--oldrevid','oldrevid'),
                ('--title','title'),
                ('--scrapemin', 'scrapemin'),
                ('--username', 'user')]
    if "--help" in a:
        print_help()
        return None
    if "--version" in a:
        print "Version:", VERSION_NUMBER
        return None
    for o in foptions:
        if o[0] in a:
            params[o[1]] = a[a.index(o[0]) + 1]
            a.pop(a.index(o[0]) + 1)
            a.pop(a.index(o[0]))
    if len(a):
        print "do not recognise arguments:" + ",".join(a)
        return None
    
    return params

def _flag_sanity(flags):
    foptions = [('s','scrape'),
                ('p', 'plot'),
                ('i', 'iplot'),
                ('v', 'launch')]

    for arg in sys.argv:
        if re.search("^-[A-Za-z]*$", arg):
            for ch in arg[1:]:
                for o in foptions:
                    if ch == o[0]:
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
              'scrapelim':50}
    flags = {'scrape': False,
             'trundle':False,
             'view':False,
             'plot':False,
             'iplot':False,
             'launch':False}

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
    while True:
        #print "---------------SCRAPE MODE---------------"
        scraper = wk.WikiRevisionScrape(title=params['title'],
                                        domain=params['domain'],
                                        scrapelim=params['scrapelim'])
        title, pageid, domain = scraper.scrape()
        sys.exit(0)
    
        analyser = WikiAnalyser(title,
                                pageid, 
                                domain)

        #print "---------------ANALYSE MODE---------------"    
        #results = analyser.analyse()
        # if flags['plotshow']:
        #     form = ['revid',
        #             'Maths',
        #             'Citations',
        #             'Files / Images168',
        #             'Links',
        #             'Structure',
        #             'Normal',
        #             'Gradient',
        #             'user',
        #             'trajectory',
        #             'timestamp']
        #     formresults = []
        #     for r in results:
        #         res = {}
        #         for i, f in enumerate(form):
        #             res.update({f:r[i]})
        #         formresults.append(res)                 
        #     IPlot(formresults)
        
        results = self.dtb.getresults(pageid, domain)

        if not flags['trundle']:
            break
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nKeyboard Interrupt"
        sys.exit(0)
