import requests
import time
import json
import wikipedia
import sys, os
import inspect
from datetime import datetime, timedelta
sys.path.append("..")
import database

WIKI_API_URL = 'http://en.wikipedia.org/w/api.php'
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
    rand = True
    pagelimit = 10000000
    historylimit = -1
    rl = False
    rl_minwait = None
    rl_lastcall = None
    pageid = 0
    parentid = 0
    childid = 0
    db = None
    title = ""

    def dot(self):
        sys.stdout.write('.')
        sys.stdout.flush()

    #atm naively assuming headers, params, titles to be in correct format
    def __init__(self, pagelimit=-1, historylimit=-1, _headers=None, _params=None, _titles=None):
        if(_params):
            params = _params

        if(_headers):
            self.head = _headers

        if(_titles):
            self.par['titles'] = _titles
            self.rand = False

        self.pagelimit = pagelimit
        self.historylimit = historylimit
        self.db = database.Database()

    def scrape(self):
        self._pace()
        ids = []
        titles = []
        ## IMPROVE THIS LOGICAL FLOW COULD BE JUST TWO IF ELSE DECISIONS
        ## NEEDS TO BE LIKE while self.pagelimit != 0 or something
        if self.pagelimit == -1 and self.rand:
            while True:
                if 'rvprop' in self.par:
                    del self.par['rvprop']
                if 'revids' in self.par:
                    del self.par['revids']
                if(self.rand):
                    self.par['titles'] = wikipedia.random() #get random title
                    self.title = self.par['titles'] 
                print "fetching page", self.par['titles'] 
                self._getlatest()
                ids.append(self.pageid)
                titles.append(self.title)
                r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
                self._rate()
                del self.par['titles']
                self._tracehist()
        elif self.rand:
            for i in range(self.pagelimit):
                while True:
                    if 'rvprop' in self.par:
                        del self.par['rvprop']
                    if 'revids' in self.par:
                        del self.par['revids']
                    self.par['titles'] = wikipedia.random() #get random title
                    self.title = self.par['titles']
                    print "fetching page", self.par['titles']
                    self._getlatest()
                    r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
                    self._rate()
                    del self.par['titles']
                    if self._tracehist(): 
                        ids.append(self.pageid)
                        titles.append(self.title)
                        break
        else:
            for title in self.par['titles'].split('|'):
                if 'rvprop' in self.par:
                    del self.par['rvprop']
                if 'revids' in self.par:
                    del self.par['revids']
                print "fetching page", title
                self.par['titles'] = title
                self.title = self.par['titles']
                self._getlatest()
                ids.append(self.pageid)
                titles.append(self.title)
                r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
                self._rate()
                del self.par['titles']
                self._tracehist()   
        return titles, ids


    def _getlatest(self):
        r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
        r = r.json()
        #HACK = should grab multiple pages
        try:
            p = r['query']['pages']
        except:
            print r
        for key, value in r['query']['pages'].iteritems():
            self.pageid = key
        #HACK = chould grab multiple revisions (for each pageid)
        self.parentid = self.childid = r['query']['pages'][self.pageid]['revisions'][0]['revid']
        return self.childid
    
    def _tracehist(self):
        visited = []
        i = self.historylimit
        j = 0
        pageid = 0
        self.par['rvprop'] = 'userid|user|ids|flags|tags|size|comment|contentmodel|timestamp|content'
        pages = []
        b = False
        while True:
            self.par['revids'] = self.parentid
            self._pace()
            r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
            r = r.json()
            self._rate()

            try:
                page = r['query']['pages'][self.pageid]['revisions'][0]
            except:
                print r
            visited.append(self.childid)
            pages.append(page)
            self.childid =  page['revid']
            self.parentid = page['parentid']
            title = r['query']['pages'][self.pageid]['title']

            if i == 0 or self.parentid == 0 or self.parentid in visited:
                b = True

            if b or ((len(pages)%50) == 0 and len(pages)):
                if len(visited) >= 50:
                    for p in pages:
                        user, size, timestamp, comment, content = "", "", "", "", ""
                        self.childid =  p['revid']
                        self.parentid = p['parentid']
                        user = p['user']
                        try:
                            userid = p['userid']
                        except:
                            pass
                        try:
                            size = p['size']
                        except:
                            pass
                        try:
                            timestamp = p['timestamp']
                        except:
                            pass
                        try:
                            comment = p['comment']
                        except:
                            pass    
                        content = p['*']
                        self.db.indexinsert([int(self.childid), 
                                             int(self.pageid), 
                                             user.encode("UTF-8"), 
                                             int(userid), 
                                             timestamp, 
                                             size, 
                                             comment.encode("UTF-8")])
                        self.db.contentinsert([int(self.childid), 
                                               int(self.pageid), 
                                               title, 
                                               content.encode("UTF-8")])
                        pages = []
                    sys.stdout.write('|\n')
                    sys.stdout.flush()
                else:
                    print "\nArticle discarded"
                    return False
            if b:
                break
            if(self.historylimit > 0):
                i = i - 1
            self.dot()
            j = j + 1    
        return True
        
    def _pace(self):
        if self.rl and self.rl_last_call and self.rl_lastcall + self.rl_minwait > datetime.now():
            wait_time = (self.rl_lastcall + self.rl_minwait) - datetime.now()
            time.sleep(int(wait_time.total_seconds()))

    def _rate(self):
        if self.rl:
            self.rl_lastcall = datetime.now()
