import database as db
import math as m
from consts import *
from sys import stdout
import Queue,threading,re
import lshtein as lv

def extract(start, stop, string):    
    return string[start:stop], string[:start]+string[stop:]

def distancecalc(queue, reg, revid, domain, string1, string2):
    queue.put(".")
    dist = lv.fastlev.plaindist(string1, string2)
    dtb = db.Database()
    dtb.updateweight(reg,dist,revid,domain)
    queue.task_done()

class WDistanceCalc:
    q = Queue.Queue()
    waiting = 0;

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

    def processdistance(self, revid, domain, string1, string2):
        #lists of lists of regexes
        #seperated by species
        for key,regs in self.regexdict.iteritems():
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
            #send off
            if len(compare['m1']) or len(compare['m2']):
                self.distancethread(revid, domain, key, compare['m1'], compare['m2'])
        #send off remainder
        self.distancethread(revid, domain, 'normal', string1, string2)
        #wait for completion
        self.q.join()

    def distancethread(self, revid, domain, reg, string1, string2):
        t = threading.Thread(target=distancecalc,args=(self.q,reg,revid,domain,string1,string2))
        t.daemon = True
        t.start()

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
        repeat = 1;

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
            if not self.dtb.completeweight(childid, self.domain):
                self.processweights(parentid, childid)
            dot((not i), (v == len(revs)))
            i = v
            v = v + 1

        return True
        # data = self.dtb.getresults(self.pageid, self.domain)
        # return data  

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

    def processweights(self, parentid, revid):
        contentx = ""
        if parentid:
            contentx = self.dtb.getrevcontent(parentid, self.domain)
        contenty = self.dtb.getrevcontent(revid, self.domain)
            
        dist = WDistanceCalc()
        dist.processdistance(revid, self.domain, contentx, contenty)

        gradconst = 1
        if parentid:
            x = (self.dtb.gettime(revid,self. domain) - \
                     self.dtb.gettime(parentid, self.domain)).total_seconds()/3600
            y = self.dtb.gettrajheight(revid, self.domain) -\
                     self.dtb.gettrajheight(parentid, self.domain)
            if x < 0:
                print "Error: Time travel"
            elif x != 0:
                gradconst = 0.5 - m.atan(y/x)/m.pi

        self.dtb.updateweight('gradient',gradconst,revid,self.domain)
        self.dtb.updateweight('complete',True,revid,self.domain)
