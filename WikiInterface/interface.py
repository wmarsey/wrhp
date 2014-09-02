from __future__ import division
import database as db
import math as m
from consts import *
from sys import stdout
import multiprocessing as mltp
import re
import lshtein as lv
from logger import *

##regexes for splitting wikimarkup string. mostly in form (start
##tag)-(many characters but not end tag)-(end tag)
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
##regexes, grouped
regexlist = [(math1,math2),#maths
             (bquote, cite, citeneed, asof),#citations
             (afile,score),#filesimages
             (linkint, linkext),#links
             (h1, h2, h3, h4, h5, table)]#structure

##########
## extracts a slice mid-string
##########
def extract(start, stop, string):    
    return string[start:stop], string[:start]+string[stop:]

##########
## for process spawned by calcdist below, passes back levenshtein dist
##########
def calcdistworker(string1, string2, identity, results):
    if __debug__:
        logDebug("worker process " + str(identity) + " string1 length: " +\
                     str(len(string1)) + " string2 length: " + str(len(string2)))
    
    ## calculate distance 
    dist = lv.fastlev.plaindist(string1, string2)
    ## put into queue
    results.put((identity, dist))
    
    if __debug__:
        logDebug("process " + str(identity) + " returning " + str(dist))

##########
##########
##
## WikiAnalyser class checks for / calculates trajectory and weights
##
##########
##########
class WikiAnalyser:
    dotcount = 1
    dtb = None
    title, pageid, domain = None, None, None

    def __init__(self, title, pageid, domain):
        self.title = title
        self.pageid = pageid
        self.domain = domain
        self.dtb = db.Database()
    
    ##########
    ## should be only externally used function.  grabs all revisions
    ## in database, checks whether they've been provessed before,
    ## sends them to helper functions in sequence if not.
    ##########
    def analyse(self):
        print "Analysing", self.title, self.pageid, self.domain
        
        revs = self.dtb.getextantrevs(self.pageid, self.domain)
        revx = revs[0]
        
        if __debug__:
            logDebug("most revent rev", revs[0])
        
        contentx = self.dtb.getrevcontent(revx, self.domain)   
        
        print "Tracing trajectory", len(revs), "revisions"
        
        for rev in revs:
            if not self.maketrajectory(contentx, revx, rev):
                return None
            dot()
        
        print "\nCalculating pairs"
        
        i, v = 0, 1
        while not v > len(revs):
            parentid = revs[v] if v < len(revs) else 0
            childid = revs[i]
            
            if __debug__:
                logDebug("getting weights, pair parentid:", parentid, "childid:", childid)
            
            if not self.makeweight(parentid, childid):
                return None
            
            elif __debug__:
                logDebug("in database")
            
            dot((not i), (v == len(revs)))
            i = v
            v = v + 1
        
        return True

    ##########
    ## Wrapper for Wikipedia search function, to give suggestions on a
    ## better title...
    ##########
    def search(query, results=8, suggestion=False):     
        params = {
            'list': 'search',
            'srprop': '',
            'srlimit': results,
            'limit': results,
            'srsearch': query,
            'action': 'query',
            'format': 'json',
            }
        
        if suggestion:
            search_params['srinfo'] = 'suggestion'

        raw_results = get(self.api_url, params, headers=self.head).json()

        if 'error' in raw_results:
            if raw_results['error']['info'] in ('HTTP request timed out.', 'Pool queue is full'):
                raise HTTPTimeoutError(query)
            else:
                raise WikipediaException(raw_results['error']['info'])

        search_results = (d['title'] for d in raw_results['query']['search'])

        if suggestion:
            if raw_results['query'].get('searchinfo'):
                return list(search_results), raw_results['query']['searchinfo']['suggestion']
            else:
                return list(search_results), None

        return list(search_results)

    ##########
    ## takes a revision ID pair, sends for computation 
    ##########
    def makeweight(self, parentid, revid):
        if not self.dtb.getweight(revid, self.domain): ##if not in database
            dists = self.calcdists(revid, parentid)
            gradconst = self.calcgradient(revid, parentid)
            if __debug__:
                logDebug("calculated gradient as " + str(gradconst))
            return self.dtb.insertweight(revid, self.domain, dists, gradconst)
        return True

    ##########
    ## takes revision ID pair, performs trajectory calculations if
    ## necessary
    ##########
    def maketrajectory(self, contentx, revx, oldrev):
        if __debug__:
            logDebug("getting trajectory distance, between revisions " + str(revx) + " and " + str(oldrev))
        
        dist = self.dtb.gettraj(revx, oldrev, self.domain)
        
        if dist < 0: ## if not in database
            
            contenty = self.dtb.getrevcontent(oldrev, self.domain) 
            if not contenty:
                contenty = "" ## caveat for blank page entries
            
            lev = lv.fastlev.plaindist(contentx,contenty) if revx != oldrev else 0
            
            if __debug__:
                logDebug("calculated as " + str(lev))
            
            return self.dtb.trajinsert(revx,oldrev,lev,self.domain)
        
        elif __debug__:
            logDebug("in database as " + str(dist))
        
        return True
        
    ##########
    ## Employs multiprocessing module. Splits a string according to a
    ## series of regexes, if there is a distance to calculate, spawns
    ## a subprocess to make the calculation while going onto prepare
    ## the next string. Final string usually much longer than the
    ## rest, but some time is saved.
    ##########
    def calcdists(self, revid, parentid):
        string1 = self.dtb.getrevcontent(parentid, self.domain) if parentid else ""
        string2 = self.dtb.getrevcontent(revid, self.domain)  
        strings = [string1, string2]

        processes = []
        results = mltp.Queue(maxsize=len(regexlist))
        dists = [0 for _ in range(len(regexlist) + 1)]

        for i, regs in enumerate(regexlist):
            compare = ["",""]
            for v, s in enumerate(strings):
                for r in regs:
                    while True:
                        m = r.search(strings[v])
                        if not m:
                            break
                        match, strings[v] = extract(m.start(), m.end(), strings[v])
                        compare[v] += match

            ## spawn process if necessary
            if len(compare[0]) or len(compare[1]):
                p = mltp.Process(target=calcdistworker, args=(compare[0], compare[1], i, results))
                p.start()
                processes.append(p)
        
        ## for the remainder string
        p = mltp.Process(target=calcdistworker, args=(strings[0], strings[1], len(regexlist), results))
        p.start()
        processes.append(p)
        
        if __debug__:
            logDebug("spawned", len(processes))

        ## wait on child processes
        for p in processes:
            if p.is_alive():
                p.join()
                
        if __debug__:
            logDebug("recieved", results.qsize(), "results")

        ## collect results
        while not results.empty():
            r = results.get()
            dists[r[0]] = r[1] 

        return dists

    ##########
    ## Graph gradient -> integer. 0 the highest gradient, 1 the
    ## lowest.
    ##########
    def calcgradient(self, revid, parentid): 
        if parentid:
            time1, height1 = self.dtb.gettrajpoint(revid, self.domain)
            time2, height2 = self.dtb.gettrajpoint(parentid, self.domain)
            x = (time1 - time2).total_seconds()/3600
            y = height1 - height2
            
            logDebug("gradient: time1,2: " + str(time1) + "," + str(time2) + \
                      " | " + "height1,2: " + str(height1) + "," + str(height2)\
                         + " | " + "x,y: " + str(x) + "," + str(y))
            
            return 1 if (x <= 0) else (0.5 - m.atan(y/x)/m.pi)
        return 1

        
