from __future__ import division
from consts import *
import matplotlib
import sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import database as db
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

class Plotter:
    def trajectorydata(self, pageid, domain):
        dtb = db.Database()

        tdata = dtb.gettrajectory(pageid, domain)
        gdata = dtb.getgrowth(pageid, domain)
        creation = tdata[0][0]
        
        tpoints = [e[1] for e in tdata]
        gpoints = [e[1] for e in gdata]
        xpoints = [(e[0]-creation).total_seconds()/3600 for e in tdata]
        
        return xpoints, tpoints, gpoints

    def editcountdata(self, pageid, domain):
        dtb = db.Database()

        dbdata = dtb.getusereditcounts(pageid, domain)
        sdata = sorted(dbdata, key = lambda x: x[1])

        xlabels, ypoints = zip(*sdata)
        xlabels = [e.decode('utf-8').strip() for e in xlabels]

        return xlabels, ypoints

    def editsharedata(self, pageid, domain, weights=None):
        dtb = db.Database()

        dbdata = dtb.getuserchange(pageid, domain)
        
        # Is this too python?
        # wdata = [(d[0], sum([e*(1+weights[WEIGHTLABELS[i]] if weights else 1)\
        #                   for i,e in enumerate(d[2:])])) for d in dbdata]

        wdata = []
        for u in dbdata:
            sdist = 0
            for i,d in enumerate(u[2:]):
                w = weights[WEIGHTLABELS[i]] if weights else 0
                sdist = sdist + (d * (1+w))
            wdata.append((u[0],sdist))

        total = sum([e[1] for e in wdata])
        for w in wdata:
            w[1] /= total
        
        wdata = sorted(wdata, key = lambda x: x[1])

        xlabels, ypoints = zip(*sdata)
        xlabels = [e.decode('utf-8').strip() for e in xlabels]
            
        return xlabels, ypoints

    def plot(self,
             title,
             pageid,
             domain,
             trajectory=True,
             editcount=True,
             share=True,
             weights=None):
        
        filenames = []

        if trajectory:
            xpoints, tpoints, gpoints = self.trajectorydata(pageid, domain)
            filenames.append(self.trajectory2(xpoints, 
                                              tpoints, 
                                              gpoints,
                                              "Hours since creation",
                                              "Edit distance from final",
                                              "Article size",
                                              "Trajectory of " + title + ", " + domain + str(pageid),
                                              domain + str(pageid) + "traj",
                                              width=13,
                                              height=8))

        if share:
            xlabels, ypoints = self.editcountdata(pageid, domain)
            filenames.append(self.barchart2(xlabels, ypoints,
                                       "Username", "Edit count",
                                       "Editors of " + title + ", " +
                                       domain + str(pageid) + ", by edit count", 
                                       domain + str(pageid) + "editc"))

        if editcount:
            xlabels, ypoints = self.editsharedata(pageid, domain)
            filenames.append(self.barchart2(xlabels, 
                                       ypoints, 
                                       "Username", 
                                       "Edit share", 
                                       "Editors of " + title + ", " + domain + str(pageid) + ", by share", 
                                       domain + str(pageid) + "share"))

            

    def barchart2(self, xlabels, ypoints, xaxisname, yaxisname, title, 
                  filename, width=13, height=8):
        imagefile = BASEPATH + "plot/images/" + filename + ".png"
        
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

    def barchart(self, revid, barheights, barlabels, pageid, domain, 
                 title, ident, xaxisname, yaxisname, width=13, height=8): 
        filename = domain + str(pageid) + ident
        imagefile = BASEPATH + "plot/images/" + filename + ".png"
        
        tfigsize, tdpi = (width,height), 600
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
        plt.xlim([0,len(barlabels)])

 
        plt.savefig(imagefile)
        return imagefile

    def linechart(self, xpoints, ypoints, xaxisname, yaxisname, title, 
                  filename, width=13, height=6, xlog=False, ylog=False):
        imagefile = BASEPATH +"plot/images/" + filename + ".png"
        
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
        imagefile = BASEPATH +"plot/images/" + filename + ".png"
        
        fig = plt.figure(figsize=(width, height), dpi=600, tight_layout=True)

        ax1 = fig.add_subplot(111)

        n, bins, patches = ax1.hist(ypoints, bins=(len(xpoints)//2))

        ax1.set_xlabel(xaxisname)
        ax1.set_ylabel(yaxisname, color='b')

        
        plt.title(title)

        plt.savefig(imagefile)
        return imagefile

    def trajectory2(self, xpoints, tpoints, gpoints, xaxisname, taxisname,
                    gaxisname, title, filename, width=13, height=8):
        
        #filename = domain + str(pageid) + 'traj'
        imagefile = BASEPATH + "plot/images/" + filename + ".png"
        
        ##prepare matplotlib
        tfigsize, tdpi = (width,height), 600
        fig = plt.figure(figsize=tfigsize, 
                         dpi=tdpi, 
                         tight_layout=None)

        ax1 = fig.add_subplot(111)
        ax1.plot(xpoints, tpoints, 'bo-', label='Edit distance from final')

        ax1.set_xlabel(xpoints)
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
    
    def trajectory(self, revid, times, trajectory, growth, pageid, domain, _title):
        ##prepare text
        filename = domain + str(pageid) + 'traj'
        imagefile = BASEPATH + "plot/images/" + filename + ".png"
        xaxis = 'Hours since article creation'
        yaxis1 = 'Edit distance from final'
        yaxis2 = 'Article length'
        title = _title

        ##prepare matplotlib
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
 
        plt.savefig(imagefile)
        return imagefile

    def dumpplot(self, clip=200):
        dtb = db.Database()
        
        ##PAGE-WISE PLOTS
        pages = dtb.getallfetched()
        shuffle(pages)
        for r in pages[:clip]:
            pageid = r[0]
            domain = r[1]
            title = dtb.gettitle(pageid, domain).decode('utf-8')
            xrev = dtb.getyoungestrev(pageid, domain)

            ##TRAJECTORY DATA
            trajdata = dtb.gettrajectory(xrev, domain)
            growthdata = dtb.getgrowth(xrev, domain)
            creation = trajdata[0][0]

            ##TRAJECTORY PLOT
            traj = [e[1] for e in trajdata]
            growth = [e[1] for e in growthdata]
            times = [(e[0]-creation).total_seconds()/3600 for e in trajdata]
            print self.trajectory(xrev, times, traj, growth, pageid, domain, title)
            
            ##UNWEIGHTED USERSHARE
            userdata = dtb.getuserchange(pageid, domain)
            userdata.sort(key=lambda x: x[1])
            unames = [e[0].decode('utf-8') for e in userdata]
            shares = [sum(e[1:]) for e in userdata]
            total = sum(shares)
            shares = [e/total for e in shares]
            xaxis = 'users'
            yaxis = 'share'
            print self.barchart(xrev, shares, unames, pageid, domain, title, 'users', xaxis, yaxis)

            ##EDIT COUNT
            userdata = dtb.getusereditcounts(pageid, domain)
            unames, shares = zip(*userdata)
            unames = tuple(e.decode('utf-8') for e in unames)
            yaxis = 'edit count'
            print self.barchart(xrev, shares, unames, pageid, domain, title, 'users', xaxis, yaxis)

    def metricplots(self):
        dtb = db.Database()

        y = dtb.gettexttypedistribution('en')[0]
        xlabels = ['maths', 'citations', 'filesimages', 'links', 'structure', 'normal']
        print self.barchart(0, 
                            y, 
                            xlabels, 
                            000, 
                            'en', 
                            "English Wikipedia, Text type change frequency", 
                            'users', 
                            "Text types", 
                            "Change count",
                            width=8,
                            height=5)
        y = dtb.gettexttypedistribution('en')[0]
        xlabels = ['maths', 'citations', 'filesimages', 'links', 'structure', 'normal']
        print self.barchart(0, 
                            y, 
                            xlabels, 
                            000, 
                            'en', 
                            "All Wikipedias, Text type change frequency", 
                            'users', 
                            "Text types", 
                            "Change count",
                            width=8,
                            height=5)


        ##### RARENESS
        ### GET ALL CONTENT
        ### REGEX SUMS

        x, y = zip(*dtb.geteditdistribution('en'))
        print self.histogram(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "English Wikipedia: User edit counts, random sample", 
                             "0editdistributionhisto")

        x, y = zip(*dtb.getregeditdistribution('en'))
        print self.histogram(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "English Wikipedia: Registered users edit counts, random sample", 
                             "0regeditdistributionhisto")

        x, y = zip(*dtb.geteditdistribution())
        print self.histogram(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
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
        print self.linechart(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "English Wikipedia: User edit counts, random sample", 
                             "0editdistribution")
        print self.linechart(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "English Wikipedia: User edit counts, random sample", 
                             "0editdistributionlog", ylog=True)

        x, y = zip(*dtb.getregeditdistribution('en'))
        print self.linechart(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "English Wikipedia: Registered users edit counts, random sample", 
                             "0regeditdistribution")
        print self.linechart(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "English Wikipedia: Registered users edit counts, random sample", 
                             "0regeditdistributionlog", ylog=True)

        x, y = zip(*dtb.geteditdistribution())
        print self.linechart(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "All Wikipediaa: User edit counts, random sample", 
                             "0editdistributionall")
        print self.linechart(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "All Wikipedias: User edit counts, random sample", 
                             "0editdistributionalllog", ylog=True)

        x, y = zip(*dtb.getregeditdistribution())
        print self.linechart(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "All Wikipediaa: Registered users edit counts, random sample", 
                             "0regeditdistributionall")
        print self.linechart(x, 
                             y, 
                             "Edit count", 
                             "Frequency", 
                             "All Wikipediaa: Registered users edit counts, random sample", 
                             "0regeditdistributionalllog", ylog=True)

        ##AVERAGE HISTORY LENGTH BY DOMAIN
        historylengths = dtb.getaveragerevisioncounts()
        domains, lengths = zip(*historylengths)
        xaxis = 'Domain'
        yaxis = 'Average article history lengths'
        print self.barchart(000, 
                            lengths, 
                            domains, 
                            0, 
                            '', 
                            '', 
                            'avpageactivity', 
                            xaxis, 
                            yaxis, 
                            width=30, 
                            height=10)

        ##AVERAGE ARTICLE LENGTH BY DOMAIN
        pagelengths = dtb.getaveragepagelengths()
        domains, lengths = zip(*pagelengths)
        xaxis = 'Domain'
        yaxis = 'Average article length'
        print self.barchart(000, 
                            lengths, 
                            domains, 
                            0, 
                            '', 
                            '', 
                            'avpagelen', 
                            xaxis, 
                            yaxis, 
                            width=30, 
                            height=10)

    # def fetch():
    #     contentparams = {}
    #     contentparams.update({'titles':self.params['titles']})
    #     if self.params['page_titles'] != "random" and self.params['revids']:
    #         contentparams.update({'revids':self.params['revids']})
    #     if self.params['userids']:
    #         contentparams.update({'userids':self.params['userids']})
    #     print "Fetching from database"
    #     return db.getrevfull(**contentparams)

def main():
    p = Plotter()
    if "--dump" in sys.argv:
        if "--clip" in sys.argv:
            p.dumpplot(sys.argv[sys.argv.index("--index") + 1])
        else: 
            p.dumpplot()
    if "--metrics" in sys.argv:
        p.metricplots()
        

if __name__ == "__main__":
    main()
