#from weighteddistance import WDistanceCalc
from __future__ import division 
import database as db
#import lshtein as lv
import math as m
from time import mktime

class DHandler:
    dtb = None

    def __init__(self):
        self.dtb = db.Database()

    def trajectorydata(self, pageid, domain, normalise=True):
        tdata = self.dtb.gettrajectory(pageid, domain)
        gdata = self.dtb.getgrowth(pageid, domain)

        tpoints = [e[1] for e in tdata]
        gpoints = [e[1] for e in gdata]
        if normalise:
            creation = tdata[0][0]
            xpoints = [(e[0]-creation).total_seconds()/3600 for e in tdata]
        else:
            #xpoints = [mktime(e[0].timetuple()) for e in tdata]
            xpoints = [e[0] for e in tdata]

        return xpoints, tpoints, gpoints

    def editcountdata(self, pageid, domain):
        dtb = db.Database()

        dbdata = self.dtb.getusereditcounts(pageid, domain)
        sdata = sorted(dbdata, key = lambda x: x[1])

        xlabels, ypoints = zip(*sdata)
        xlabels = [e.decode('utf-8').strip() for e in xlabels]

        return xlabels, ypoints

    def editsharedata(self, pageid, domain, weights=None, namesort=None, dbdata=None):
        dtb = db.Database()

        dbdata = dbdata if dbdata else dtb.getuserchange2(pageid, domain)

        if weights:
            assert len(dbdata[0][1:-1])+1 == len(weights)
            
        gradients = [u[-1] for u in dbdata]
        #gradients = sorted(gradients)
        # print "gradient range", min(gradients), "to", max(gradients), "average", sum(gradients)/len(gradients)

        users = {}
        for u in dbdata:
            sdist = 0
            for i,d in enumerate(u[1:-1]):
                w = weights[i] if weights else 0
                sdist += (d * (1+w))
            w = weights[-1] if weights else 0
            tot = sdist * (u[-1]) if w else sdist
            if u[0] in users:
                users[u[0]] += tot
            else:
                users.update({u[0]:tot})
        
        wdata = []
        for key, val in users.iteritems():
            wdata.append([key,val])

        total = sum([e[1] for e in wdata])
        for w in wdata:
            w[1] /= total
            
        wdata = sorted(wdata, key = lambda x: x[0 if namesort else 1])

        xlabels, ypoints = zip(*wdata)
        xlabels = [e.decode('utf-8').strip() for e in xlabels]
            
        return xlabels, ypoints

    # def getweights(self, pageid, domain):
    #     wdata = []
    #     for u in self.dtb.getuserchange(pageid, domain):
    #         w = {
    #             'math':u[2],
    #             'heading':u[3],
    #             'quotes':u[4],
    #             'filesimages':u[5],
    #             'links':u[6],
    #             'citations':u[7],
    #             'normal':u[8],
    #             }
    #         wdata.append((u[0],w))
    #     return wdata
