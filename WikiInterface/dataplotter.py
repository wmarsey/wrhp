from __future__ import division
from consts import *
import matplotlib
import sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import database as db
from datahandler import DHandler
from random import shuffle
from numpy import polyfit, poly1d, linspace, convolve, exp, ones, asarray

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

class Plotter:
    def __init__(self, fileloc=None):
        if fileloc:
            self.plotdir = fileloc + "/"
        else:
            self.plotdir = BASEPATH + "/plot/images/"

    def plot(self, title, pageid, domain, trajectory=True,
             editcount=True, share=True, weights=None):   
        filenames = []
        dat = DHandler()

        title = title.decode('utf-8')
        domain = domain.decode('utf-8')
        
        if trajectory:
            xpoints, tpoints, gpoints = dat.trajectorydata(pageid, domain)
            filenames.append(self.trajectory(xpoints, tpoints,
                                             gpoints,
                                             "Hours since creation",
                                             "Edit distance from final",
                                             "Article size",
                                             "Trajectory of " + safefilename(title) + ", " + domain + str(pageid),
                                             domain + str(pageid) + "traj",
                                             width=13, height=8))
            print "plotted", filenames[-1]

        if share:
            xlabels, ypoints = dat.editcountdata(pageid, domain)
            filenames.append(self.barchart(xlabels, ypoints,
                                           "Username", "Edit count",
                                           "Editors of " + safefilename(title) + ", " +
                                           domain + str(pageid) + ", by edit count", 
                                           domain + str(pageid) + "editc",
                                           width = 13, height = 8))
            print "plotted", filenames[-1]

        if editcount:
            xlabels, ypoints = dat.editsharedata(pageid, domain)
            filenames.append(self.barchart(xlabels, ypoints,
                                           "Username", "Edit share", 
                                           "Editors of " + safefilename(title) + ", " + domain + str(pageid) + ", by share", 
                                           domain + str(pageid) + "share",
                                           width = 13, height = 8))
            print "plotted", filenames[-1]

        return filenames
            

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

    def dumpplot(self, clip=200):
        dtb = db.Database()
        pages = dtb.getallfetched()
        shuffle(pages)
        for r in pages[:clip]:
            self.plot(*r)
 
    def metricplots(self):
        dtb = db.Database()
        y = dtb.gettexttypedistribution('en')[0]
        xlabels = ['maths', 'citations', 'filesimages', 'links', 'structure', 'normal']
        print self.barchart(0, y, xlabels, 000, 'en',
                            "English Wikipedia, Text type change frequency", 
                            'users', "Text types", "Change count",
                            width=8, height=5)
        y = dtb.gettexttypedistribution('en')[0]
        xlabels = ['maths', 'citations', 'filesimages', 'links', 'structure', 'normal']
        print self.barchart(0, y, xlabels, 000, 'en',
                            "All Wikipedias, Text type change frequency", 
                            'users', "Text types", "Change count",
                            width=8, height=5)


        x, y = zip(*dtb.geteditdistribution('en'))
        print self.histogram(x, y, "Edit count", "Frequency", 
                             "English Wikipedia: User edit counts, random sample", 
                             "0editdistributionhisto")

        x, y = zip(*dtb.getregeditdistribution('en'))
        print self.histogram(x, y, "Edit count", "Frequency",
                             "English Wikipedia: Registered users edit counts, random sample", 
                             "0regeditdistributionhisto")

        x, y = zip(*dtb.geteditdistribution())
        print self.histogram(x, y, "Edit count", "Frequency",
                             "All Wikipediaa: User edit counts, random sample", 
                             "0editdistributionallhisto")

        x, y = zip(*dtb.getregeditdistribution())
        print self.histogram(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "All Wikipediaa: Registered users edit counts, random sample", 
                             "0regeditdistributionallhisto")


        x, y = zip(*dtb.geteditdistribution('en'))
        print self.linechart(x, y, "Edit count", "Frequency",
                             "English Wikipedia: User edit counts, random sample", 
                             "0editdistribution")
        print self.linechart(x, y, "Edit count", "Frequency",
                             "English Wikipedia: User edit counts, random sample", 
                             "0editdistributionlog", ylog=True)

        x, y = zip(*dtb.getregeditdistribution('en'))
        print self.linechart(x, y, "Edit count", "Frequency",
                             "English Wikipedia: Registered users edit counts, random sample", 
                             "0regeditdistribution")
        print self.linechart(x, y, "Edit count", "Frequency",
                             "English Wikipedia: Registered users edit counts, random sample", 
                             "0regeditdistributionlog", ylog=True)

        x, y = zip(*dtb.geteditdistribution())
        print self.linechart(x, y, "Edit count", "Frequency",
                             "All Wikipediaa: User edit counts, random sample", 
                             "0editdistributionall")
        print self.linechart(x, y, "Edit count", "Frequency",
                             "All Wikipedias: User edit counts, random sample", 
                             "0editdistributionalllog", ylog=True)

        x, y = zip(*dtb.getregeditdistribution())
        print self.linechart(x, y, "Edit count", "Frequency", 
                             "All Wikipediaa: Registered users edit counts, random sample", 
                             "0regeditdistributionall")
        print self.linechart(x, y, "Edit count", "Frequency",
                             "All Wikipediaa: Registered users edit counts, random sample", 
                             "0regeditdistributionalllog", ylog=True)

        ##AVERAGE HISTORY LENGTH BY DOMAIN
        historylengths = dtb.getaveragerevisioncounts()
        domains, lengths = zip(*historylengths)
        xaxis = 'Domain'
        yaxis = 'Average article history lengths'
        print self.barchart(000, lengths, domains, 0, '', '',
                            'avpageactivity', xaxis, yaxis, width=30,
                            height=10)

        ##AVERAGE ARTICLE LENGTH BY DOMAIN
        pagelengths = dtb.getaveragepagelengths()
        domains, lengths = zip(*pagelengths)
        xaxis = 'Domain'
        yaxis = 'Average article length'
        print self.barchart(000, lengths, domains, 0, '', '',
                            'avpagelen', xaxis, yaxis, width=30,
                            height=10)

def main():
    p = Plotter()
    if "--dump" in sys.argv:
        if "--clip" in sys.argv:
            p.dumpplot(int(sys.argv[sys.argv.index("--clip") + 1]))
        else: 
            p.dumpplot()
    if "--metrics" in sys.argv:
        p.metricplots()
        

if __name__ == "__main__":
    main()
