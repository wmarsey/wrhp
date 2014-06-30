import database as db
import wikiScraper as wk
import lshtein as lv
import sys
import errno
import re
import datetime, time
#from os import system
#import gnuplot
#import pylab as plt
#import subprocess
import scipy
import os

VERSION_NUMBER = "0.0.0.0.00.1"

def dot():
    sys.stdout.write('.')
    sys.stdout.flush()

def sdot():
    sys.stdout.write('-')
    sys.stdout.flush()

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
## ### NEED TO ADD CONDITIONALS ACCORDING TO FLAGS
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
    return scraper.scrape()

def plot(revid, database):
    rawtrajectory = database.gettrajectory(revid)
    creation = rawtrajectory[0][0]
    trajectory = [((e[0]-creation).total_seconds(), e[1]) for e in rawtrajectory] 
    rawgrowth = database.getgrowth(revid)
    growth = [e[1] for e in rawgrowth]
    data = []
    if len(growth) == len(trajectory):
        with open("plot/data/"+str(revid)+'plot', "w") as file:
            file.write("# size \t revid\n")
            for gr, tr in zip(growth, trajectory):
                file.write("\t".join([str(tr[0]), str(tr[1]), str(gr)])+"\n")
    with open("plot/data/"+str(revid)+"plot", "r") as file:
        print file.read()
    outputfile = 'plot/images/' + str(revid) + 'plot.png'
    plotfile = 'plot/data/' + str(revid) + 'plot'
    xaxis = 'Seconds since article creation'
    yaxis = 'Distance from final'
    title = 'Edit trajectory towards revision ' + str(revid) 
    f = os.popen('gnuplot', 'w')
    print >>f, "set terminal pngcairo size 700,512 enhanced font 'Verdana,10'"
    print >>f, "set output '" + outputfile + "'"
    print >>f, "set border linewidth 1.5"
    print >>f, "set style line 1 lc rgb '#0060ad' lt 1 lw 2 pt 7 ps 1.5"
    print >>f, "set style line 2 lc rgb '#000000' lt 1 lw 2 pt 7 ps 1.5"
    print >>f, "set ylabel '" + yaxis + "'"
    print >>f, "set xlabel '" + xaxis + "'"
    print >>f, "set format y \"%6.0f\";"
    print >>f, "set format x \"%6.0f\";"
    print >>f, "set nokey"
    print >>f, "set title '" + title + ","
    print >>f, "plot '" + plotfile + "' using 1:2 with linespoints ls 1,\\"
    print >>f, "'" + plotfile + "' using 1:3 with linespoints ls 2"
    f.flush()

def analyse(params, flags):
    if(params['scrape_limit'] != -1):
        print "Warning: ignoring '--scrape_limit' setting -- will only analyse 1 article"
    params['scrape_limit'] = 1
    database = db.Database()
    pageid = None
    if flags['offline']:
        params['titles'], pageid = database.getrandom()
        print "Fetching random article from database,", params['titles']
        pageids = [pageid]
    else:
        pageids = scrape(params)
        print pageids
    for pageid in pageids:
        print "analysing", pageids
        extantrevs = [e[0] for e in database.getextantrevs(pageid)]
        #print extantrevs
        revx, oldrevs = extantrevs[-1], extantrevs[:-1]
        contentx = database.getrevcontent(revx)[0][0]   
        print "tracing trajectory", len(extantrevs), "revisions"
        print "target revision", len(contentx), "long"
        for oldrev in oldrevs:
            dist1 = database.getdist([revx,oldrev])
            dist2 = database.getdist([oldrev, revx])
            if not dist1 or dist2:
                contenty = database.getrevcontent(oldrev)[0][0] 
                levy = lv.fastlev.dist(contentx, contenty)
            if not dist1:
                database.distinsert([revx, oldrev, levy])
            if not dist2:
                database.distinsert([oldrev, revx, levy])
            dot()
        print "\ncalculating pairs"
        i, v = 0, 1
        while v < len(extantrevs):
            while v != len(extantrevs)-1 \
                    and database.getdist([revx,extantrevs[i]]) \
                    <= database.getdist([revx,extantrevs[v]]):
                sdot()
                v = v + 1
            i = v-1
            dist = database.getdist([extantrevs[i],extantrevs[v]])
            if not dist:
                contentx = database.getrevcontent(extantrevs[i])[0][0]
                contenty = database.getrevcontent(extantrevs[v])[0][0]
                levy = lv.fastlev.dist(contentx, contenty)
                database.distinsert([extantrevs[i], extantrevs[v], levy])
                database.distinsert([extantrevs[v], extantrevs[i], levy])
            dot()
            i = v
            v = v + 1
        #plottrajectory(revx,database)
        #plotgrowth(revx, database)
        plot(revx, database)
        
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
