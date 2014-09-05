from __future__ import division ##for float-returning divisor
import sys,os,errno
from wikiDataPlot import WikiDataPlot
from consts import *
import datetime
from copy import copy
from traceback import print_exception
from argParser import ArgParser
import scraper as wk
from wikiAnalysis import WikiAnalysis
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

    def dbrepair(self, delete=False, clear=False):
        import database as db
        dtb = db.WikiDatabase()
        fetch = dtb.getallfetched()
        
        delete = True

        if delete:
            print "cleaning incomplete entries from the database"
            if clear:
                dtb.empty()
            else:
                dtb.cleanup()
            return 0
        elif:
            piddoms = dtb.getallscraped()

        print "Checking", len(piddoms), "pageids for complete details"

        for t in piddoms:
            scraper = wk.WikiRevisionScrape(pageid=self.params['pageid'],
                                            title=self.params['title'],
                                            domain=self.params['domain'],
                                            scrapemin=0)
            if scraper.scrape():
                pageid = scraper.getPageID()
                title = scraper.getTitle()
                domain = scraper.getDomain()
            else:
                continue
            
        print "Checking", len(fetch), "fetched entries for analyses"

        for f in fetch:
            analyser = WikiAnalysis(*f)
            results = analyser.analyse()
            if not results:
                return -1
        return 0

    def run(self):
        if self.flags['launch']:
            return self.launch()
        
        if self.flags['dbrepair']:
            return self.dbrepair()

        while True:
            while True:
                print "---------FETCHING WIKIPEDIA PAGE------------"
                scraper = wk.WikiRevisionScrape(title=self.params['title'],
                                                pageid=self.params['pageid'],
                                                domain=self.params['domain'],
                                                scrapemin=self.params['scrapemin'])
                
                if scraper.scrape():
                    pageid = scraper.getPageID()
                    title = scraper.getTitle()
                    domain = scraper.getDomain()
                    break
                elif (self.params['title'] or self.params['pageid']):
                    return -1 ##if you asked but didnt get. terminate
                              ##instead of trying again

            print
            print "-----------------ANALYSING------------------"    
            analyser = WikiAnalysis(title,pageid,domain)
            results = analyser.analyse()
            if not results:
                return -1

            if self.flags['plot']:
                print
                print "--------------------PLOT--------------------"
                import wikiDataPlot as dpl
                plotter = dpl.WikiDataPlot(os.path.abspath(self.params['plotpath']) if self.params['plotpath'] else None)
                plotted = plotter.plot(title, pageid, domain)
                print len(plotted), "plotted"

            revidLog(title, pageid, domain)

            if not self.flags['trundle']:
                break

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
