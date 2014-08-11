from consts import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
