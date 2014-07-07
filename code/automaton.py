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

dotcount = 1
def dot(reset=False, final=False):
    global dotcount
    if reset:
        dotcount = 1
    if not (dotcount%50) and dotcount:
        sys.stdout.write('|')
    else:
        sys.stdout.write('.')
    if final or (not (dotcount%50) and dotcount):
        sys.stdout.write('\n')
    dotcount = dotcount + 1
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
    filename = title + 'count'
    imagefile = BASEPATH + "plot/images/" + filename + ".png"
    xaxis = 'Username'
    yaxis = 'Contribution count'
    title = 'User contribution counts for article "' + title + '"'.encode('utf-8')
    sdata = sorted(rawdata, key = lambda x: x[1])
    barlabels = [] 
    barheight = []
    for i, e in enumerate(sdata):
        barlabels.append(e[0].decode('utf-8').strip())
        barheight.append(e[1])
    fig = plt.figure(figsize=(13,8), dpi=600, tight_layout=True)
    ax = fig.add_subplot(111)
    h = ax.bar(xrange(len(barheight)), barheight, label=barlabels, width=0.8)
    xticks_pos = [0.5*p.get_width() + p.get_xy()[0] for p in h]
    ax.get_yaxis().get_major_formatter().set_scientific(False)
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(title)
    plt.xticks(xticks_pos, barlabels, rotation=90, ha='center')
    plt.savefig(imagefile)
    return imagefile

def reward(revid, rawdata, title):
    filename = title + 'reward'
    imagefile = BASEPATH + "plot/images/" + filename + ".png"
    xaxis = 'Username'
    yaxis = 'Contribution weight'
    title = 'User rewards for contributions to article "' + title + '"'.encode('utf-8')
    filename = str(revid) + 'reward'
    sdata = sorted(rawdata, key = lambda x: x[1])
    barlabels = [] 
    barheight = []
    for i, e in enumerate(sdata):
        barlabels.append(e[0].decode('utf-8').strip())
        barheight.append(e[1])
    fig = plt.figure(figsize=(13,8), dpi=600, tight_layout=True)
    ax = fig.add_subplot(111)
    h = ax.bar(xrange(len(barheight)), barheight, label=barlabels, width=0.8)
    xticks_pos = [0.5*p.get_width() + p.get_xy()[0] for p in h]
    ax.get_yaxis().get_major_formatter().set_scientific(False)    
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    plt.title(title)
    plt.xticks(xticks_pos, barlabels, rotation=90, ha='center')
    plt.savefig(imagefile)
    return imagefile

def trajectory(revid, rawtrajectory, rawgrowth, title):
    filename = title + 'traj'
    imagefile = BASEPATH + "plot/images/" + filename + ".png"
    xaxis = 'Hours since article creation'
    yaxis1 = 'Edit distance from final'
    yaxis2 = 'Article length'
    title = ('Edit trajectory towards revision ' + str(revid) + ', article ' + title + '\n from ' + str(rawtrajectory[0][0]) + " to " + str(rawtrajectory[-1][0])).encode('utf-8')
    creation = rawtrajectory[0][0]
    times = [(e[0]-creation).total_seconds()/3600 for e in rawtrajectory]
    trajectory = [e[1] for e in rawtrajectory]
    growth = [e[1] for e in rawgrowth]
    
    fig = plt.figure(figsize=(13,8), dpi=600)
    ax1 = fig.add_subplot(111)
    ax1.plot(times, trajectory, 'bo-', label='Edit distance from final')
    ax1.set_xlabel(xaxis)
    ax1.set_ylabel(yaxis1, color='b')
    ax1.get_yaxis().get_major_formatter().set_scientific(False)
    ax2 = ax1.twinx()
    ax2.plot(times, growth, 'ko-', label='Article length')
    ax2.set_ylabel(yaxis2, color='k')
    ax2.get_yaxis().get_major_formatter().set_scientific(False)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    plt.title(title)
    plt.savefig(imagefile)
    return imagefile

def getweights(weights):
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
            message = "Type a number between 0 and 1 for weight '" + w + "' [1]:"
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
        count = 0
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
                database.distinsert([extantrevs[i], extantrevs[v], levresults['dist']])
                database.distinsert([extantrevs[v], extantrevs[i], levresults['dist']])
            i = v
            v = v + 1
            dot((not count), (v < len(extantrevs)))
            count = count + 1
            if creward < params['creward'] and creward >= 0:
                 creward = creward + 1
            elif creward > 0:
                creward = -1
                
        print
        print
        if(flags['weightsdefault']):
            getweights(params['weights']);
            
        title = titles[t].replace(" ","_")
        print
        print "\nAnalysis complete, saving image files:"
        print trajectory(revx, database.gettrajectory(revx), database.getgrowth(revx), title)
        print count(revx, database.getusereditcounts(pageid), title)
        print reward(revx, database.getuserchange(pageid), title)

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
    params = {'scrape_limit': -1,
              'depth_limit': -1,
              'page_titles': 'random',
              'revids': 0,
              'userids': 0,
              'weights':{'maths':1,
                        'headings':1,
                        'quotes':1,
                        'files/images':1,
                        'links':1,
                        'citations':1,
                        'normal':1}}
    flags = {'scrape': False,
             'fetch': False,
             'analyse': False,
             'offline': False,
             'weightsdefault' : True}

    
    params = _arg_sanity(params) ##ARGUMENT HANDLING
    flags = _flag_sanity(flags) ##FLAG SANITY 
    #echo_params(flags, params) ##ECHO PARAMETERS 
    
    if flags['scrape']: ##if limited to scrape
        print "---------------SCRAPE MODE---------------"
        if scrape(params):
            sys.exit(0)
        else:
            print "error"
            sys.exit(-1)

    if flags['fetch']: ##if limited to fetch
        print "---------------FETCH MODE---------------"
        data = fetch(params)
        if data:
            print "fetched"
            print data
        else:
            print "error"
            sys.exit(-1)
    
    print "---------------ANALYSE MODE---------------"
    params['freward'] = 3 ##else analyse
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
