from __future__ import division ##for float-returning divisor
import errno
import re
import sys
import math as m
from wikipedia import search
from dataplotter import Plotter
from interface import WikiInterface 
from consts import *

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

def _get_weights(weights):
    print
    message = "You haven't supplied any non-default weights. Would you like to supply some now? [N]:"
    while True:
        inp = raw_input(message).strip().lower()
        if not inp:
            return
        if inp == "n" or inp == "no":
            return
        if inp != "y" and inp != "yes":
            message = "Invalid input. Please enter Y or N [N]:"
        else:
            break

    print "You may now choose weights for each of the following:"
    print ", ".join([k for k in weights])

    while True:
        for w in weights:
            message = "Type a number between 0 and 1 for weight '" + w + "' [0]:"
            while True:
                fail = False;
                inp = raw_input(message);
                if not inp:
                    break
                try:
                    l = len(inp)
                except:
                    fail = True
                    pass
                else:
                    if (l == 0):
                        print "here"
                        break
                if not fail:
                    try:
                        num = float(inp)
                    except:
                        pass
                    else:
                        if 0 <= num <= 1:
                            weights[w] = num
                            break
                message = "Invalid input for weight '" + w + "'. Please type a number between 0 and 1. [1]:"
        print "Chosen weights:"
        print [k + " : " + str(v) for k,v in weights.iteritems()]
        message = "Is this correct? [Y]:"
        while True:
            conf = raw_input(message).strip().lower()
            if not conf or conf == "y" or conf == "yes":
                return
            if conf == "n" or conf == "no":
                break
            message = "Invalid input. Please type Y or N [Y]:"

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
                        'normal':0}}
    flags = {'scrape': False,
             'fetch': False,
             'analyse': False,
             'offline': False,
             'weightsdefault' : True,
             'plotshow': False,
             'noweight':False,
             'trundle':False}

    
    params = _arg_sanity(params) ##ARGUMENT HANDLING
    flags = _flag_sanity(flags) ##FLAG SANITY 
    #echo_params(flags, params) ##ECHO PARAMETERS 
    
    analyser = WikiInterface(params, flags)

    if flags['scrape']:
        print "---------------SCRAPE MODE---------------"
        if analyser.scrape():
            sys.exit(0)
        else:
            print "error"
            sys.exit(-1)

    if flags['fetch']:
        print "---------------FETCH MODE---------------"
        data = fetch(params)
        if data:
            print "fetched"
            print data
        else:
            print "error"
            sys.exit(-1)
    
    print "---------------ANALYSE MODE---------------"    
    #analyser = WikiInterface(params, flags)
    while True:
        "hey"
        results = analyser.analyse()
        "hi"
        if(results):
            plt = Plotter()
            for k, t in results.iteritems():
                print
                print "\nAnalysis of article " + t['title'] + " complete, saving image files:"
                title = "Edit trajectory of article '" + t['title'] + "'" 
                revx = t['revs'][-1]
                print plt.trajectory(revx, 
                                     *t['trajectory'],
                                     pageid=k,
                                     title=title)
                title = "Contributors to " + t['title'] + " by edit count"
                ident = "count"
                xaxisname = "Hours since creation"
                yaxisname = "Edit count"
                print plt.barchart(revx,
                                   *t['editcounts'], ##barheights/labels
                                   pageid=k,
                                   title=title,
                                   ident=ident,
                                   xaxisname=xaxisname,
                                   yaxisname=yaxisname)
                title = "Contributors by reward"
                ident = "reward"
                yaxisname = "Reward share"
                print plt.barchart(revx, 
                                   *t['rewards'], ##barheights/labels
                                   pageid=k,
                                   title=title,
                                   ident=ident,
                                   xaxisname=xaxisname,
                                   yaxisname=yaxisname)
        else:
            print "ho"
            sys.exit(-1)
        if not (flags['trundle'] and params['page_titles'] == 'random'):
            if not flags['trundle']:
                print "trundle broke"
            if not params['page_titles']:
                print 'page titles broke'
            print "breaking"
            break
    print "hey"
    sys.exit(0)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nKeyboard Interrupt"
        sys.exit(0)
