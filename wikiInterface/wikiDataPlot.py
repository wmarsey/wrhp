from __future__ import division
from consts import *
from logger import logDebug
import matplotlib
import sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import database as db
from wikiDataHandle import WikiDataHandle
from random import shuffle

def movingaverage(x, n, type='exponential'):
    x = asarray(x)
    if type=='simple':
        weights = ones(n)
    else:
        weights = exp(linspace(-1., 0., n))
    weights /= weights.sum()

    a =  convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a

def safefilename(string):
    string = string.replace('/','')
    return string

##########
##########
##
## Class Plotter takes title, page ID, and domain for a page in the
## database, and gives facilities for plotting various graphs on that
## page. You can run this file as a script to get plot dumps, see the
## main function below.
##
##########
##########
class WikiDataPlot:
    def __init__(self, fileloc=None, weights=None):
        if fileloc:
            self.plotdir = fileloc + "/"
        else:
            self.plotdir = BASEPATH + "/plots/"
        
        self.weights = weights

    ##########
    ## The main function for plotting, outputs the three main types
    ##########
    def plot(self, title, pageid, domain, trajectory=True,
             editcount=True, editshare=True, weights=None):   
        filenames = []
        dat = WikiDataHandle()

        try:
            title = title.decode('utf-8')
        except:
            title = "id" + str(pageid)
        domain = domain.decode('utf-8')
        
        if trajectory:
            xpoints, tpoints, gpoints = dat.trajectorydata(pageid, domain)
            filenames.append(self.trajectory(xpoints, tpoints,
                                             gpoints,
                                             "Hours since creation",
                                             "Edit distance from final",
                                             "Article size",
                                             "Trajectory of " + safefilename(title) + ", " +\
                                                 domain + str(pageid),
                                             domain + str(pageid) + "traj",
                                             width=13, height=8))
            print "plotted", filenames[-1]
            logDebug("plotted "+ filenames[-1])

        if editcount:
            xlabels, ypoints = dat.editcountdata(pageid, domain)
            filenames.append(self.barchart(xlabels, ypoints,
                                           "Username", "Edit count",
                                           "Editors of " + safefilename(title) + ", " +
                                           domain + str(pageid) + ", by edit count", 
                                           domain + str(pageid) + "editc",
                                           width = 13, height = 8))
            print "plotted", filenames[-1]
            logDebug("plotted "+ filenames[-1])

        if editshare:
            xlabels, ypoints = dat.editsharedata(pageid, domain, self.weights)
            filenames.append(self.barchart(xlabels, ypoints,
                                           "Username", "Edit share", 
                                           "Editors of " + safefilename(title) + ", " + domain\
                                               + str(pageid) + ", by share", 
                                           domain + str(pageid) + "share",
                                           width = 13, height = 8))
            print "plotted", filenames[-1]
            logDebug("plotted "+ filenames[-1])

        return filenames
            
    
    ##########
    ## Dumps a plot of a large number of different-weight share plots
    ## for comparison
    ##########
    def weightplot(self,clip=1):       
        dtb = db.WikiDatabase()
        pages = dtb.getallfetched()
        print "got", len(pages)

        import itertools
        possw = list(itertools.product([0,1], repeat=6))

        shuffle(pages)
        for r in pages[:clip]:
            article = r[0].decode('utf-8')
            pageid = r[1]
            domain = r[2]
            xaxisname = "Username"
            yaxisname = "Edit share",
            title = "Editors of " + safefilename(article) 
            title += ", " + domain + str(pageid) + ", by edit count"
            filename = domain + str(pageid) + "editcW"

            dbdata = dtb.getuserchange2(pageid,domain)
            dat = WikiDataHandle()

            xlz = []
            ylz = [[],[]]
            for w in possw:
                for d in (0,1):
                    ww = list(w + (d,))
                    f = filename + str(ww)
                    xlabels, ypoints = dat.editsharedata(pageid,domain,weights=ww,
                                                         namesort=True,dbdata=dbdata)
                    xlz = xlabels
                    ylz[d].append(ypoints)

            realy = [[],[]]
            for i,y in enumerate(ylz):
                yy = zip(*y)
                yyy = [sum(e) for e in yy]
                assert len(yyy) == len(xlz)
                realy[i] = yyy
            
            xf = []
            yf = [[],[]]
            for i,y in enumerate(realy):
                f = filename + "average" + "G" + str(i)
                comb = zip(xlz,y)
                comb = sorted(comb, key = lambda x: x[1])
                xf, yf[i] = zip(*comb) 
                xpoints = list(range(len(xf)))
            print self.specialtrajectory(xpoints, yf[0], xpoints,
                                         yf[1], None, None, None,
                                         xaxisname, yaxisname, None,
                                         title, filename, width=20, height=12)

    ##########
    ## Gets a dump of all talk pages in the database, plots them
    ## against their respective articles
    ##########
    def talkplots(self):
        dat = WikiDataHandle()

        titles, pids, tids, domains = dat.talkpages()
        

        for i in range(len(titles)):
            domain = domains[i]
            pageid = pids[i]
            talkid = tids[i]
            title = titles[i]
        
            print title, pageid

            try:
                x1, t1, _ = dat.trajectorydata(pageid, domain, normalise=False)
                x2, t2, growth = dat.trajectorydata(talkid, domain, normalise=False)
            except:
                continue

            t1sum = max(t1) 
            if t1sum:
                for i in xrange(len(t1)):
                    t1[i] /= t1sum

            t2sum = max(t2)
            if t2sum:
                for i in xrange(len(t2)):
                    t2[i] /= t2sum

            gsum = max(growth)
            if gsum:
                for i in xrange(len(growth)):
                    growth[i] /= gsum

            creation = min(x1[0],x2[0])
            for x in (x1, x2):
                for i in xrange(len(x)):
                    x[i] = (x[i]-creation).total_seconds()/3600

            title = title.decode('utf-8').replace('/','') + " article vs talk page trajectories"
            xaxisname = "Hours since creation"
            taxisname = "Change"
            gaxisname = "Article page size"
            filename = domain + str(pageid) + " Special Combo"

            print self.talktrajectory(x1, t1, x2, t2, growth,
                                         xaxisname, taxisname, gaxisname,
                                         title, filename, width=20, height=12)

    ##########
    ## Plots two trajectories against one another, talkpage and
    ## article
    ##########
    def talktrajectory(self, xpoints1, tpoints1, xpoints2, tpoints2,
                     gpoints, xaxisname, taxisname, gaxisname, title,
                     filename, width=13, height=8):

        imagefile = self.plotdir + filename + " " + title + ".png"
        
        fig = plt.figure(figsize=(width,height), 
                         dpi=600, 
                         tight_layout=None)
        
        ax1 = fig.add_subplot(111)
        if gpoints:
            ax1.plot(xpoints2, gpoints, 'ko-', label='Article length')
        ax1.plot(xpoints1, tpoints1, 'ro-', label='Talk page trajectory')
        ax1.plot(xpoints2, tpoints2, 'go-', label='Article page trajectory')
        ax1.set_xlabel(xaxisname)
        ax1.set_ylabel(taxisname)
        ax1.get_yaxis().set_ticks([])
        
        ax1.legend(loc='upper left')

        for tl in ax1.get_yticklabels():
            tl.set_color('b')
        plt.title(title)
 
        plt.savefig(imagefile)
        return imagefile        

    ##########
    ## Generic bar chart function
    ##########
    def barchart(self, xlabels, ypoints, xaxisname, yaxisname, title, 
                  filename, width=13, height=8):
        imagefile = self.plotdir + filename +  " " + title + ".png"
        
        fig = plt.figure(figsize=(width,height), dpi=600, tight_layout=True)

        ax = fig.add_subplot(111)
        h = ax.bar(xrange(len(ypoints)), 
                   ypoints, 
                   label=xlabels, 
                   width=0.8)
        xticks_pos = [0.5*p.get_width() + p.get_xy()[0] for p in h]
        ax.get_yaxis().get_major_formatter().set_scientific(False)

        plt.xlabel(xaxisname)
        plt.ylabel(yaxisname)

        plt.title(title)
        plt.xticks(xticks_pos, 
                   xlabels, 
                   rotation=90, 
                   ha='center')
        plt.xlim([0,len(xlabels)])
 
        plt.savefig(imagefile)
        return imagefile

    def linechart(self, xpoints, ypoints, xaxisname, yaxisname, title, 
                  filename, width=13, height=6, xlog=False, ylog=False):
        imagefile = self.plotdir + filename + ".png"
        
        fig = plt.figure(figsize=(width, height), dpi=600, tight_layout=True)

        ax1 = fig.add_subplot(111)

        ax1.plot(xpoints,ypoints, 'rx')

        ax1.set_xlabel(xaxisname)
        ax1.set_ylabel(yaxisname, color='b')

        if ylog:
            ax1.set_yscale('log')
        if xlog:
            ax1.set_xscale('log')
        
        plt.title(title)

        plt.savefig(imagefile)
        return imagefile

    def histogram(self, xpoints, ypoints, xaxisname, yaxisname, 
                  title, filename, width=13, height=6):
        imagefile = self.plotdir + filename + ".png"
        
        fig = plt.figure(figsize=(width, height), dpi=600, tight_layout=True)

        ax1 = fig.add_subplot(111)

        n, bins, patches = ax1.hist(ypoints, bins=(len(xpoints)//2))

        ax1.set_xlabel(xaxisname)
        ax1.set_ylabel(yaxisname, color='b')
        
        plt.title(title)

        plt.savefig(imagefile)
        return imagefile

    ##########
    ## Specialised trajectory-plotting diagram
    ##########
    def trajectory(self, xpoints, tpoints, gpoints, xaxisname, taxisname,
                    gaxisname, title, filename, width=13, height=8):
        
        #filename = domain + str(pageid) + 'traj'
        imagefile = self.plotdir + filename + " " + title + ".png"
        
        ##prepare matplotlib
        fig = plt.figure(figsize=(width,height), 
                         dpi=600, 
                         tight_layout=None)

        ax1 = fig.add_subplot(111)
        ax1.plot(xpoints, tpoints, 'bo-', label='Edit distance from final')

        ax1.set_xlabel(xaxisname)
        ax1.set_ylabel(taxisname, color='b')
        ax1.get_yaxis().get_major_formatter().set_scientific(False)
        
        ax2 = ax1.twinx()
        ax2.plot(xpoints, gpoints, 'ko-', label='Article length')
        ax2.set_ylabel(gaxisname, color='k')
        ax2.get_yaxis().get_major_formatter().set_scientific(False)
        for tl in ax1.get_yticklabels():
            tl.set_color('b')
        plt.title(title)
 
        plt.savefig(imagefile)
        return imagefile

    ##########
    ## For collecting large numbers of plots
    ##########
    def dumpplot(self, clip=200):
        dtb = db.WikiDatabase()
        pages = dtb.getallfetched()
        shuffle(pages)
        for r in pages[:clip]:
            try:
                self.plot(*r)
            except:
                pass

##########
## For running as a script, getting dump plots. used to prepare
## for report.
##########
def main():
    p = WikiDataPlot()
    if "--dump" in sys.argv:
        if "--clip" in sys.argv:
            p.dumpplot(int(sys.argv[sys.argv.index("--clip") + 1]))
        else: 
            p.dumpplot()
    if "--talk" in sys.argv:
        p.talkplots()
    if "--weight" in sys.argv:
        if "--clip" in sys.argv:
            p.weightplot(int(sys.argv[sys.argv.index("--clip") + 1]))
        else: 
            p.weightplot()
        
if __name__ == "__main__":
    main()
