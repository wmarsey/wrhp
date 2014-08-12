import database as db
import wikiScraper as wk
from datahandler import DHandler
from consts import *
import sys

class WikiInterface:
    dat = None
    plt = None
    dotcount = 1
    dtb = None
    params = {'scrape_limit': -1,
              'depth_limit': -1,
              'page_titles': 'random',
              'revids': 0,
              'userids': 0,
              'domain':None,
              'weights':{'maths':0,
                        'headings':0,
                        'quotes':0,
                        'files/images':0,
                        'links':0,
                        'citations':0,
                        'normal':0}}
    flags = {'scrape': False,
             'fetch': False,
             'analyse': False,
             'offline': False,
             'weightsdefault' : True,
             'plotshow': False,
             'noweight':False,
             'trundle':False}
    
    def __init__(self, params=None, flags=None):
        if params:
            self.params = params
        if flags:
            self.flags = flags
        self.dtb = db.Database()
        self.dat = DHandler(self.params['weights'], self.flags)

    def checktitle(self):
        return self.scrape(test=True)

    def search(self, word):
        searcher = wk.WikiRevisionScrape()
        return searcher.search(query=word, suggestion=True)     

    def config(self, params=None, flags=None):
        if params:
            self.params.update(params)
        if flags:
            self.flags.update(flags)
        self.dtb = db.Database()
        self.dat = DHandler(self.params['weights'])

    def analyse(self):
        repeat = 1;
        if(self.params['scrape_limit'] != -1):
            repeat = self.params['scrape_limit']
        self.params['scrape_limit'] = 1
        self.database = db.Database()
        pageid = None
        if self.flags['offline']:
            self.params['titles'], pageid = self.dtb.getrandom()
            print "Fetching random article from database,", self.params['titles']
            pageids = [pageid]
            titles = [self.params['titles']]
            domains = [self.params['domain']]
        else:
            titles, pageids, domains = self.scrape()
        pagecount = 0
        for t, pageid in enumerate(pageids):
            print "Analysing", titles[t], pageid, domains[t]
            revs = self.dtb.getextantrevs(pageid, domains[t])
            revx = revs[0]
            contentx = self.dtb.getrevcontent(revx, domains[t])   
            print "Tracing trajectory", len(revs), "revisions"
            for rev in revs:
                self.dat.gettraj(contentx, revx, rev, domains[t])
                dot()
            print "\nCalculating pairs"
            creward, i, v = 0, 0, 1
            while not v > len(revs):
                parentid = 0
                if v < len(revs):
                    parentid = revs[v]
                childid = revs[i]
                if not self.dtb.completeweight(childid, domains[t]):
                    self.dat.processweights(parentid, 
                                            childid,
                                            domains[t])
                    #self.dtb.distinsert(###processweightsgoeshere#)
                dot((not i), (t != (len(pageids)-1)))
                i = v
                v = v + 1
                pagecount = pagecount + 1

            # if(self.flags['weightsdefault']):
            #     if not self.flags['noweight']:
            #         _get_weights(self.params['weights'])

            results = {'title':titles[t]}
            data = self.dtb.getresults(pageid, domains[t])
            return data            

            # analysis = {pageid:{'title':titles[t],
            #                     'revs':revs,
            #                     'trajectory':self.dat.gettrajdata(revx, domains[t]),
            #                     'editcounts':self.dat.getbardata(pageid, domains[t],
            #                                                      "count"),
            #                     # 'rewards':self.dat.getbardata(pageid,
            #                     #                               "reward"),
            #                     'rewards':self.dat.getweights(pageid, domains[t]),
            #                     'userinfo':self.dtb.getuserinfo(revx, domains[t])
            #                     }
            #             }

            # return analysis

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

    def scrape(self, test=False):
        scraper = None
        if not test and self.params["page_titles"] == "random":
            scraper = wk.WikiRevisionScrape(
                historylimit=self.params['depth_limit'],
                pagelimit=self.params['scrape_limit'],
                domain=self.params['domain']
                )
        else:
            scraper = wk.WikiRevisionScrape(
                historylimit=self.params['depth_limit'],
                _titles=self.params['page_titles'],
                upperlimit=False,
                domain=self.params['domain']
                )
        if test:
            return scraper.test()
        return scraper.scrape()
