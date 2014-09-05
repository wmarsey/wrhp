from requests import get 
#import json
from random import choice
from sys import stdout, path
import os
import csv
 
path.append(os.path.abspath('..'))
import database as db
from logger import *
from consts import *

WIKI_API_URL = 'http://en.wikipedia.org/w/api.php'
WIKI_API_TEMPLATE = 'http://|.wikipedia.org/w/api.php'
WIKI_USER_AGENT = 'wm613@ic.ac.uk wmarsey wikipedia project, imperial college london'

##########
##########
##
## WikiRevisionScrape automates the downloading of Wikipedia history
## via the Wikipedia API. Can automatically vary language, and skip
## corrupt entries. Created once per eventually fetched page.
##
##########
##########
class WikiRevisionScrape:
    par = {
        'format': 'json',
        'action': 'query',
        'prop': 'revisions'
        }
    head = {
        'User-Agent': WIKI_USER_AGENT
        }
    rand = False
    scrapemin, pageid, parentid, childid = 0, 0, 0, 0
    db = None
    dotcount = 1
    title, api_url, api_lang, api_domain = "", "", "", ""
    domainset, domains = False, []
    visited = []

    def getPageID(self):
        return self.pageid if self.pageid else None
    
    def getRevisions(self):
        return self.visited if len(self.visited) else None
    
    def getDomain(self):
        return self.api_domain if len(self.api_domain) else None
    
    def getTitle(self):
        return self.title if len(self.title) else None

    def __init__(self,title="",pageid=None,domain=None,scrapemin=50):

        if not (title or pageid) or title=='random':
            self.rand = True
 
        self.title=title
        if pageid:
            self.pageid = pageid

        if domain:
            self.api_domain = domain
            self.domainset = True
            print domain
              
        self.scrapemin = scrapemin
        
        self.db = db.WikiDatabase()
        self.domains = self.langsreader()
    
    ##########
    ## Fetches possible wikipedia languages from csv file
    ##########
    def langsreader(self):
        langs = []
        try:
            with open(BASEPATH + '/scraper/langs.csv', 'r') as langfile:
                lread = csv.reader(langfile, delimiter='\t', quotechar='"')
                for row in lread:
                    langs.append(tuple(row))
        except:
            if __debug__:
                logDebug("langs.csv not found, picking english wiki")
            langs = [('en', 'English')]
        return langs

    ##########
    ## Uses the wikipedia API search function to suggest possible titles
    ##########
    def search(self, results=8):     
        params = {
            'list': 'search',
            'srprop': '',
            'srlimit': results,
            'srsearch': self.title,
            'action': 'query',
            'format': 'json',
            }

        raw_results = get(self.api_url, params=params, headers=self.head).json()
        
        try:
            search_results = (d['title'] for d in raw_results['query']['search'])
        except:
            return []

        return list(search_results)

    ##########
    ## Decides whether to pick a random language, prepares the API
    ## base url accordingly
    ##########
    def _picklang(self, domainset=False):
        s = WIKI_API_TEMPLATE
        if domainset:
            lname = ""
            for ds in self.domains:
                if ds[0] == self.api_domain:
                    lname = ds[1]
                    break
            return s.replace("|", self.api_domain), lname
        d = self.domains[0]
        if self.rand:
            d = choice(self.domains)
            print d[1], "Wikipedia", "(" + d[0] + ")"
            self.api_domain = d[0]
        url = s.replace("|", d[0])
        if __debug__:
            logDebug("url chosen: " + url)
        return url, d[1]

    ##########
    ## Automates the scraping process, fetches if necessary
    ##########
    def scrape(self):
        ## prepare params for choosing article
        self.api_url, self.api_lang = self._picklang(self.domainset)
        if 'rvprop' in self.par:
            del self.par['rvprop']
        if 'revids' in self.par:
            del self.par['revids']

        ## choose article
        if self.rand:
            self.title = self._getrandom()
        ##fetch versions
        if not self._getlatest():
            print "Malformed title or pageid."
            if len(self.title):
                sug = self.search()
                if len(sug):
                    print "Wikipedia suggestions: ", ", ".join(sug)
                else:
                    print "Wikipedia has no suggestions."
            return False

        print "Fetching page", self.title, ",", self.pageid

        ## sanity check
        if self._tracehist():
            self.db.fetchedinsert((self.pageid, self.title,
                                   self.api_domain))
            return True
        return False

    ##########
    ## Uses the Wikipedia API random article chooser
    ##########
    def _getrandom(self, pages=1):
        query_params = {
            'action': 'query',
            'list': 'random',
            'rnnamespace': 0,
            'rnlimit': pages,
            'format':'json'
            }        
        request = get(self.api_url, params=query_params, headers=self.head).json()
        titles = [page['title'] for page in request['query']['random']]
        
        if len(titles) == 1:
            return titles[0]
        
        return titles

    ##########
    ## Using title or page ID, gets latest revision ID
    ##########
    def _getlatest(self):
        ## prepare arguments
        if self.title:
            self.par.update({'titles':self.title})
        elif self.pageid:
            self.par.update({'pageids':self.pageid})
        
        ## get it
        r = get(self.api_url, params=self.par, headers=self.head).json()
        
        ## clean up after yourself
        if self.title:
            del self.par['titles']
        elif self.pageid:
            del self.par['pageids']

        ## see if you got anything good
        try:
            p = r['query']['pages']
        except:
            return False

        ##get pageid
        for key, value in r['query']['pages'].iteritems():
            self.pageid = key
        
        ##get the revision ID
        try:
            self.parentid = self.childid = p[self.pageid]['revisions'][0]['revid']
            if not self.title:
                self.title = p[self.pageid]['title']
        except:
            return False
        return True
    
    ##########
    ## Cleaning corrupt entries. If two corrupt entries one after
    ## other, remove one of them, then send to database one by one for
    ## pointer rearranging
    ##########
    def _remove_corruption(self, corrupt):
        while True:
            for c1 in corrupt:
                for i, c2 in enumerate(corrupt):
                    if c1['parentid'] == c2['revid']:
                        c1['parentid'] = c2['parentid']
                        corrupt.pop(i)
                        continue
            break
        
        for c in corrupt:
            self.db.bridgerevision(c['revid'], c['parentid'], self.api_domain)

    ###########
    ## Does grunt work of requesting, checking for consistency /
    ## inconsistency
    ##########
    def _tracehist(self):
        self.visited = []
        j = 0
        pageid = 0
        self.par['rvprop'] = 'userid|user|ids|flags|tags|size|comment|contentmodel|timestamp|content'
        pages = []
        b = False
        failed = []
        while True:
            self.par['revids'] = self.parentid
            
            self.visited.append(self.childid)
            
            ## check database
            parent = -1
            if self.childid == self.parentid:
                parent = self.db.getparent(self.childid, self.api_domain)
            elif self.db.revexist(self.childid, self.parentid, self.api_domain):
                parent = self.db.getparent(self.parentid, self.api_domain)
            
            ## fetch if necessary
            if parent >= 0:
                self.childid = self.parentid
                self.parentid = parent
            else:
                ## request to api
                r = get(self.api_url, params=self.par, headers=self.head).json()
 
                ## if fully corrupt, prepare to terminate early.
                ## this includes all random api failures
                try:
                    page = r['query']['pages'][self.pageid]['revisions'][0]
                except:
                    b = True 
                else:
                    if not self.db.revexist(page['revid'],page['parentid'],self.api_domain):
                        pages.append(page)
                    self.childid = page['revid']
                    self.parentid = page['parentid']
                    title = r['query']['pages'][self.pageid]['title']
                
            ## check if we are at the oldest discoverable revision
            if self.parentid == 0 or self.parentid in self.visited:
                b = True

            ## check whether it's time to batch insert into database
            ## (this happens either every 50 fetches, or just every
            ## time we are about to break from fetching a page with a
            ## long enough history)
            if b or ((len(pages)%50) == 0 and len(pages)):
                if len(self.visited) >= self.scrapemin or not self.rand:
                    for p in pages:
                        user, size, timestamp, comment, content = "", "", "", "", ""
                        try:
                            userid = p['userid']
                        except:
                            pass
                        try:
                            comment = p['comment']
                        except:
                            pass

                        ## register as corrupt if missing what we need most
                        try:
                            childid =  p['revid']
                            parentid = p['parentid']
                            user = p['user']
                            timestamp = p['timestamp']
                        except:
                            failed.append(p)  
                            continue

                        ## empty pages is a thing 
                        try:
                            content = p['*']
                        except:
                            content = ""

                        ## we don't want to trust Wikipedia native
                        ## size / are unsure what its measuring
                        size = len(content)

                        ## send to database
                        if not self.db.indexinsert([int(childid),
                                                    int(parentid),
                                                    int(self.pageid),
                                                    user.encode("UTF-8"), 
                                                    int(userid), 
                                                    timestamp, 
                                                    size, 
                                                    comment.encode("UTF-8"),
                                                    self.api_domain]):
                            return False
                        if not self.db.contentinsert([int(childid), 
                                                      int(pageid),
                                                      content.encode("UTF-8"),
                                                      self.api_domain]):
                            return False
                    pages = []                        
                else:
                    print "\nToo few revisions, article discarded"
                    print
                    return False
            dot(reset=(not j),final=b)
            
            ## break if ready
            if b:
                ##deal with corruption before break
                if len(failed):
                    print len(failed), "corrupt pages fetched, revids:"
                    for f in failed:
                        try:
                            print f['revid']
                        except:
                            pass
                    print "circumnavigating corrupt pages"
                    self._remove_corruption(failed)
                break
            j = j + 1
        return True
