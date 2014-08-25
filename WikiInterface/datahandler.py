#from weighteddistance import WDistanceCalc
import database as db
#import lshtein as lv
import math as m

class DHandler:
    dtb = None

    def __init__(self, _weights, _flags=None):
        self.dtb = db.Database()
        self.weights = _weights
        self.flags = _flags

    def weightdata(self, pageid, domain):
        wdata = []
        for u in self.dtb.getuserchange(pageid, domain):
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

    def getbardata(self, pageid, domain, datatype):
        dbdata = None
        if(datatype == "count"):
            dbdata = self.dtb.getusereditcounts(pageid, domain)
        elif(datatype == "reward"):
            dbdata = self.weightdata(pageid, domain)      
        sdata = sorted(dbdata, 
                       key = lambda x: x[1])
        barlabels = [] 
        barheights = []
        for i, e in enumerate(sdata):
            barlabels.append(e[0].decode('utf-8').strip())
            barheights.append(e[1])
        return (barheights, barlabels)

    def gettrajdata(self, revx, domain):
        dbtraj = self.dtb.gettrajectory(revx, domain)
        traj = [e[1] for e in dbtraj]
        dbgrowth = self.dtb.getgrowth(revx, domain)
        growth = [e[1] for e in dbgrowth]
        creation = dbtraj[0][0]
        times = [(e[0]-creation).total_seconds()/3600 for e in dbtraj]
        return (times, traj, growth)

    # def processweights(self, parentid, revid, domain):
    #     contentx = ""
    #     if parentid:
    #         contentx = self.dtb.getrevcontent(parentid, domain)
    #     contenty = self.dtb.getrevcontent(revid, domain)

    #     dist = WDistanceCalc()
    #     dist.processdistance(revid, domain, contentx, contenty)

    #     gradconst = 1
    #     if parentid:
    #         x = (self.dtb.gettime((revid,domain)) - \
    #                  self.dtb.gettime((parentid,domain))).total_seconds()/3600
    #         y = self.dtb.gettrajheight((revid,domain)) - self.dtb.gettrajheight((parentid,domain))
    #         if x < 0:
    #             print "Error: Time travel"
    #         elif x != 0:
    #             gradconst = 0.5 - m.atan(y/x)/m.pi

    #     self.dtb.updateweight('gradient',gradconst,revid,domain)
    #     self.dtb.updateweight('complete',True,revid,domain)
        
    # def gettraj(self, contentx, revx, oldrev, domain):
    #     dist = self.dtb.gettraj([revx, 
    #                              oldrev])
    #     #print dist
    #     if dist < 0:
    #         contenty = self.dtb.getrevcontent(oldrev, domain) 
    #         lev = 0
    #         if revx == oldrev:
    #             lev = 0
    #         else:
    #             lev = lv.fastlev.plaindist(contentx, 
    #                                        contenty)
    #         self.dtb.trajinsert((revx, 
    #                              oldrev, 
    #                              lev))

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
