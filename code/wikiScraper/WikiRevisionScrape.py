import requests
import time
import json
import csv
import wikipedia
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from decimal import Decimal

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
    pagelimit = 1
    historylimit = -1
    rl = False
    rl_minwait = None
    rl_lastcall = None
    pageid = 0
    parentid = 0
    childid = 0

    #atm naively assuming headers, params, titles to be in correct format
    def __init__(self, pagelimit=1, historylimit=-1, _headers=None, _params=None, _titles=None):
        if(_params):
            params = _params

        if(_headers):
            self.head = _headers

        if(_titles):
            self.params['titles'] = _titles
            self.rand = False

        self.pagelimit = pagelimit
        self.historylimit = historylimit
        

    def scrape(self, indexfilename, contentsfilename):
        self._pace()
        index_f = open(indexfilename + ".csv", "ab") #HACK = needs to migrate to postrgres
        contents_f = open(contentsfilename + ".csv", "ab")  #HACK = needs to migrate to postrgres
        index = csv.writer(index_f)
        contents = csv.writer(contents_f)
        index.writerow(["PAGEID","REVISION","USER","USERID","TIMSTAMP","SIZE","COMMENT"]) 
        contents.writerow(["PAGEID","REVISION","CONTENT"])
        
        for i in range(self.pagelimit):
            if 'rvprop' in self.par:
                del self.par['rvprop']
            if 'revids' in self.par:
                del self.par['revids']
            print "fetching page"
            if(self.rand):
                self.par['titles'] = wikipedia.random() #get random title
            self.childid = self._getlatest()
            r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
            self._rate()
            del self.par['titles']
            self._tracehist(index, contents)
       
    def _getlatest(self):
        r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
        r = r.json()

        #HACK = should grab multiple pages
        for key, value in r['query']['pages'].iteritems():
            self.pageid = key
        #HACK = chould grab multiple revisions (for each pageid)
        self.parentid = self.childid = r['query']['pages'][self.pageid]['revisions'][0]['revid'] 
        return self.childid
    
    def _tracehist(self, index, contents):
        ##We store revisions we've visited
        ##loops can occur in revision histories
        visited = []
        i = self.historylimit
        j = 0

        self.par['rvprop'] = 'userid|user|ids|flags|tags|size|comment|contentmodel|timestamp|content'

        while (self.parentid not in visited) and i is not 0 and self.parentid is not 0:
            self.par['revids'] = self.parentid

            self._pace()

            r = requests.get(WIKI_API_URL, params=self.par, headers=self.head)
            r = r.json()
            
            self._rate()

            visited.append(self.childid)
            
            #print r
            
            self.childid =  r['query']['pages'][self.pageid]['revisions'][0]['revid']
            self.parentid = r['query']['pages'][self.pageid]['revisions'][0]['parentid']
            user = r['query']['pages'][self.pageid]['revisions'][0]['user']
            userid = r['query']['pages'][self.pageid]['revisions'][0]['userid']
            size = r['query']['pages'][self.pageid]['revisions'][0]['size']
            timestamp = r['query']['pages'][self.pageid]['revisions'][0]['timestamp']
            comment = "" #comments sometimes don't return from old revisions...
            try:
                comment = r['query']['pages'][self.pageid]['revisions'][0]['comment']
            except:
                comment = ""    
            content = r['query']['pages'][self.pageid]['revisions'][0]['*']
            
            index.writerow([self.pageid, self.childid, user.encode("UTF-8"), userid, timestamp, size, comment.encode("UTF-8")])
            contents.writerow([self.pageid, self.childid, content.encode("UTF-8")])

            if(self.historylimit > 0):
                print self.pageid, "fetch", j+1, "of", self.historylimit, ", revid", self.childid, "timestamp", str(timestamp)
                i = i - 1
            else:
                print self.pageid, "fetch", j+1, ", revid", self.childid, "timestamp", str(timestamp)
            j = j + 1    
        print "limit reached"
        
    def _pace(self):
        if self.rl and self.rl_last_call and self.rl_lastcall + self.rl_minwait > datetime.now():
            wait_time = (self.rl_lastcall + self.rl_minwait) - datetime.now()
            time.sleep(int(wait_time.total_seconds()))

    def _rate(self):
        if self.rl:
            self.rl_lastcall = datetime.now()
