from requests import get 
import json
from random import choice
from sys import stdout, path
import sys
import csv
import re
 
path.append("/homes/wm613/individual-project/WikiInterface/")
import database

WIKI_API_URL = 'http://en.wikipedia.org/w/api.php'
WIKI_API_TEMPLATE = 'http://|.wikipedia.org/w/api.php'
WIKI_USER_AGENT = 'wikipedia (https://github.com/goldsmith/Wikipedia/)'

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
    #rl, rl_minwait, rl_lastcall = False, None, None
    scrapemin, pageid, parentid, childid = 0, 0, 0, 0
    db = None
    dotcount = 1
    title, api_url, api_lang, api_domain = "", "", "", ""
    domainset, domains = False, []
    
    def __init__(self,title=None,pageid=None,domain=None,scrapemin=50):

        self.title=title
        if not title or title=='random':
            self.rand = True
            
        if domain:
            self.api_domain = domain
            self.domainset = True
              
        self.scrapemin = scrapemin
        
        self.db = database.Database()
        self.domains = self.langsreader()
        
    def langsreader(self):
        langs = []
        try:
            with open('/homes/wm613/individual-project/WikiInterface/wikiScraper/langs.csv', 'r') as langfile:
                lread = csv.reader(langfile, delimiter='\t', quotechar='"')
                for row in lread:
                    langs.append(tuple(row))
        except:
            print "langs.csv missing. Using only English wikipedia"
            langs = [('en', 'English')]
        return langs

    def picklang(self, domainset=False):
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
        return s.replace("|", d[0]), d[1]

    def scrape(self):
        ## prepare params for choosing article
        self.api_url, self.api_lang = self.picklang(self.domainset)
        if 'rvprop' in self.par:
            del self.par['rvprop']
        if 'revids' in self.par:
            del self.par['revids']

        ## choose article
        if self.rand:
            self.title = self._getrandom()
        ##fetch versions
        self._getlatest()

        print "Fetching page", self.title, ",", self.pageid

        if self._tracehist():
            self.db.fetchedinsert((self.pageid,
                                   self.title,
                                   self.api_domain))
            return self.title, self.pageid, self.api_domain
        return None, None, None

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

    def _getlatest(self):
        self.par.update({'titles':self.title})
        r = get(self.api_url, params=self.par, headers=self.head).json()
        del self.par['titles']
        try:
            p = r['query']['pages']
        except:
            print r
        for key, value in r['query']['pages'].iteritems():
            self.pageid = key
        self.parentid = self.childid = r['query']['pages'][self.pageid]['revisions'][0]['revid']
        return self.childid
    
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

    def _tracehist(self):
        visited = []
        j = 0
        pageid = 0
        self.par['rvprop'] = 'userid|user|ids|flags|tags|size|comment|contentmodel|timestamp|content'
        pages = []
        b = False
        failed = []
        while True:
            self.par['revids'] = self.parentid
            
            visited.append(self.childid)
            
            ##fetch only if not already in database
            parent = -1
            if self.childid == self.parentid:
                parent = self.db.getparent(self.childid, self.api_domain)
            elif self.db.revexist(self.childid, self.parentid, self.api_domain):
                parent = self.db.getparent(self.parentid, self.api_domain)
            if parent > -1:
                self.childid = self.parentid
                self.parentid = parent
            else:
                r = get(self.api_url, params=self.par, headers=self.head).json()
                try:
                    page = r['query']['pages'][self.pageid]['revisions'][0]
                except:
                    b = True 
                else:
                    if not self.db.revexist(page['revid'],page['parentid'],self.api_domain):
                        pages.append(page)
                    self.childid =  page['revid']
                    self.parentid = page['parentid']
                    title = r['query']['pages'][self.pageid]['title']
                
            ##CHECK FOR END OF HISTORY
            if self.parentid == 0 or self.parentid in visited:
                b = True

            if b or ((len(pages)%50) == 0 and len(pages)):
                if len(visited) >= self.scrapemin:
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
                        try:
                            self.childid =  p['revid']
                            self.parentid = p['parentid']
                            user = p['user']
                            timestamp = p['timestamp']
                            content = p['*']
                        except:
                            failed.append(p)  
                            continue
                        size = len(content)
                        if not size:
                            failed.append(p)
                            continue
                        self.db.indexinsert([int(self.childid),
                                             int(self.parentid),
                                             int(self.pageid),
                                             user.encode("UTF-8"), 
                                             int(userid), 
                                             timestamp, 
                                             size, 
                                             comment.encode("UTF-8"),
                                             self.api_domain])
                        self.db.contentinsert([int(self.childid), 
                                               int(self.pageid),
                                               content.encode("UTF-8"),
                                               self.api_domain])
                    pages = []                        
                else:
                    print "\nToo few revisions, article discarded"
                    print
                    return False
            self.dot(reset=(not j),final=b)
            if b:
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

    # def _pace(self):
    #     if self.rl and self.rl_last_call \
    #             and self.rl_lastcall + self.rl_minwait > datetime.now():
    #         wait_time = (self.rl_lastcall + self.rl_minwait) - datetime.now()
    #         time.sleep(int(wait_time.total_seconds()))

    # def _rate(self):
    #     if self.rl:
    #         self.rl_lastcall = datetime.now()

    def dot(self, reset=False, final=False):
        if reset:
            self.dotcount = 1
        if not (self.dotcount%50) and self.dotcount:
            stdout.write('|')
        else:
            stdout.write('.')
        if final or (not (self.dotcount%50) and self.dotcount):
            stdout.write('\n')
        self.dotcount = self.dotcount + 1
        stdout.flush()
