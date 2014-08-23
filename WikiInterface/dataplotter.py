from __future__ import division
from consts import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import database as db
from random import shuffle

class Plotter:
    def barchart(self, revid, barheights, barlabels, pageid, domain, title, ident, xaxisname, yaxisname, show=False, width=13, height=8): 
        filename = domain + str(pageid) + ident
        imagefile = BASEPATH + "plot/images/" + filename + ".png"
        if (show):
            tfigsize, tdpi = None, None
        else:
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
        if(show):
            plt.show()
        plt.savefig(imagefile)
        return imagefile

    def trajectory(self, revid, times, trajectory, growth, pageid, domain, _title, show=False):
        ##prepare text
        filename = domain + str(pageid) + 'traj'
        imagefile = BASEPATH + "plot/images/" + filename + ".png"
        xaxis = 'Hours since article creation'
        yaxis1 = 'Edit distance from final'
        yaxis2 = 'Article length'
        title = _title

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

    def dumpplot(self):
        dtb = db.Database()
        
        ##PAGE-WISE PLOTS
        pages = dtb.getallfetched()
        shuffle(pages)
        for r in pages[:10]:
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

        
        ##AVERAGE HISTORY LENGTH BY DOMAIN
        historylengths = dtb.getaveragerevisioncounts()
        domains, lengths = zip(*historylengths)
        xaxis = 'Domain'
        yaxis = 'Average article history lengths'
        print self.barchart(000, lengths, domains, 0, '', '', 'avpageactivity', xaxis, yaxis, width=30, height=10)

        ##AVERAGE ARTICLE LENGTH BY DOMAIN
        pagelengths = dtb.getaveragepagelengths()
        domains, lengths = zip(*pagelengths)
        xaxis = 'Domain'
        yaxis = 'Average article length'
        print self.barchart(000, lengths, domains, 0, '', '', 'avpagelen', xaxis, yaxis, width=30, height=10)

    def fetch():
        contentparams = {}
        contentparams.update({'titles':self.params['titles']})
        if self.params['page_titles'] != "random" and self.params['revids']:
            contentparams.update({'revids':self.params['revids']})
        if self.params['userids']:
            contentparams.update({'userids':self.params['userids']})
        print "Fetching from database"
        return db.getrevfull(**contentparams)

def main():
    p = Plotter()
    p.dumpplot()

if __name__ == "__main__":
    main()
