import database as db
import wikiScraper as wk
import lshtein as lv
import errno
import re
import datetime, time
import scipy
import os, sys
import signal
import matplotlib.pyplot as plt

VERSION_NUMBER = "0.0.0.0.00.1"
BASEPATH = "/homes/wm613/individual-project/code/"

unzip = lambda l:tuple(zip(*l))

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

def count(revid, rawdata, title):
    filename = str(revid) + 'count'
    imagefile = BASEPATH + "plot/images/" + filename + ".png"
    xaxis = 'Username'
    yaxis = 'Contribution count'
    title = 'User contribution counts for article "' + title + '"'

    sdata = sorted(rawdata, key = lambda x: x[1])

    n, bins, patches = plt.hist(sdata, facecolor='green')
    plt.setp(patches, 'facecolor', 'g', 'alpha', 0.75)    
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(title)
    
    plt.show()

    return True

def reward(revid, rawdata, title):
    xaxis = 'Username'
    yaxis = 'Contribution weight'
    title = unicode('User rewards for contributions to article "' + title + '"')
    filename = str(revid) + 'reward'
    sdata = sorted(rawdata, key = lambda x: x[1])
    splitdata = unzip(sdata)
    drange = xrange(len(sdata))
    fig, ax = plt.subplots()   

    ax.bar(drange, splitdata[1], width=100)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(title)
    plt.xticks(drange,[unicode(e) for e in splitdata[0]], rotation=90)
    plt.show()

    return True

def trajectory(revid, rawtrajectory, rawgrowth, title):
    #imagefile = BASEPATH + "plot/images/" + filename + ".png"
    xaxis = 'Hours since article creation'
    yaxis1 = 'Edit distance from final'
    yaxis2 = 'Article length'
    title =  unicode('Edit trajectory towards revision ' + unicode(revid) + ', article ' + title + ', from ' + unicode(rawtrajectory[0][0]) + " to " + unicode(rawtrajectory[-1][0]))
    creation = rawtrajectory[0][0]
    times = [(e[0]-creation).total_seconds()/3600 for e in rawtrajectory]
    trajectory = [e[1] for e in rawtrajectory]
    growth = [e[1] for e in rawgrowth]
    fig, ax1 = plt.subplots()
    ax1.plot(times, trajectory, 'bo-', label='Edit distance from final')
    ax1.set_xlabel(xaxis)
    ax1.set_ylabel(yaxis1, color='b')
    
    ax2 = ax1.twinx()
    ax2.plot(times, growth, 'ko-', label='Article length')
    ax2.set_ylabel(yaxis2, color='k')

    for tl in ax1.get_yticklabels():
        tl.set_color('b')

    ax1.legend(loc=0)
    ax2.legend(loc=0)

    plt.title(title)
    plt.show()

    return True

def analyse(params, flags):
    repeat = 1;
    if(params['scrape_limit'] != -1):
        repeat = params['scrape_limit']
    params['scrape_limit'] = 1
    database = db.Database()
    pageid = None
    if flags['offline']:
        params['titles'], pageid = database.getrandom()
        print "Fetching random article from database,", params['titles']
        pageids = [pageid]
        titles = [params['titles']]
    else:
        titles, pageids = scrape(params)
        print pageids
    for t, pageid in enumerate(pageids):
        print "Analysing", titles[t]
        extantrevs = [e[0] for e in database.getextantrevs(pageid)]
        revx, oldrevs = extantrevs[-1], extantrevs[:-1]
        contentx = database.getrevcontent(revx)[0][0]   
        print "Tracing trajectory", len(extantrevs), "revisions"
        for oldrev in oldrevs:
            dist1 = database.gettraj([revx, oldrev])
            if not dist1:
                contenty = database.getrevcontent(oldrev)[0][0] 
                levy = lv.fastlev.plaindist(contentx, contenty)
                database.trajinsert([revx, oldrev, levy])
            dot()
        print "\nCalculating pairs"
        i, v = 0, 1
        creward = 0
        while v < len(extantrevs):
            q = 0
            if creward < 0: #doesn't do skipping until out of creward period
                while v != len(extantrevs)-1 \
                        and q < params['freward'] \
                        and database.gettraj([revx,extantrevs[i]]) \
                        <= database.gettraj([revx,extantrevs[v]]):
                    sdot() #dash
                    v = v + 1
                    q = q + 1
                i = v-1
            dist = database.getdist([extantrevs[i],extantrevs[v]])
            if not dist:
                contentx = database.getrevcontent(extantrevs[i])[0][0]
                contenty = database.getrevcontent(extantrevs[v])[0][0]
                levresults = lv.fastlev.weightdist(contentx, contenty)
                print '\n', levresults
                levresults2 = lv.fastlev.plaindist(contentx, contenty)
                print levresults2
                database.distinsert([extantrevs[i], extantrevs[v], levresults[0]])
                database.distinsert([extantrevs[v], extantrevs[i], levresults[0]])
            dot()
            i = v
            v = v + 1
            if creward < params['creward'] and creward >= 0:
                 creward = creward + 1
            elif creward > 0:
                creward = -1
        plot1 = trajectory(revx, database.gettrajectory(revx), database.getgrowth(revx), titles[t])
        #plot2 = count(revx, database.getusereditcounts(pageid), titles[t])
        plot3 = reward(revx, database.getuserchange(pageid), titles[t])
        print plot1
        print plot2
        print plot3
        return True

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

    ##if limited to scrape
    if flags['scrape']:
        if scrape(params):
            sys.exit(0)
        else:
            print "error"
            sys.exit(-1)
    ##if limited to fetch
    if flags['fetch']:
        data = fetch(params)
        if data:
            print "fetched"
            print data
        else:
            print "error"
            sys.exit(-1)
    ##else analyse
    params['freward'] = 3
    params['creward'] = 10
    if(analyse(params, flags)):
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nKeyboard Interrupt"
        sys.exit(0)
