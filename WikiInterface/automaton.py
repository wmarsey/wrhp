from __future__ import division ##for float-returning divisor
import database as db
import wikiScraper as wk
import lshtein as lv
import errno
import re
import datetime, time
import sys
import matplotlib.pyplot as plt
import math as m
from wikipedia import search

VERSION_NUMBER = "0.0.0.0.00.1"
BASEPATH = "/homes/wm613/individual-project/WikiInterface/"
WEIGHTLABELS = ["maths",
                "headings",
                "quotes", 
                "files/images",
                "links",
                "citations",
                "normal"]
class WikiInterface:
    dat = None
    plt = None
    dotcount = 1
    dtb = None
    params = {'scrape_limit': -1,
              'depth_limit': -1,
              'page_titles': 'random',
              'revids': 0,
              'userids': 0,
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
             'plotshow': False}
    
    def __init__(self, params=None, flags=None):
        if params:
            self.params = params
        if flags:
            self.flags = flags
        self.dtb = db.Database()
        self.dat = Data(self.params['weights'])

    def checktitle(self):
        return self.scrape(test=True)

    def config(self, params=None, flags=None):
        if params:
            self.params.update(params)
        if flags:
            self.flags.update(flags)
        self.dtb = db.Database()
        self.dat = Data(self.params['weights'])

    def analyse(self):
        repeat = 1;
        if(self.params['scrape_limit'] != -1):
            repeat = self.params['scrape_limit']
        self.params['scrape_limit'] = 1
        self.database = db.Database()
        pageid = None
        if self.flags['offline']:
            self.params['titles'], pageid = self.dtb.getrandom()
            print "Fetching random article from database,", self.params['titles']
            pageids = [pageid]
            titles = [self.params['titles']]
        else:
            titles, pageids = self.scrape()
        pagecount = 0
        for t, pageid in enumerate(pageids):
            print "Analysing", titles[t]
            revs = self.dtb.getextantrevs(pageid)
            revx = revs[0]
            contentx = self.dtb.getrevcontent(revx)   
            print "Tracing trajectory", len(revs), "revisions"
            for rev in revs:
                self.dat.gettraj(contentx, revx, rev)
                dot()
            print "\nCalculating pairs"
            creward, i, v = 0, 0, 1
            while not v > len(revs):
                parentid = 0
                if v < len(revs):
                    parentid = revs[v]
                childid = revs[i]
                if self.dtb.getdist(childid) < 0:
                    self.dtb.distinsert(self.dat.processweights(parentid, 
                                                                childid))
                dot((not i), (t != (len(pageids)-1)))
                i = v
                v = v + 1
                pagecount = pagecount + 1

            if(self.flags['weightsdefault']):
                _get_weights(self.params['weights'])

            analysis = {pageid:{'title':titles[t],
                                'revs':revs,
                                'trajectory':self.dat.gettrajdata(revx),
                                'editcounts':self.dat.getbardata(pageid, 
                                                                 "count"),
                                'rewards':self.dat.getbardata(pageid,
                                                              "reward"),
                                'userinfo':self.dtb.getuserinfo(revx)
                                }
                        }

            return analysis

    def dot(self, reset=False, final=False, slash=False):
        dot = '.'
        if slash:
            dot = '-'
        if reset:
            self.dotcount = 1
        if not (dotcount%50) and dotcount:
            sys.stdout.write('|')
        else:
            sys.stdout.write(dot)
        if final or (not (dotcount%50) and dotcount):
            sys.stdout.write('\n')
        self.dotcount = self.dotcount + 1
        sys.stdout.flush()

    def scrape(self, test=False):
        scraper = None
        if not test and self.params["page_titles"] == "random":
            scraper = wk.WikiRevisionScrape(
                historylimit=self.params['depth_limit'],
                pagelimit=self.params['scrape_limit'],
                domain=self.params['domain']
                )
        else:
            scraper = wk.WikiRevisionScrape(
                historylimit=self.params['depth_limit'],
                _titles=self.params['page_titles'],
                upperlimit=False,
                domain=self.params['domain']
                )
        if test:
            return scraper.test()
        return scraper.scrape()

class Data:
    dtb = None

    def __init__(self, _weights):
        self.dtb = db.Database()
        self.weights = _weights

    def weightdata(self, pageid):
        wdata = []
        for u in self.dtb.getuserchange(pageid):
            sdist = 0
            for i,d in enumerate(u[2:]):
                sdist = sdist + (d * (1+self.weights[WEIGHTLABELS[i]]))
            wdata.append((u[0],sdist))
        shdata = []
        total = sum([e[1] for e in wdata])
        for user, reward in wdata:
            share = reward / total
            shdata.append((user, share))
        return shdata

    def getbardata(self, pageid, datatype):
        dbdata = None
        if(datatype == "count"):
            dbdata = self.dtb.getusereditcounts(pageid)
        elif(datatype == "reward"):
            dbdata = self.weightdata(pageid)      
        sdata = sorted(dbdata, 
                       key = lambda x: x[1])
        barlabels = [] 
        barheights = []
        for i, e in enumerate(sdata):
            barlabels.append(e[0].decode('utf-8').strip())
            barheights.append(e[1])
        return (barheights, barlabels)

    def gettrajdata(self, revx):
        dbtraj = self.dtb.gettrajectory(revx)
        traj = [e[1] for e in dbtraj]
        dbgrowth = self.dtb.getgrowth(revx)
        growth = [e[1] for e in dbgrowth]
        creation = dbtraj[0][0]
        times = [(e[0]-creation).total_seconds()/3600 for e in dbtraj]
        for i,e in enumerate(dbgrowth):
            print dbtraj[i], e
        return (times, traj, growth)

    def gradientadjust(self, parentid, revid, distuple):
        gradconst = 1
        if parentid:
            x = (self.dtb.gettime((revid,)) - \
                     self.dtb.gettime((parentid,))).total_seconds()/3600
            y = self.dtb.gettrajheight((revid,)) - self.dtb.gettrajheight((parentid,))
            if x < 0:
                print "Error: Time travel"
            elif not x:
                return wdata
            gradconst = 0.5 - m.atan(y/x)/m.pi
        return tuple([revid] + [d*gradconst for d in distuple[1:]])

    def processweights(self, parentid, revid):
        contentx = ""
        if parentid:
            contentx = self.dtb.getrevcontent(parentid)
        contenty = self.dtb.getrevcontent(revid)
        levresults = lv.fastlev.weightdist(contentx, contenty)
        #lev2 = lv.fastlev.weightdist(*self.dtb.getdifftexts(parentid, revid))
        #print levresults['dist'], lev2['dist']
        plaindist = levresults['dist']
        maths = levresults['maths1'] + levresults['maths2']
        headings = levresults['h2'] + levresults['h3'] + \
            levresults['h4'] + levresults['h4'] + levresults['h5'] + \
            levresults['h6']
        quotes = levresults['blockquote']
        filesimages = levresults['file'] + levresults['table'] + \
            levresults['table'] + levresults['score'] + \
            levresults['media']
        links = levresults['linkinternal'] + levresults['linkexternal']
        citations = levresults['citation'] + levresults['citationneeded']
        normal = levresults['norm']
        results = (revid, 
                   plaindist,
                   maths,
                   headings,
                   quotes,
                   filesimages,
                   links,
                   citations,
                   normal)
        return self.gradientadjust(parentid, revid, results)

    def gettraj(self, contentx, revx, oldrev):
        dist = self.dtb.gettraj([revx, 
                                 oldrev])
        #print dist
        if dist < 0:
            contenty = self.dtb.getrevcontent(oldrev) 
            lev = 0
            if revx == oldrev:
                lev = 0
            else:
                lev = lv.fastlev.plaindist(contentx, 
                                           contenty)
            self.dtb.trajinsert((revx, 
                                 oldrev, 
                                 lev))

    # def diff(self, oldrev, newrev):
    #     oldtext, newtext = self.dtb.getdifftexts(oldrev, newrev)
        
    #     if oldtext:
    #         return result
        

class Plotter:
    def barchart(self, revid, barheights, barlabels, pageid, title, ident, xaxisname, yaxisname, show=False): 
        filename = pageid + ident
        imagefile = BASEPATH + "plot/images/" + filename + ".png"
        if (show):
            tfigsize, tdpi = None, None
        else:
            tfigsize, tdpi = (13,8), 600
        fig = plt.figure(figsize=tfigsize, dpi=tdpi, tight_layout=True)
        ax = fig.add_subplot(111)
        h = ax.bar(xrange(len(barheights)), 
                   barheights, 
                   label=barlabels, 
                   width=0.8)
        xticks_pos = [0.5*p.get_width() + p.get_xy()[0] for p in h]
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        plt.xlabel(xaxisname)
        plt.ylabel(yaxisname)
        plt.title(title)
        plt.xticks(xticks_pos, 
                   barlabels, 
                   rotation=90, 
                   ha='center')
        if(show):
            plt.show()
        plt.savefig(imagefile)
        return imagefile

    def trajectory(self, revid, times, trajectory, growth, pageid, title, show=False):
        ##prepare text
        filename = str(pageid) + 'traj'
        imagefile = BASEPATH + "plot/images/" + filename + ".png"
        xaxis = 'Hours since article creation'
        yaxis1 = 'Edit distance from final'
        yaxis2 = 'Article length'
        title = 'Edit trajectory towards revision ' + str(revid) + ', article \'' + title + '\''.encode('utf-8')

        ##prepare matplotlib
        if (show):
            tfigsize, tdpi = None, None
        else:
            tfigsize, tdpi = (13,8), 600
        fig = plt.figure(figsize=tfigsize, 
                         dpi=tdpi, 
                         tight_layout=None)
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
        if(show):
            plt.show()
        plt.savefig(imagefile)
        return imagefile

    def fetch():
        contentparams = {}
        contentparams.update({'titles':self.params['titles']})
        if self.params['page_titles'] != "random" and self.params['revids']:
            contentparams.update({'revids':self.params['revids']})
        if self.params['userids']:
            contentparams.update({'userids':self.params['userids']})
        print "Fetching from database"
        return db.getrevfull(**contentparams)


dotcount = 1
def dot(reset=False, final=False, slash=False):
    dot = '.'
    if slash:
        dot = '-'
    global dotcount
    if reset:
        dotcount = 1
    if not (dotcount%50) and dotcount:
        sys.stdout.write('|')
    else:
        sys.stdout.write(dot)
    if final or (not (dotcount%50) and dotcount):
        sys.stdout.write('\n')
    dotcount = dotcount + 1
    sys.stdout.flush()

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
             'plotshow': False}

    
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
    results = analyser.analyse()
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
            sys.exit(0)
        else:
            sys.exit(-1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nKeyboard Interrupt"
        sys.exit(0)
