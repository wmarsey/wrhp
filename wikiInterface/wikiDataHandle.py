from __future__ import division 
import database as db
import math as m

class WikiDataHandle:
    dtb = None

    def __init__(self):
        self.dtb = db.WikiDatabase()

    ##########
    ## Prepares for trajectory-style diagrams
    ##########
    def trajectorydata(self, pageid, domain, normalise=True):
        tdata = self.dtb.gettrajectory(pageid, domain)
        gdata = self.dtb.getgrowth(pageid, domain)

        tpoints = [e[1] for e in tdata]
        gpoints = [e[1] for e in gdata]
        if normalise:
            creation = tdata[0][0]
            xpoints = [(e[0]-creation).total_seconds()/3600 for e in tdata]
        else:
            xpoints = [e[0] for e in tdata]

        return xpoints, tpoints, gpoints

    ##########
    ## Prepares for count diagrams
    ##########
    def editcountdata(self, pageid, domain):
        dtb = db.WikiDatabase()

        dbdata = self.dtb.getusereditcounts(pageid, domain)
        sdata = sorted(dbdata, key = lambda x: x[1])

        xlabels, ypoints = zip(*sdata)
        xlabels = [e.decode('utf-8').strip() for e in xlabels]

        return xlabels, ypoints

    ##########
    ## Prepares for share diagrams
    ##########
    def editsharedata(self, pageid, domain, weights=None, namesort=None, dbdata=None):
        dtb = db.WikiDatabase()

        dbdata = dbdata if dbdata else dtb.getuserchange2(pageid, domain)

        gradients = [u[-1] for u in dbdata]

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

    ##########
    ## Used for some dump plots
    ##########
    def talkpages(self):
        dtb = db.WikiDatabase()
        
        tiid = dtb.getalltalk()

        title, id1, id2, domain = zip(*tiid)

        return title, id1, id2, domain
