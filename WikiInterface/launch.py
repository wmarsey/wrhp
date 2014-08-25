import urllib, urlparse
import webbrowser

class WikiLaunch:
    tmplurl = "http://|.wikipedia.org/"
    indexf = "wiki/index.php"
    apif = "api.php"

    def showpage(self, pageid, domain):
        urlbase = self.tmplurl.replace("|",domain) + self.indexf
        parameters = {'curid': pageid}
        self._launch(urlbase, parameters)

    def showdiff(self, oldrevid, newrevid, domain):
        urlbase = self.tmplurl.replace("|",domain) + self.apif
        parameters = {'diff':newrevid,
                      'oldid':oldrevid}

        self._launch(urlbase, parameters)

    def showrev(self, revid, domain):
        urlbase = self.tmplurl.replace("|",domain) + self.apif
        parameters = {'oldid':oldrevid}

        self._launch(urlbase, parameters)

    def showuser(self, revid, domain):
        urlbase = self.tmplurl.replace("|",domain) + self.apif
        parameters = {'oldid':oldrevid}

        self._launch(urlbase, parameters)

    def _launch(self, url, param):   
        urlp = list(urlparse.urlparse(url))
        urlp[4] = urllib.urlencode(param)
        webbrowser.open(urlparse.urlunparse(urlp))

# def main():
#     wl = WikiLaunch()
#     wl.showpage(43937,"fr")

# if __name__=="__main__":
#     main()
