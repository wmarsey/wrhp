import database as db
import wikiScraper as wk
#from datahandler import DHandler
#from weighteddistance import WDistanceCalc
from consts import *
import sys
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

    # reg1 = re.compile('y')
    # reg2 = re.compile('h')
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
        with open('regexlog.txt','w') as log:
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
                        message = "MATCH calculating for revid " + str(revid) + " slice " + str(m.start()) + " to " + str(m.end()) + "\n"
                        message += "text: " + match + "\n"
                        message += "pattern: " + r.pattern + "\n\n"
                        log.write(message)
                    while True:
                        m = r.search(string2)
                        if not m:
                            break
                        match, string2 = extract(m.start(), m.end(), string2)
                        compare['m2'] += match
                        message = "MATCH calculating for revid " + str(revid) + " \n"
                        message += "text: " + match + "\n"
                        message += "pattern: " + r.pattern + "\n\n"
                        log.write(message)
                #send off
                if len(compare['m1']) or len(compare['m2']):
                    message = "COMPARING SLICES\n"
                    message += "SLICE 1: " + compare['m1'] + "\n"
                    message += "SLICE 2: " + compare['m2'] + "\n"
                    log.write(message)
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
    #dat = None
    #plt = None
    dotcount = 1
    dtb = None
    title, pageid, domain = None, None, None
    # params = {'scrape_limit': -1,
    #           'depth_limit': -1,
    #           'page_titles': 'random',
    #           'revids': 0,
    #           'userids': 0,
    #           'domain':None,
    #           'weights':{'maths':0,
    #                     'headings':0,
    #                     'quotes':0,
    #                     'files/images':0,
    #                     'links':0,
    #                     'citations':0,
    #                     'normal':0}}
    # flags = {'scrape': False,
    #          'fetch': False,
    #          'analyse': False,
    #          'offline': False,
    #          'weightsdefault' : True,
    #          'plotshow': False,
    #          'noweight':False,
    #          'trundle':False}
    
    def __init__(self, 
                 title,
                 pageid,
                 domain):
        # if params:
        #     self.params = params
        # if flags:
        #     self.flags = flags
        self.title = title
        self.pageid = pageid
        self.domain = domain
        self.dtb = db.Database()
        #self.dat = DHandler(self.params['weights'], self.flags)

    # def checktitle(self):
    #     return self.scrape(test=True)

    # def search(self, word):
    #     searcher = wk.WikiRevisionScrape()
    #     return searcher.search(query=word, suggestion=True)
    
    # def config(self, params=None, flags=None):
    #     if params:
    #         self.params.update(params)
    #     if flags:
    #         self.flags.update(flags)
    #     self.dtb = db.Database()
    #     self.dat = DHandler(self.params['weights'])

    def analyse(self):
        repeat = 1;
        # if(self.params['scrape_limit'] != -1):
        #     repeat = self.params['scrape_limit']
        #self.params['scrape_limit'] = 1
        #self.database = db.Database()
        #pageid = None
        
        ###REIMPLEMENT THIS
        # if self.flags['offline']:
        #     self.params['title'], pageid = self.dtb.getrandom()
        #     print "Fetching random article from database,", self.params['title']
        #     pageid = [pageid]
        #     title = [self.params['title']]
        #     domain = [self.params['domain']]
        # else:
        #     title, pageid, domain = self.scrape()
        # pagecount = 0

        print "Analysing", self.title, self.pageid, self.domain
        revs = self.dtb.getextantrevs(pageid, domain)
        revx = revs[0]
        contentx = self.dtb.getrevcontent(revx, self.domain)   
        print "Tracing trajectory", len(revs), "revisions"
        for rev in revs:
            self.gettraj(contentx, revx, rev)
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
                #self.dtb.distinsert(###processweightsgoeshere#)
            dot((not i), (t != (len(pageids)-1)))
            i = v
            v = v + 1
            #pagecount = pagecount + 1

        #results = {'title':title}
        data = self.dtb.getresults(self.pageid, self.domain)
        return data  

    def gettraj(self, contentx, revx, oldrev):
        dist = self.dtb.gettraj([revx, oldrev])
        if dist < 0:
            contenty = self.dtb.getrevcontent(oldrev, self.domain) 
            lev = 0
            if revx == oldrev:
                lev = 0
            else:
                lev = lv.fastlev.plaindist(contentx,contenty)
            self.dtb.trajinsert((revx,oldrev,lev))

    def processweights(self, parentid, revid):
        contentx = ""
        if parentid:
            contentx = self.dtb.getrevcontent(parentid, self.domain)
        contenty = self.dtb.getrevcontent(revid, self.domain)
            
        dist = WDistanceCalc()
        dist.processdistance(revid, domain, contentx, contenty)

        gradconst = 1
        if parentid:
            x = (self.dtb.gettime((revid,domain)) - \
                     self.dtb.gettime((parentid,domain))).total_seconds()/3600
            y = self.dtb.gettrajheight((revid,domain)) - self.dtb.gettrajheight((parentid,domain))
            if x < 0:
                print "Error: Time travel"
            elif x != 0:
                gradconst = 0.5 - m.atan(y/x)/m.pi

        self.dtb.updateweight('gradient',gradconst,revid,domain)
        self.dtb.updateweight('complete',True,revid,domain)

    def dot(self, reset=False, final=False, slash=False):
        dot = '.'
        if slash:
            dot = '-'
        if reset:
            self.dotcount = 1
        if not (dotcount%50) and dotcount:
            sys.stdout.write('|')
        else:
            sys.stdout.write(dot)
        if final or (not (dotcount%50) and dotcount):
            sys.stdout.write('\n')
        self.dotcount = self.dotcount + 1
        sys.stdout.flush()

    # def scrape(self, test=False):
    #     scraper = None
    #     if not test and self.params["page_titles"] == "random":
    #         scraper = wk.WikiRevisionScrape(
    #             historylimit=self.params['depth_limit'],
    #             pagelimit=self.params['scrape_limit'],
    #             domain=self.params['domain']
    #             )
    #     else:
    #         scraper = wk.WikiRevisionScrape(
    #             historylimit=self.params['depth_limit'],
    #             _titles=self.params['page_titles'],
    #             upperlimit=False,
    #             domain=self.params['domain']
    #             )
    #     if test:
    #         return scraper.test()
    #     return scraper.scrape()
