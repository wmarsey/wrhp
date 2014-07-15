from __future__ import division
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
#import csv
import math as m

VERSION_NUMBER = "0.0.0.0.00.1"
BASEPATH = "/homes/wm613/individual-project/code/"
WEIGHTLABELS = ["maths",
                "headings",
                "quotes", 
                "files/images",
                "links",
                "citations",
                "normal"]

def intstring(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

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
        self.dat = Data(params['weights'])
        self.plt = Plotter()

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
            titles = [params['titles']]
        else:
            titles, pageids = self.scrape()
        pagecount = 0
        for t, pageid in enumerate(pageids):
            print "Analysing", titles[t]
            revs = self.dtb.getextantrevs(pageid)
            revx = revs[-1]
            contentx = self.dtb.getrevcontent(revx)   
            print "Tracing trajectory", len(revs), "revisions"
            for rev in revs:
                self.dat.gettraj(contentx, revx, rev)
                dot()
            print "\nCalculating pairs"
            creward, i, v = 0, 0, 1
            while v < len(revs):
                if self.dtb.getdist(revs[i]) < 0:
                    print "didn't get anything"
                    self.dtb.distinsert(self.dat.processweights(revs[v], 
                                                               revs[i]))
                dot((not i), (t != (len(pageids)-1)))
                i = v
                v = v + 1
                pagecount = pagecount + 1

            if(self.flags['weightsdefault']):
                getweights(self.params['weights'])

            print
            print "\nAnalysis complete, saving image files:"
            title = titles[t].replace(" ","_")
            print self.plt.trajectory(*self.dat.gettrajdata(revx, 
                                                            title,
                                                            show=self.flags['plotshow']))
            print self.plt.count(*self.dat.getbardata(revx, 
                                             pageid, 
                                             title, 
                                             "count"))
            print self.plt.reward(*self.dat.getbardata(revx, 
                                              pageid, 
                                              title, 
                                              "reward",
                                              weights=self.params['weights']))
            return True

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

    def scrape(self):
        scraper = None
        if self.params["page_titles"] == "random":
            scraper = wk.WikiRevisionScrape(
                historylimit=self.params['depth_limit'],
                pagelimit=self.params['scrape_limit']
                )
        else:
            scraper = wk.WikiRevisionScrape(
                historylimit=self.params['depth_limit'],
                _titles=self.params['page_titles'],
                upperlimit=False
                )
        return scraper.scrape()

class Data:
    dtb = None

    def __init__(self, _weights):
        self.dtb = db.Database()
        self.weights = _weights

    def weightdata(dbdata):
        wdata = []
        for u in dbdata:
            sdist = 0
            for i,d in enumerate(u[2:]):
                sdist = sdist + (d * (1+self.weights[WEIGHTLABELS[i]]))
            wdata.append((u[0],sdist))
        shdata = []
        total = sum([e[1] for e in wdata])
        for user, reward in wdata:
            share = reward / total
            shdata.append((u[0], share))
        return shdata

    def getbardata(revx, pageid, title, datatype, weights=None, show=False):
        dbdata = None
        if(datatype == "count"):
            dbdata = self.dtb.getusereditcounts(pageid)
        elif(datatype == "reward"):
            dbdata = weightdata(self.dtb.getuserchange(pageid),
                                weights)      
        sdata = sorted(dbdata, 
                       key = lambda x: x[1])
        barlabels = [] 
        barheights = []
        for i, e in enumerate(sdata):
            barlabels.append(e[0].decode('utf-8').strip())
            barheights.append(e[1])
        return (revx, barheights, barlabels, title, show)

    def gettrajdata(self, revx, title, show=False):
        dbtraj = self.dtb.gettrajectory(revx)
        traj = [e[1] for e in dbtraj]
        dbgrowth = self.dtb.getgrowth(revx)
        growth = [e[1] for e in dbgrowth]
        creation = dbtraj[0][0]
        times = [(e[0]-creation).total_seconds()/3600 for e in dbtraj]   
        return (revx, times, traj, growth, title, show)

    def gradientadjust(self, parentid, revid, distuple):
        x = (self.dtb.gettime((revid,)) - \
                 self.dtb.gettime((parentid,))).total_seconds()/3600
        y = self.dtb.gettrajheight((revid,)) - self.dtb.gettrajheight((parentid,))
        if x < 0:
            print "Error: Time travel"
        elif not x:
            return wdata
        gradconst = 0.5 - m.atan(y/x)/m.pi
        print "returning", revid, "for insert"
        return tuple([revid] + [d*gradconst for d in distuple[1:]])

    def processweights(self, parentid, revid):
        contentx = self.dtb.getrevcontent(parentid)
        contenty = self.dtb.getrevcontent(revid)
        levresults = lv.fastlev.weightdist(contentx, contenty)
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
        if not dist:
            contenty = self.dtb.getrevcontent(oldrev) 
            lev = 0
            if revx == oldrev:
                lev = len(contenty) ##HACKKK
            else:
                lev = lv.fastlev.plaindist(contentx, 
                                           contenty)
            self.dtb.trajinsert((revx, oldrev, lev))
        #return lev         

class Plotter:
    def barchart(revid, barheights, barlabels, title, ident, xaxisname, yaxisname, show=False):
        filename = title + ident
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
        plt.xlabel(xaxis)
        plt.ylabel(yaxis)
        plt.title(title)
        plt.xticks(xticks_pos, 
                   barlabels, 
                   rotation=90, 
                   ha='center')
        if(show):
            plt.show()
        plt.savefig(imagefile)
        return imagefile

    # def count(revid, barheights, barlabels, title, show=False):
    #     filename = title + 'count'
    #     imagefile = BASEPATH + "plot/images/" + filename + ".png"
    #     xaxis = 'Username'
    #     yaxis = 'Contribution count'
    #     title = 'User contribution counts for article "' + title + '"'.encode('utf-8')

    #     if (show):
    #         tfigsize, tdpi = None, None
    #     else:
    #         tfigsize, tdpi = (13,8), 600
    #     fig = plt.figure(figsize=tfigsize, dpi=tdpi, tight_layout=True)
    #     ax = fig.add_subplot(111)
    #     h = ax.bar(xrange(len(barheights)), 
    #                barheights, 
    #                label=barlabels, 
    #                width=0.8)
    #     xticks_pos = [0.5*p.get_width() + p.get_xy()[0] for p in h]
    #     ax.get_yaxis().get_major_formatter().set_scientific(False)
    #     plt.xlabel(xaxis)
    #     plt.ylabel(yaxis)
    #     plt.title(title)
    #     plt.xticks(xticks_pos, 
    #                barlabels, 
    #                rotation=90, 
    #                ha='center')
    #     if(show):
    #         plt.show()
    #     plt.savefig(imagefile)
    #     return imagefile

    # def weightdata(dbdata, weights):
    #     if not weights:
    #         return dbdata
    #     wdata = []
    #     for u in dbdata:
    #         sdist = 0
    #         for i,d in enumerate(u[2:]):
    #             sdist = sdist + (d * (1+weights[WEIGHTLABELS[i]]))
    #         wdata.append((u[0],sdist))
    #     shdata = []
    #     total = sum([e[1] for e in wdata])
    #     for user, reward in wdata:
    #         share = reward / total
    #         shdata.append((u[0], share))
    #     return shdata

    # def getbardata(revx, pageid, title, datatype, weights=None, show=False):
    #     dbdata = None
    #     if(datatype == "count"):
    #         dbdata = database.getusereditcounts(pageid)
    #     elif(datatype == "reward"):
    #         dbdata = weightdata(database.getuserchange(pageid),
    #                             weights)      
    #     sdata = sorted(dbdata, 
    #                    key = lambda x: x[1])
    #     barlabels = [] 
    #     barheights = []
    #     for i, e in enumerate(sdata):
    #         barlabels.append(e[0].decode('utf-8').strip())
    #         barheights.append(e[1])
    #     return (revx, barheights, barlabels, title, show)

    # def reward(revid, barheights, barlabels, title, show=False):
    #     filename = title + 'reward'
    #     imagefile = BASEPATH + "plot/images/" + filename + ".png"
    #     xaxis = 'Username'
    #     yaxis = 'Contribution weight'
    #     title = 'User rewards for contributions to article "' + title + '"'.encode('utf-8')
    #     filename = str(revid) + 'reward'

    #     if (show):
    #         tfigsize, tdpi = None, None
    #     else:
    #         tfigsize, tdpi = (13,8), 600
    #     fig = plt.figure(figsize=tfigsize, 
    #                      dpi=tdpi, 
    #                      tight_layout=True)
    #     ax = fig.add_subplot(111)
    #     h = ax.bar(xrange(len(barheights)), 
    #                barheights, 
    #                label=barlabels, 
    #                width=0.8)
    #     xticks_pos = [0.5*p.get_width() + p.get_xy()[0] for p in h]
    #     ax.get_yaxis().get_major_formatter().set_scientific(False)    
    #     plt.xlabel(xaxis)
    #     plt.ylabel(yaxis)
    #     plt.title(title)
    #     plt.xticks(xticks_pos, 
    #                barlabels, 
    #                rotation=90, 
    #                ha='center')
    #     if(show):
    #         plt.show()
    #     plt.savefig(imagefile)
    #     return imagefile

    # def gettrajdata(revx, title, show=False):
    #     dbtraj = database.gettrajectory(revx)
    #     traj = [e[1] for e in dbtraj]
    #     dbgrowth = database.getgrowth(revx)
    #     growth = [e[1] for e in dbgrowth]
    #     creation = dbtraj[0][0]
    #     times = [(e[0]-creation).total_seconds()/3600 for e in dbtraj]   
    #     return (revx, times, traj, growth, title, show)

    def trajectory(self, revid, times, trajectory, growth, title, show=False):
        ##prepare text
        filename = title + 'traj'
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

    # def gradientadjust(self, parentid, revid, distuple):
    #     x = (self.dtb.gettime((revid,)) - \
    #              self.dtb.gettime((parentid,))).total_seconds()/3600
    #     y = self.dtb.gettrajheight((revid,)) - self.dtb.gettrajheight((parentid,))
    #     if x < 0:
    #         print "Error: Time travel"
    #     elif not x:
    #         return wdata
    #     gradconst = 0.5 - m.atan(y/x)/m.pi
    #     return tuple([revid] + [d*gradconst for d in distuple[1:]])

    # def processweights(self, parentid, revid):
    #     contentx = self.dtb.getrevcontent(parentid)[0][0]
    #     contenty = self.dtb.getrevcontent(revid)[0][0]
    #     levresults = lv.fastlev.weightdist(contentx, contenty)
    #     plaindist = levresults['dist']
    #     maths = levresults['maths1'] + levresults['maths2']
    #     headings = levresults['h2'] + levresults['h3'] + \
    #         levresults['h4'] + levresults['h4'] + levresults['h5'] + \
    #         levresults['h6']
    #     quotes = levresults['blockquote']
    #     filesimages = levresults['file'] + levresults['table'] + \
    #         levresults['table'] + levresults['score'] + \
    #         levresults['media']
    #     links = levresults['linkinternal'] + levresults['linkexternal']
    #     citations = levresults['citation'] + levresults['citationneeded']
    #     normal = levresults['norm']
    #     results = (revid, 
    #                plaindist,
    #                maths,
    #                headings,
    #                quotes,
    #                filesimages,
    #                links,
    #                citations,
    #                normal)
    #     return self.gradientadjust(parentid, revid, results)

    # def gettrajdist(self, contentx, oldrev):
    #     contenty = self.dtb.getrevcontent(oldrev)[0][0] 
    #     lev = lv.fastlev.plaindist(contentx, 
    #                                contenty)
    #     return lev

    

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
                if ch == 'X':
                    flags['plotshow'] = True
        if arg == "--offline":
            flags['offline'] = True
    return flags

# def scrape(params):
#     scraper = None
#     if params["page_titles"] == "random":
#         scraper = wk.WikiRevisionScrape(
#             historylimit=params['depth_limit'],
#             pagelimit=params['scrape_limit']
#             )
#     else:
#         scraper = wk.WikiRevisionScrape(
#             historylimit=params['depth_limit'],
#             _titles=params['page_titles'],
#             upperlimit=False
#             )
#     return scraper.scrape()

# def count(revid, barheights, barlabels, title, show=False):
#     filename = title + 'count'
#     imagefile = BASEPATH + "plot/images/" + filename + ".png"
#     xaxis = 'Username'
#     yaxis = 'Contribution count'
#     title = 'User contribution counts for article "' + title + '"'.encode('utf-8')
    
#     if (show):
#         tfigsize, tdpi = None, None
#     else:
#         tfigsize, tdpi = (13,8), 600
#     fig = plt.figure(figsize=tfigsize, dpi=tdpi, tight_layout=True)
#     ax = fig.add_subplot(111)
#     h = ax.bar(xrange(len(barheights)), 
#                barheights, 
#                label=barlabels, 
#                width=0.8)
#     xticks_pos = [0.5*p.get_width() + p.get_xy()[0] for p in h]
#     ax.get_yaxis().get_major_formatter().set_scientific(False)
#     plt.xlabel(xaxis)
#     plt.ylabel(yaxis)
#     plt.title(title)
#     plt.xticks(xticks_pos, 
#                barlabels, 
#                rotation=90, 
#                ha='center')
#     if(show):
#         plt.show()
#     plt.savefig(imagefile)
#     return imagefile

# def weightdata(dbdata, weights):
#     if not weights:
#         return dbdata
#     wdata = []
#     for u in dbdata:
#         sdist = 0
#         for i,d in enumerate(u[2:]):
#             sdist = sdist + (d * (1+weights[WEIGHTLABELS[i]]))
#         wdata.append((u[0],sdist))
#     shdata = []
#     total = sum([e[1] for e in wdata])
#     for user, reward in wdata:
#         share = reward / total
#         shdata.append((u[0], share))
#     return shdata

# def getbardata(revx, pageid, database, title, datatype, weights=None, show=False):
#     dbdata = None
#     if(datatype == "count"):
#         dbdata = database.getusereditcounts(pageid)
#     elif(datatype == "reward"):
#         dbdata = weightdata(database.getuserchange(pageid),
#                             weights)      
#     sdata = sorted(dbdata, 
#                    key = lambda x: x[1])
#     barlabels = [] 
#     barheights = []
#     for i, e in enumerate(sdata):
#         barlabels.append(e[0].decode('utf-8').strip())
#         barheights.append(e[1])
#     return (revx, barheights, barlabels, title, show)

# def reward(revid, barheights, barlabels, title, show=False):
#     filename = title + 'reward'
#     imagefile = BASEPATH + "plot/images/" + filename + ".png"
#     xaxis = 'Username'
#     yaxis = 'Contribution weight'
#     title = 'User rewards for contributions to article "' + title + '"'.encode('utf-8')
#     filename = str(revid) + 'reward'
    
#     if (show):
#         tfigsize, tdpi = None, None
#     else:
#         tfigsize, tdpi = (13,8), 600
#     fig = plt.figure(figsize=tfigsize, 
#                      dpi=tdpi, 
#                      tight_layout=True)
#     ax = fig.add_subplot(111)
#     h = ax.bar(xrange(len(barheights)), 
#                barheights, 
#                label=barlabels, 
#                width=0.8)
#     xticks_pos = [0.5*p.get_width() + p.get_xy()[0] for p in h]
#     ax.get_yaxis().get_major_formatter().set_scientific(False)    
#     plt.xlabel(xaxis)
#     plt.ylabel(yaxis)
#     plt.title(title)
#     plt.xticks(xticks_pos, 
#                barlabels, 
#                rotation=90, 
#                ha='center')
#     if(show):
#         plt.show()
#     plt.savefig(imagefile)
#     return imagefile

# def gettrajdata(revx, database, title, show=False):
#     dbtraj = database.gettrajectory(revx)
#     traj = [e[1] for e in dbtraj]
#     dbgrowth = database.getgrowth(revx)
#     growth = [e[1] for e in dbgrowth]
#     creation = dbtraj[0][0]
#     times = [(e[0]-creation).total_seconds()/3600 for e in dbtraj]   
#     return (revx, times, traj, growth, title, show)

# def trajectory(revid, times, trajectory, growth, title, show=False):
#     ##prepare text
#     filename = title + 'traj'
#     imagefile = BASEPATH + "plot/images/" + filename + ".png"
#     xaxis = 'Hours since article creation'
#     yaxis1 = 'Edit distance from final'
#     yaxis2 = 'Article length'
#     title = 'Edit trajectory towards revision ' + str(revid) + ', article \'' + title + '\''.encode('utf-8')
 
#     ##prepare matplotlib
#     if (show):
#         tfigsize, tdpi = None, None
#     else:
#         tfigsize, tdpi = (13,8), 600
#     fig = plt.figure(figsize=tfigsize, 
#                      dpi=tdpi, 
#                      tight_layout=None)
#     ax1 = fig.add_subplot(111)
#     ax1.plot(times, trajectory, 'bo-', label='Edit distance from final')
#     ax1.set_xlabel(xaxis)
#     ax1.set_ylabel(yaxis1, color='b')
#     ax1.get_yaxis().get_major_formatter().set_scientific(False)
#     ax2 = ax1.twinx()
#     ax2.plot(times, growth, 'ko-', label='Article length')
#     ax2.set_ylabel(yaxis2, color='k')
#     ax2.get_yaxis().get_major_formatter().set_scientific(False)
#     for tl in ax1.get_yticklabels():
#         tl.set_color('b')
#     plt.title(title)
#     if(show):
#         plt.show()
#     plt.savefig(imagefile)
#     return imagefile

def getweights(weights):
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

# def gradientadjust(parentid, revid, distuple, database):
#     x = (database.gettime((revid,)) - \
#              database.gettime((parentid,))).total_seconds()/3600
#     #x = 200
#     y = database.gettrajheight((revid,)) - database.gettrajheight((parentid,))
#     if x < 0:
#         print "Error: Time travel"
#     elif not x:
#         return wdata
#     gradconst = 0.5 - m.atan(y/x)/m.pi
#     return tuple([revid] + [d*gradconst for d in distuple[1:]])

# def processweights(parentid, revid, database):
#     contentx = database.getrevcontent(parentid)[0][0]
#     contenty = database.getrevcontent(revid)[0][0]
#     levresults = lv.fastlev.weightdist(contentx, contenty)
#     # lev = lv.fastlev.plaindist(contentx,contenty)
#     # if lev != levresults['dist']:
#     #     print lev, levresults['dist']
#     #     print levresults
#     plaindist = levresults['dist']
#     maths = levresults['maths1'] + levresults['maths2']
#     headings = levresults['h2'] + levresults['h3'] + \
#         levresults['h4'] + levresults['h4'] + levresults['h5'] + \
#         levresults['h6']
#     quotes = levresults['blockquote']
#     filesimages = levresults['file'] + levresults['table'] + \
#         levresults['table'] + levresults['score'] + \
#         levresults['media']
#     links = levresults['linkinternal'] + levresults['linkexternal']
#     citations = levresults['citation'] + levresults['citationneeded']
#     normal = levresults['norm']
#     results = (revid, 
#                plaindist,
#                maths,
#                headings,
#                quotes,
#                filesimages,
#                links,
#                citations,
#                normal)
#     return gradientadjust(parentid, revid, results, database)
    
# def gettrajdist(contentx, oldrev, database):
#     contenty = database.getrevcontent(oldrev)[0][0] 
#     lev = lv.fastlev.plaindist(contentx, 
#                                contenty)
#     return lev
# 
# def analyse(params, flags):
#     repeat = 1;
#     if(params['scrape_limit'] != -1):
#         repeat = params['scrape_limit']
#     params['scrape_limit'] = 1
#     database = db.Database()
#     pageid = None
#     if flags['offline']:
#         params['titles'], pageid = database.getrandom()
#         print "Fetching random article from database,", params['titles']
#         pageids = [pageid]
#         titles = [params['titles']]
#     else:
#         titles, pageids = scrape(params)
#     pagecount = 0
#     for t, pageid in enumerate(pageids):
#         print "Analysing", titles[t]
#         revs = [e[0] for e in database.getextantrevs(pageid)]
#         revx, oldrevs = revs[-1], revs[:-1]
#         contentx = database.getrevcontent(revx)[0][0]   
#         print "Tracing trajectory", len(revs), "revisions"
#         for oldrev in oldrevs:
#             gettrajdist(revx, oldrev)
#             # dist1 = database.gettraj([revx, 
#             #                           oldrev])
#             # if not dist1:       
#             #     database.trajinsert((revx, 
#             #                          oldrev, 
#             #                          gettrajdist(contentx, 
#             #                                      oldrev, 
#             #                                      database)))
#             dot()
#         print "\nCalculating pairs"
#         creward, i, v = 0, 0, 1
#         while v < len(revs):
#             if not database.getdist(revs[i]):
#                 database.distinsert(self.dat.processweights(revs[v], 
#                                                             revs[i], 
#                                                             database))
#             dot((not i), (t != (len(pageids)-1)))
#             i = v
#             v = v + 1
#             pagecount = pagecount + 1
        
#         if(flags['weightsdefault']):
#             getweights(params['weights'])
            
#         print
#         print "\nAnalysis complete, saving image files:"
#         title = titles[t].replace(" ","_")
#         print trajectory(*gettrajdata(revx, 
#                                       database, 
#                                       title,
#                                       show=flags['plotshow']))
#         print count(*self.dat.getbardata(revx, 
#                                 pageid, 
#                                 database, 
#                                 title, 
#                                 "count",
#                                 show=flags['plotshow']))        
#         print reward(*self.dat.getbardata(revx, 
#                                  pageid, 
#                                  database, 
#                                  title, 
#                                  "reward",
#                                  weights=params['weights'],
#                                  show=flags['plotshow']))
#         return True

# def fetch():
#     contentparams = {}
#     contentparams.update({'titles':params['titles']})
#     if params['page_titles'] != "random" and params['revids']:
#         contentparams.update({'revids':params['revids']})
#     if params['userids']:
#         contentparams.update({'userids':params['userids']})
#     print "Fetching from database"
#     return db.getrevfull(**contentparams)

def main():
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

    
    params = _arg_sanity(params) ##ARGUMENT HANDLING
    flags = _flag_sanity(flags) ##FLAG SANITY 
    #echo_params(flags, params) ##ECHO PARAMETERS 
    
    if flags['scrape']:
        print "---------------SCRAPE MODE---------------"
        if scrape(params):
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
    # params['freward'] = 3
    # params['creward'] = 10
    
    analyser = WikiInterface(params, flags)
    if(analyser.analyse()):
        sys.exit(0)
    else:
        sys.exit(-1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nKeyboard Interrupt"
        sys.exit(0)
