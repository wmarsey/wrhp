import urllib, urlparse
import webbrowser

class WikiLaunch:
    tmplurl = "http://|.wikipedia.org/wiki/"
    indexf = "index.php"
    apif = "api.php"
    userf = "User:"

    def showpage(self, pageid, domain):
        urlbase = self.tmplurl.replace("|",domain) + self.indexf
        parameters = {'curid': pageid}
        self._launch(urlbase, parameters)

    def showtitle(self, title, domain):
        urlbase = self.tmplurl.replace("|",domain) + title
        self._launch(urlbase, None)

    def showdiff(self, oldrevid, newrevid, domain):
        urlbase = self.tmplurl.replace("|",domain) + self.apif
        parameters = {'diff':newrevid,
                      'oldid':oldrevid}

        self._launch(urlbase, parameters)

    def showrev(self, revid, domain):
        urlbase = self.tmplurl.replace("|",domain) + self.apif
        parameters = {'oldid':revid}

        self._launch(urlbase, parameters)

    def showuser(self, username, domain):
        urlbase = self.tmplurl.replace("|",domain) + self.userf + username 
        self._launch(urlbase, None)

    def _launch(self, url, param):
        if param:
            urlp = list(urlparse.urlparse(url))
            urlp[4] = urllib.urlencode(param)
            webbrowser.open(urlparse.urlunparse(urlp))
        else:
            webbrowser.open(url)
