import database as db
import math as m
from consts import *
from sys import stdout
#import Queue,threading,
import multiprocessing
import re
import lshtein as lv

def extract(start, stop, string):    
    return string[start:stop], string[:start]+string[stop:]

math1 = re.compile('<math>((?!<\/math>).)*<\/math>', re.S)
math2 = re.compile('\{\{math((?!\}\}).)*\}\}')
bquote = re.compile('<blockquote>((?!<\/blockquote>).)*<\/blockquote>', re.S)
cite = re.compile('\{\{cite((?!\}\}).)*\}\}')
citeneed = re.compile('\{\{Citation needed((?!\}\}).)*\}\}')
afile = re.compile('\[\[File((?!\]\]).)*\]\]')
score = re.compile('<score>((?!<\/score>).)*<\/score>', re.S)
linkint = re.compile('\[\[(?!File)((?!\]\]).)*\]\]')
linkext = re.compile('\[http((?!\]).)*\]')
asof = re.compile('\{\{As of((?!\}\}).)*\}\}')
table = re.compile('\{\|((?!\|\}).)*\|\}', re.S)
h1 = re.compile('= ((?!=).)* =')
h2 = re.compile('== ((?!==).)* ==')
h3 = re.compile('=== ((?!===).)* ===')
h4 = re.compile('==== ((?!====).)* ====')
h5 = re.compile('===== ((?!=====).)* =====')
regexdict = {'maths':(math1,math2),
             'citations': (bquote, cite, citeneed, asof),
             'filesimages':(afile,score),
             'links':(linkint, linkext),
             'structure':(h1, h2, h3, h4, h5, table, asof)}

class WikiAnalyser:
    dotcount = 1
    dtb = None
    title, pageid, domain = None, None, None

    def __init__(self, 
                 title,
                 pageid,
                 domain):
        self.title = title
        self.pageid = pageid
        self.domain = domain
        self.dtb = db.Database()

    def analyse(self):
        print "Analysing", self.title, self.pageid, self.domain
        revs = self.dtb.getextantrevs(self.pageid, self.domain)
        revx = revs[0]
        contentx = self.dtb.getrevcontent(revx, self.domain)   
        print "Tracing trajectory", len(revs), "revisions"
        for rev in revs:
            if not self.gettraj(contentx, revx, rev):
                return None
            dot()
        print "\nCalculating pairs"
        i, v = 0, 1
        while not v > len(revs):
            parentid = 0
            if v < len(revs):
                parentid = revs[v]
            childid = revs[i]
            if not self.dtb.getweight(childid, self.domain):
                if not self.makeweight(parentid, childid):
                    return None
            dot((not i), (v == len(revs)))
            i = v
            v = v + 1
        return True

    def gettraj(self, contentx, revx, oldrev):
        dist = self.dtb.gettraj(revx, oldrev, self.domain)
        if dist < 0:
            contenty = self.dtb.getrevcontent(oldrev, self.domain) 
            lev = 0
            if revx == oldrev:
                lev = 0
            else:
                lev = lv.fastlev.plaindist(contentx,contenty)
            return self.dtb.trajinsert(revx,oldrev,lev,self.domain)
        return True

    def calcdists(self, revid, parentid):
        string1 = self.dtb.getrevcontent(parentid, self.domain) if parentid else ""
        string2 = self.dtb.getrevcontent(revid, self.domain)

        dists = []
        for regs in regexdict.itervalues():
            compare = {'m1':'',
                       'm2':''}
            for r in regs:
                while True:
                    m = r.search(string1)
                    if not m:
                        break
                    match, string1 = extract(m.start(), m.end(), string1)
                    compare['m1'] += match
                while True:
                    m = r.search(string2)
                    if not m:
                        break
                    match, string2 = extract(m.start(), m.end(), string2)
                    compare['m2'] += match

            if len(compare['m1']) or len(compare['m2']):
                dists.append(lv.fastlev.plaindist(compare['m1'], compare['m2']))
            else:
                dists.append(0)
        dists.append(lv.fastlev.plaindist(string1, string2))             
        return dists

    def calcgradient(self, revid, parentid): 
        if parentid:
            time1, height1 = self.dtb.gettrajpoint(revid, self.domain)
            time2, height2 = self.dtb.gettrajpoint(parentid, self.domain)
            x = (time1 - time2).total_seconds()/3600
            y = height1 - height2
            return 1 if x <= 0 else 0.5 - m.atan(y/x)/m.pi
        return 1

    def makeweight(self, parentid, revid):
        dists = self.calcdists(revid, parentid)
        gradconst = self.calcgradient(revid, parentid)
        return self.dtb.insertweight(revid, self.domain, dists, gradconst)

#        self.dtb.updateweight('gradient',gradconst,revid,self.domain)
 #       self.dtb.updateweight('complete',True,revid,self.domain)

        
