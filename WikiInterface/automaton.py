from __future__ import division ##for float-returning divisor
import sys,os,errno
from dataplotter import Plotter
from interactiveplotter import IPlot 
from consts import *
import datetime
from copy import copy
from traceback import print_exception
from argParser import ArgParser
import wikiScraper as wk
from interface import WikiAnalyser
from logger import revidLog

class WikiCLI:
    params, flags = None, None

    def __init__(self, params, flags):
        self.params = params
        self.flags = flags
    
    def launch(self):
        import launch
        wl = launch.WikiLaunch()
        #print "---------------VIEW MODE---------------"
        if self.params['revid']:
            if self.params['oldrevid']:
                wl.showdiff(self.params['oldrevid'], 
                            self.params['revid'], 
                            self.params['domain'])
            else:
                wl.showrev(self.params['revid'], 
                          self.params['domain'])
        elif self.params['pageid']:
            wl.showpage(self.params['pageid'], 
                        self.params['domain'])
        elif self.params['title']:
            wl.showtitle(self.params['title'], 
                         self.params['domain'])
        else: wl.showuser(self.params['user'],
                        self.params['domain'])
        return 0

    def dbrepair(self):
        import database as db
        dtb = db.Database()
        fetch = dtb.getallfetched()

        piddoms = dtb.getallscraped()

        print "Checking", len(piddoms), "pageids for complete details"

        for t in piddoms:
            scraper = wk.WikiRevisionScrape(pageid=t[0],
                                            domain=t[1],
                                            scrapemin=0)
            title, pageid, domain = scraper.scrape()

        print "Checking", len(fetch), "fetched entries for analyses"

        for f in fetch:
            analyser = WikiAnalyser(*f)
            results = analyser.analyse()
            if not results:
                return -1
    
    def run(self):
        if self.flags['launch']:
            return self.launch()
        
        if self.flags['dbrepair']:
            return self.dbrepair()

        #################### NEW CODE START

        import database as db
        dtb = db.Database()
        tpl = dtb.getallfetched()
        
        print "got", len(tpl)
        
        titles, pageids, languages = zip(*tpl)
        
        print titles

        self.params['scrapemin'] = 1

        for i in range(len(tpl)):
            if "Talk:" in titles[i]:
                continue
            if not len(titles[i]):
                continue
            self.params['title'] = "Talk:" + titles[i]
            self.params['domain'] = languages[i]

            print self.params['title']
            print self.params['domain']

        #################### NEW CODE END

        ############################## INDENTATION CHANGE START

            while True:
                b = False ###DELETE
                while True:
                    print "---------FETCHING WIKIPEDIA PAGE------------"
                    scraper = wk.WikiRevisionScrape(title=self.params['title'],
                                                    domain=self.params['domain'],
                                                    scrapemin=self.params['scrapemin'])
                    title, pageid, domain = scraper.scrape()

                    if title and pageid and domain:
                        break
                    elif (self.params['title'] or self.params['pageid']):
                        #return -1 ##if you asked but didnt get. terminate
                                 ##instead of trying again
                        b = True ##DELETe
                        break ## DELETE
                if b:
                    break

                print
                print "-----------------ANALYSING------------------"    
                analyser = WikiAnalyser(title,pageid,domain)
                results = analyser.analyse()
                if not results:
                    return -1

                if self.flags['plot']:
                    print
                    print "--------------------PLOT--------------------"
                    import dataplotter as dpl
                    plotter = dpl.Plotter(os.path.abspath(self.params['plotpath']) if self.params['plotpath'] else None)
                    plotted = plotter.plot(title, pageid, domain)
                    print len(plotted), "plotted"

                revidLog(title, pageid, domain)

                if not self.flags['trundle']:
                    break

        ############################## INDENTATION CHANGE END

        return 0


def main():
    argparse = ArgParser(sys.argv[1:])
    try:
        params, flags = argparse.run()
    except ValueError:
        print_exception(sys.exc_info()[0], sys.exc_info()[1], None)
        sys.exit(errno.EINVAL)
    if not params:
        sys.exit(0)
    
    cli = WikiCLI(params, flags)
    sys.exit(cli.run())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nKeyboard Interrupt"
        sys.exit(0)
