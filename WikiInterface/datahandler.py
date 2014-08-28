#from weighteddistance import WDistanceCalc
from __future__ import division 
import database as db
#import lshtein as lv
import math as m

class DHandler:
    dtb = None

    def __init__(self):
        self.dtb = db.Database()

    def trajectorydata(self, pageid, domain):
        tdata = self.dtb.gettrajectory(pageid, domain)
        gdata = self.dtb.getgrowth(pageid, domain)
        creation = tdata[0][0]
        
        tpoints = [e[1] for e in tdata]
        gpoints = [e[1] for e in gdata]
        xpoints = [(e[0]-creation).total_seconds()/3600 for e in tdata]
        
        return xpoints, tpoints, gpoints

    def editcountdata(self, pageid, domain):
        dtb = db.Database()

        dbdata = self.dtb.getusereditcounts(pageid, domain)
        sdata = sorted(dbdata, key = lambda x: x[1])

        xlabels, ypoints = zip(*sdata)
        xlabels = [e.decode('utf-8').strip() for e in xlabels]

        return xlabels, ypoints

    def editsharedata(self, pageid, domain, weights=None):
        dtb = db.Database()

        dbdata = dtb.getuserchange(pageid, domain)

        wdata = []
        for u in dbdata:
            sdist = 0
            for i,d in enumerate(u[2:]):
                w = weights[WEIGHTLABELS[i]] if weights else 0
                sdist = sdist + (d * (1+w))
            wdata.append([u[0],sdist])

        total = sum([e[1] for e in wdata])
        for w in wdata:
            w[1] /= total
        
        wdata = sorted(wdata, key = lambda x: x[1])

        xlabels, ypoints = zip(*wdata)
        xlabels = [e.decode('utf-8').strip() for e in xlabels]
            
        return xlabels, ypoints

    def getweights(self, pageid, domain):
        wdata = []
        for u in self.dtb.getuserchange(pageid, domain):
            w = {
                'math':u[2],
                'heading':u[3],
                'quotes':u[4],
                'filesimages':u[5],
                'links':u[6],
                'citations':u[7],
                'normal':u[8],
                }
            wdata.append((u[0],w))
        return wdata
