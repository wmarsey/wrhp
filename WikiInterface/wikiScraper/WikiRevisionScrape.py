from requests import get 
import json
from random import choice
from sys import stdout, path
from time import sleep
from datetime import datetime, timedelta
path.append("/homes/wm613/individual-project/WikiInterface/")
import database
import csv
from bs4 import BeautifulSoup
import re

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
    api_url = ""
    api_lang = ""
    api_domain = ""
    domainset = False
    domains = []

    #atm naively assuming headers, params, titles to be in correct format
    def __init__(self, pagelimit=-1, historylimit=-1, _headers=None, _params=None, _titles=None, upperlimit=True, domain=None):
        if _params:
            params = _params

        if _headers:
            self.head = _headers

        if _titles:
            self.par['titles'] = _titles
            self.rand = False
            self.domainset = True
            self.api_domain = domain

        if domain:
            self.domainset = True
            self.api_domain = domain

        if not upperlimit:
            self.upperlimit = False
        
        self.pagelimit = pagelimit
        self.historylimit = historylimit
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
            print d[1], "Wikipedia", "(" + d[0] + ".)"
        return s.replace("|", d[0]), d[1]

    def scrape(self):
        self._pace()
        ids = []
        titles = []
        while True:
            ##prepare params for choosing article
            self.api_url, self.api_lang = self.picklang(self.domainset)##LOGIC
            if 'rvprop' in self.par:
                del self.par['rvprop']
            if 'revids' in self.par:
                del self.par['revids']
            
            ## choose article
            if self.rand:
                self.par['titles'] = self._getrandom() #get random title
                self.title = self.par['titles']
            else:
                self.title = self.par['titles']
            print "Fetching page", self.par['titles'], "(" + self.api_url + ")"

            ##fetch versions
            self._getlatest()
            self._rate()
            del self.par['titles']
            if self._tracehist():# and self._tracediffs():
                ids.append(self.pageid)
                titles.append(self.title)
                self.db.fetchedinsert((self.pageid,
                                       self.title,
                                       self.api_lang));
            
            ##finish if necessary
            if not self.rand or len(ids) == self.pagelimit:
                break
        return titles, ids

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
        r = get(self.api_url, params=self.par, headers=self.head).json()
        try:
            p = r['query']['pages']
        except:
            print r
        for key, value in r['query']['pages'].iteritems():
            self.pageid = key
        #print r
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
                #print "getting", self.par, self.head
                r = get(self.api_url, params=self.par, headers=self.head).json()
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
                        if not size:
                            failed.append(p)
                            continue
                        #print self.childid, timestamp, size
                        #print content
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
                                               content.encode("UTF-8")])
                    pages = []                        
                else:
                    print "\nToo few revisions, article discarded"
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
            if(self.historylimit > 0):
                i = i - 1
            j = j + 1
        return True

    def _tracediffs(self):
        print "Fetching diffs"
        del self.par['rvprop']
        revs = self.db.getextantrevs(self.pageid)
        revs.reverse()
        for i in xrange(len(revs)-1):
            actions = []
            killme = True
            self.par['revids'] = revs[i]
            self.par['rvdiffto']=revs[i+1]
            request = get(self.api_url, params=self.par, headers=self.head).json()
            html = request['query']['pages'][self.pageid]['revisions'][0]['diff']['*']
            parsed = BeautifulSoup(html)
            #print parsed.prettify()
            tags = [("td","diff-deletedline","deleted"),
                    ("td","diff-addedline", "added")]
            # subtags = [("ins", "diffchange", "changed"),
            #            ("del", "diffchange", "changed")]
            changeswap = {}
            for t in tags:
                found = parsed.find_all(t[0], attrs={"class": t[1]})
                for f in found:
                    action = ""
                    line = 0
                    text = ""
                    ##get line number
                    prev = f.find_parent().find_previous_siblings("tr")
                    for p in prev:
                        lineno = p.find_all("td", attrs={"class":"diff-lineno"})
                        if len(lineno):
                            line = int(re.findall(r'\b\d+\b', lineno[-1].text)[0])
                            break

                    ##get action
                    action = t[2]
                    # for st in subtags:
                    #     subfound = f.find(st[0], attrs={"class": st[1]})
                    #     if subfound:
                    #         action = st[2]
                    #         text = subfound.text
                    #         break
                    
                    subdiv = f.find("div")
                    if subdiv:
                        text = subdiv.text
                    else:
                        text = f.text
                    toinsert = (line, action)
                    index = self._findaction(actions,toinsert)
                    if index > -1:
                        actions[index][-1].append(text)
                        actions[index][-2] = actions[index][-2] + 1 
                    else:
                        actions.append([revs[i],
                                        revs[i+1],
                                        toinsert[0],
                                        toinsert[1],
                                        1,
                                        [text]])
                    
            for a in actions:
                self.db.diffinsert(tuple(a))
            self.dot(not i, i == (len(revs)-2))
        return True

    def _findaction(self,actions,action):
        for i,e in enumerate(actions):
            if e[2] == action[0]:
                if e[3] == action[1]:
                    return i
        return -1

    def _pace(self):
        if self.rl and self.rl_last_call \
                and self.rl_lastcall + self.rl_minwait > datetime.now():
            wait_time = (self.rl_lastcall + self.rl_minwait) - datetime.now()
            time.sleep(int(wait_time.total_seconds()))

    def _rate(self):
        if self.rl:
            self.rl_lastcall = datetime.now()
