from __future__ import division ##for float-returning divisor
import errno
import re
import sys
import math as m
from wikipedia import search
from dataplotter import Plotter
from interface import WikiInterface
from interactiveplotter import IPlot 
from consts import *
import datetime

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
    a = sys.argv
    if "--help" in a:
        print_help()
        sys.exit(0)
    if "--version" in a:
        print "Version:", VERSION_NUMBER
        sys.exit(0)
    if "--scrape_limit" in a:
        slim = a[a.index("--scrape_limit") + 1]
        if intstring(slim) and int(slim) > 0:
            params["scrape_limit"] = int(slim)
        else:
            print "Scrape limit must be an integer above 0. Default is unlimited."
            return errno.EINVAL
    if "--depth_limit" in a:
        dlim = a[a.index("--depth_limit") + 1]
        if intstring(dlim) and int(dlim) > 0:
            params["depth_limit"] = int(dlim)
            if int(dlim) < 500:
                print "Warning: depth limit set to below 500."
        else:
            print "Depth limit must be an integer above 0. Default is unlimited."
            return errno.EINVAL
    if "--titles" in a:
        titles = a[a.index("--titles") + 1]
        if " |" in titles or "| " in titles:
            print "Warning: removing trailing spaces from compound titles parameter"
            titles = title.replace(" |","|")
            titles = title.replace("| ","|")
        params["page_titles"] = titles
        print titles.count('|')+1, "page(s) chosen:", ", ".join(titles.split('|'))
    if "--domain" in a:
        params["domain"] = a[a.index("--domain") + 1] 
    return params

def _flag_sanity(flags):
    for arg in sys.argv:
        if re.search("^-[A-Za-z]*$", arg):
            for ch in arg[1:]:
                if ch == 's':
                    flags['scrape'] = True
                    continue
                if ch == 'f':
                    flags['fetch'] = True
                    continue
                if ch == 'X':
                    flags['plotshow'] = True
        if arg == "--offline":
            flags['offline'] = True
        if arg == "--no-weights":
            flags['noweight'] = True
            print "flagged"
        if arg == "--trundle":
            flags['trundle'] = True
    return flags

def main():
    params = {'scrape_limit': -1,
              'depth_limit': -1,
              'page_titles': 'random',
              'revids': 0,
              'userids': 0,
              'domain':None,
              'weights':{'maths':0,
                        'headings':0,
                        'quotes':0,
                        'files/images':0,
                        'links':0,
                        'citations':0,
                        'normal':0},
              'user':None}
    flags = {'scrape': False,
             'offline': False,
             'weightsdefault' : True,
             'plotshow': False,
             'noweight':False,
             'trundle':False,
             'view':False}

    
    params = _arg_sanity(params) ##ARGUMENT HANDLING
    flags = _flag_sanity(flags) ##FLAG SANITY 
    
    analyser = WikiInterface(params, flags)

    if flags['scrape']:
        print "---------------SCRAPE MODE---------------"
        if analyser.scrape():
            sys.exit(0)
        else:
            print "error"
            sys.exit(-1)
    
    print "---------------ANALYSE MODE---------------"    
    while True:
        results = analyser.analyse()
        if flags['plotshow']:
            form = ['revid',
                    'Maths',
                    'Citations',
                    'Files / Images',
                    'Links',
                    'Structure',
                    'Normal',
                    'Gradient',
                    'user',
                    'trajectory',
                    'timestamp']
            formresults = []
            for r in results:
                res = {}
                for i, f in enumerate(form):
                    res.update({f:r[i]})
                formresults.append(res)                 
            IPlot(formresults)
        
        if not (flags['trundle'] and params['page_titles'] == 'random'):
            break

    sys.exit(0)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nKeyboard Interrupt"
        sys.exit(0)
