import database as db
import wikiScraper as wk
import lshtein as lv
import sys
import errno
import re

VERSION_NUMBER = "0.0.0.0.00.1"

def print_help():
    print "There is no help for you, not now. Not after what you did."

def intstring(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

##PRINTS OUT DICTIONARY
def echo_params(flags, params):
    print "---- PARAMETERS ----"
    for key, val in flags.iteritems():
        if val:
            print "mode:\t\t", key
    for key, val in params.iteritems():
        print key, ":\t", val

##HANDLES COMMAND-LINE ARGUMENTS
def _arg_sanity(params):
    a = sys.argv
    if "--help" in a:
        return print_help()
    if "--version" in a:
        print "Version:", VERSION_NUMBER
        return
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
    if "--title" in a:
        titles = a[a.index("--title") + 1]
        if " " in titles:
            print "Warning: removing spaces from titles parameter"
            titles = title.replace(" ","")
        params["page_titles"] = titles
        print titles.count('|')+1, "page(s) chosen:", ", ".join(titles.split('|'))
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
                if ch == 'a':
                    flags['analyse'] = True
    try:
        if sum([1 for f in flags.itervalues() if f]) != 1:
            raise ValueError("One mode must be used: -s, -f or -a")
    except ValueError:
        print "Error: One mode must be used: -s, -f or -a"
        sys.exit(0)
    return flags

def main():
    params = {"scrape_limit": -1,
              "depth_limit": -1,
              "page_titles": "random",
              "revids": 0,
              "userids": 0}
    flags = {'scrape': False,
             'fetch': False,
             'analyse': False}

    ##ARGUMENT HANDLING
    params = _arg_sanity(params)
    ##FLAG SANITY
    flags = _flag_sanity(flags)
    ##ECHO PARAMETERS
    echo_params(flags, params)
    
    if flags['scrape']:
        scraper = None
        if params["page_titles"] == "random":
            scraper = wk.WikiRevisionScrape(
                historylimit=params['depth_limit'],
                )
        else:
            scraper = wk.WikiRevisionScrape(
                historylimit=params['depth_limit'],
                _titles=params['page_titles']
                )
        scraper.scrape()
        sys.exit(0)

    if flags['fetch']:
        if params['page_titles'] == "random" and not params['revids'] and not params['userids']:
            print "You must specify an article title, revid or userid in order to use fetch mode."
            sys.exit(-1)
        contentparams = {}
        if params['page_titles'] != "random":
            contentparams.update({'titles':params['titles']})
        if params['revids']:
            contentparams.update({'revids':params['revids']})
        if params['userids']:
            contentparams.update({'userids':params['userids']})
        fetch = getrevfull(**contentparams)
        if not fetch:
            print "FULL FAILURE"
            sys.exit(-1)
        sys.exit(0)

    if flags['analyse']:
        sys.exit(0)

if __name__ == "__main__":
    main()
