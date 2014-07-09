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
    dotcount = 1
    upperlimit = True

    def dot(self, reset=False, final=False):
        if reset:
            self.dotcount = 1
        if not (self.dotcount%50) and self.dotcount:
            sys.stdout.write('|')
        else:
            sys.stdout.write('.')
        if final or (not (self.dotcount%50) and self.dotcount):
            sys.stdout.write('\n')
        self.dotcount = self.dotcount + 1
        sys.stdout.flush()

    #atm naively assuming headers, params, titles to be in correct format
    def __init__(self, pagelimit=-1, historylimit=-1, _headers=None, _params=None, _titles=None, upperlimit=True):
        if(_params):
            params = _params

        if(_headers):
            self.head = _headers

        if(_titles):
            self.par['titles'] = _titles
            self.rand = False

        if not upperlimit:
            self.upperlimit = False
        
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
                print "Fetching page", self.par['titles'] 
                self._getlatest()
                ids.append(self.pageid)
                titles.append(self.title)
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
                    print "Fetching page", self.par['titles']
                    self._getlatest()
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
                print "Fetching page", title
                self.par['titles'] = title
                self.title = self.par['titles']
                self._getlatest()
                ids.append(self.pageid)
                titles.append(self.title)
                self._rate()
                del self.par['titles']
                self._tracehist()   
        return titles, ids


    def _getlatest(self):
        r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
        r = r.json()
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
                for c2 in corrupt:
                    if c1['parentid'] == c2['revid']:
                        c1['parentid'] = c2['parentid']
                        corrupt.pop(c2)
                        continue
            break
        for c in corrupt:
            if not self.db.bridgerevision(c['revid'], c['parentid']):
                print "panic"

    def _tracehist(self):
        visited = []
        i = self.historylimit
        j = 0
        pageid = 0
        self.par['rvprop'] = 'userid|user|ids|flags|tags|size|comment|contentmodel|timestamp|content'
        pages = []
        b = False
        failed = []
        while True:
            self.par['revids'] = self.parentid
            self._pace()
            
            visited.append(self.childid)
            
            ##fetch only if not already in database
            parent = -1
            if self.childid == self.parentid:
                parent = self.db.getparent(self.childid)
            elif self.db.revexist(self.childid, self.parentid):
                parent = self.db.getparent(self.parentid)
            if parent > -1:
                self.childid = self.parentid
                self.parentid = parent
            else:
                r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
                r = r.json()
                self._rate()
                try:
                    page = r['query']['pages'][self.pageid]['revisions'][0]
                except:
                    print r
                if not self.db.revexist(page['revid'], page['parentid']):
                    pages.append(page)
                self.childid =  page['revid']
                self.parentid = page['parentid']
                title = r['query']['pages'][self.pageid]['title']
            
            ##determine whether to break later
            if i == 0 or self.parentid == 0 or self.parentid in visited:
                b = True

            ##fetch every 50, or before breaking
            if b or ((len(pages)%50) == 0 and len(pages)):
                if not self.upperlimit or len(visited) >= 50:
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
                        self.db.indexinsert([int(self.childid),
                                             int(self.parentid),
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
                else:
                    print "\nToo few revisions, article discarded"
                    return False
            self.dot(reset=(not j),final=b)
            if b:
                if len(failed):
                    print len(failed), "corrupt pages fetched"
                    print "circumnavigating corrupt pages"
                    self._remove_corruption(failed)
                break
            if(self.historylimit > 0):
                i = i - 1
            j = j + 1
        return True
        
    def _pace(self):
        if self.rl and self.rl_last_call \
                and self.rl_lastcall + self.rl_minwait > datetime.now():
            wait_time = (self.rl_lastcall + self.rl_minwait) - datetime.now()
            time.sleep(int(wait_time.total_seconds()))

    def _rate(self):
        if self.rl:
            self.rl_lastcall = datetime.now()
