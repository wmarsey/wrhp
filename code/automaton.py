import database as db
import wikiScraper as wk
import lshtein as lv
import sys
import errno
import re
#import gnuplot
#import pylab as plt

VERSION_NUMBER = "0.0.0.0.00.1"

def print_help():
    with open("../README", "r") as helpfile:
        print helpfile.read()

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
        if arg == "--offline":
            flags['offline'] = True
    
    # try:
    #     if sum([1 for f in flags.itervalues() if f]) != 1:
    #         raise ValueError("One mode must be used: -s, -f")
    # except ValueError:
    #     print "Error: One mode must be used: -s, -f"
    #     sys.exit(0)
    return flags

def scrape(params):
    scraper = None
    if params["page_titles"] == "random":
        scraper = wk.WikiRevisionScrape(
            historylimit=params['depth_limit'],
            pagelimit=params['scrape_limit']
            )
    else:
        scraper = wk.WikiRevisionScrape(
            historylimit=params['depth_limit'],
            _titles=params['page_titles']
            )
    return scraper.scrape() #a list of the scraped pages ids
    #return True

def plottrajectory(revid, database):
    trajectory = database.gettrajectory(revid)
    with open("plot/"+str(revid), "w") as file:
        file.write("# distance \t revid\n")
        for tr in trajectory:
            file.write("\t".join(str(t) for t in tr)+"\n")
    with open("plot/"+str(revid), "r") as file:
        print file.read()

def analyse(params, flags):
    if(params['scrape_limit'] != -1):
        print "Warning: ignoring '--scrape_limit' setting -- will only analyse 1 article"
    params['scrape_limit'] = 1
    database = db.Database()
    pageid = None
    if flags['offline']:
        params['titles'], pageid = database.getrandom("title")
        print "Fetching random article from database,", params['titles']
    else:
        pageids = scrape(params)
    pageids = [pageid]
    for pageid in pageids:
        print "analysing", pageids
        extantrevs = [e[0] for e in database.getextantrevs(pageid)]
        revx, oldrevs = extantrevs[-1], extantrevs[:-1]
        #print "extant revids", oldrevs
        #print "newest rev", revx
        contentx = database.getrevcontent(revx)[0][0]   
        print "tracing trajectory"
        for oldrev in oldrevs:
            dist = database.getdist([revx,oldrev])
            if not dist:
                contenty = database.getrevcontent(oldrev)[0][0] 
                levy = lv.fastlev.dist(contentx, contenty)
                #print "dist between", revx, "and", oldrev, "is", levy
                sys.out.write('.')
                database.distinsert([revx, oldrev, levy])
                database.distinsert([oldrev, revx, levy])
            else:
                #print "dist between", revx, "and", oldrev, "is", dist
                sys.out.write('.')
        print "calculating pairs"
        i, v = 0, 1
        while v < len(extantrevs):
            while v != len(extantrevs)-1 \
                    and database.getdist([revx,extantrevs[i]]) \
                    <= database.getdist([revx,extantrevs[v]]):
                print "skipping version", v, "- revid:", extantrevs[v]
                v = v + 1
            i = v-1
            dist = database.getdist([extantrevs[i],extantrevs[v]])
            if not dist:
                contentx = database.getrevcontent(extantrevs[i])[0][0]
                contenty = database.getrevcontent(extantrevs[v])[0][0]
                levy = lv.fastlev.dist(contentx, contenty)
                database.distinsert([extantrevs[i], extantrevs[v], levy])
                database.distinsert([extantrevs[v], extantrevs[i], levy])
                print "dist between", extantrevs[i], "and", extantrevs[v], "is", levy
            else:
                print "dist between", extantrevs[i], "and", extantrevs[v], "is", dist
            i = v
            v = v + 1
        plottrajectory(revx,database)
        

def fetch():
    contentparams = {}
    contentparams.update({'titles':params['titles']})
    if params['page_titles'] != "random" and params['revids']:
        contentparams.update({'revids':params['revids']})
    if params['userids']:
        contentparams.update({'userids':params['userids']})
    print "Fetching from database"
    return db.getrevfull(**contentparams)

def main():
    params = {"scrape_limit": -1,
              "depth_limit": -1,
              "page_titles": "random",
              "revids": 0,
              "userids": 0}
    flags = {'scrape': False,
             'fetch': False,
             'analyse': False,
             'offline': False}

    ##ARGUMENT HANDLING
    params = _arg_sanity(params)
    ##FLAG SANITY
    flags = _flag_sanity(flags)
    ##ECHO PARAMETERS
    echo_params(flags, params)

    if flags['scrape']:
        if scrape(params):
            sys.exit(0)
        else:
            print "error"
            sys.exit(-1)

    if flags['fetch']:
        data = fetch(params)
        if data:
            print "fetched"
            print data
        else:
            print "error"
            sys.exit(-1)

    results = analyse(params, flags)
    print results
    sys.exit(0)

if __name__ == "__main__":
    main()
