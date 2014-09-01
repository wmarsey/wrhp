import psycopg2 as db
import sys
import re
import random

##########
##########
## Database class allows controlled access to database. Written for
## PSQL. Assumes schema set up as in schemacreate.sql. Most functions
## self explanatory
##########
##########

class Database:
    host = 'db-new.doc.ic.ac.uk'
    port = '5432'
    database = 'wm613'
    user = 'wm613'
    password = ''
    contenttable = "wikicontent"
    revisiontable = "wikirevisions"
    trajectorytable = "wikitrajectory"
    fetchedtable = "wikifetched"
    weighttable = "wikiweights"
    cn = None
    crsr = None

    ##########
    ## EXISTENCE TEXT FUNCTIONS
    ##########

    def revexist(self, revid, parentid, domain):
        sql = "SELECT revid, parentid FROM " + self.revisiontable + " WHERE revid = %s AND parentid = %s AND domain = %s;"
        data = (revid, parentid, domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return True
        return False

    ##########
    ## SPECIFIC FETCH FUNCTIONS
    ##########

    def getparent(self, revid, domain):
        sql = "SELECT parentid FROM " + self.revisiontable + " WHERE revid = %s AND domain = %s;"
        data = (revid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result[0][0]
        return -1

    def gettime(self, revid, domain):
        sql = "SELECT time FROM " + self.revisiontable + " WHERE revid = %s AND domain = %s;"
        data = (revid, domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result[0][0]
        return None

    def getchild(self, parentid, domain):
        sql = "SELECT revid FROM " + self.revisiontable + " WHERE parentid = %s AND domain = %s;"
        data = (parentid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result[0][0]
        return -1
  
    def gettrajpoint(self, revid, domain):
        sql = "SELECT time, distance FROM " + self.trajectorytable + " AS t JOIN " + self.revisiontable + " AS r ON revid = revid2 AND r.domain = t.domain WHERE revid = %s AND r.domain = %s;"
        data = (revid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result[0]
        return None

    def gettrajheight(self, revid, domain):
        sql = "SELECT distance FROM " + self.trajectorytable + " WHERE revid2 = %s AND r.domain = %s;"
        data = (revid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result[0][0]
        return None
        
    def getextantrevs(self, pageid, domain):
        sql = "SELECT revid FROM " + self.revisiontable + " WHERE pageid = %s AND domain = %s ORDER BY time DESC;"
        data = (pageid,domain)
        if(self._execute(sql,data)):
            result = self._crsrsanity()
            if result:
                return [e[0] for e in result]
        return None

    def getyoungestrev(self, pageid, domain):
        sql = "SELECT revid FROM " + self.revisiontable + " AS a WHERE a.pageid = %s AND a.domain = %s AND NOT EXISTS (SELECT * FROM " + self.revisiontable + " AS b WHERE b.pageid = %s AND b.domain = %s AND b.time > a.time);"
        data = (pageid,domain,pageid,domain)
        if(self._execute(sql,data)):
            result = self._crsrsanity()
            if result:
                return result[0][0]
        return None

    def getrevcontent(self, revid, domain):
        sql = "SELECT content FROM " + self.contenttable + " WHERE revid = %s AND domain = %s;"
        data = (revid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result[0][0]
        return None

    def getrevinfo(self, revid, domain):
        sql = "select revid from " + self.revisiontable + " where revid = %s AND domain = %s;"
        data = (revid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def gettitle(self, pageid, domain):
        sql = "SELECT title FROM " + self.fetchedtable + " WHERE pageid = %s AND language = %s;"
        data = (pageid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result[0][0]
        return None

    def getdist(self, revid):
        sql = "SELECT distance from " + self.distancetable + " WHERE revid = %s;"
        data = (revid,)
        if(self._execute(sql, data)):
            try:
                result = self._crsrsanity()
                if result:
                    return result[0][0]
            except:
                print "error", revid
                pass
        return -1
    
    def gettraj(self, rev1, rev2, domain):
        sql = "SELECT distance from " + self.trajectorytable + " WHERE revid1 = %s AND revid2 = %s AND domain = %s;"
        data = (rev1, rev2, domain)
        if(self._execute(sql, data)):
            try:
                result = self._crsrsanity()
                if result:
                    return result[0][0]
            except:
                print "error", param[0], param[1]
                pass
        return -1

    def getrandom(self):
        sql = "SELECT * FROM (SELECT DISTINCT pageid, language FROM " + self.fetchedtable + ") AS w OFFSET random()*(SELECT count(*) FROM (SELECT DISTINCT pageid FROM " + self.fetchedtable + ") AS w2) LIMIT 1;"
        while True:
            if(self._execute(sql,())):
                result = self._crsrsanity()
                if result:
                    return result[0][0], result[0][1]
        return None

    def gettrajectory(self, pageid, domain):
        sql = "SELECT time, distance FROM " + self.revisiontable + " AS r JOIN " + self.trajectorytable + " AS t ON revid2 = revid AND r.domain = t.domain WHERE pageid = %s AND t.domain = %s ORDER BY time;"
        data = (pageid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def getgrowth(self, pageid, domain):
        sql = "SELECT time, size FROM " + self.revisiontable + " AS a JOIN " + self.trajectorytable + " AS b ON b.revid2 = a.revid AND a.domain = b.domain WHERE pageid = %s AND b.domain = %s ORDER BY time;"
        data = (pageid,domain)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()

    def getuserchange(self, pageid, domain):
        sql = "SELECT username, sum(maths), sum(citations), sum(filesimages), sum(links), sum(structure), sum(normal) FROM " + self.weighttable + " AS a JOIN " + self.revisiontable + " AS b USING(revid, domain) WHERE b.pageid = %s AND domain = %s GROUP BY username;"
        data = (pageid,domain)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()
        return None

    def getuserchange2(self, pageid, domain):
        sql = "SELECT username, maths, citations, filesimages, links, structure, normal, gradient FROM " + self.weighttable + " AS a JOIN " + self.revisiontable + " AS b USING(revid, domain) WHERE b.pageid = %s AND domain = %s;"
        data = (pageid,domain)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()
        return None
    
    def getusereditcounts(self, pageid, domain):
        sql = "SELECT username, count(revid) AS rcount FROM " + self.revisiontable + " AS a JOIN " + self.fetchedtable + " AS b USING (pageid) WHERE pageid = %s AND language = %s GROUP BY username ORDER BY rcount;"
        data = (pageid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result
        return None 

    def getuserinfo(self, revx, domain):
        sql = "SELECT DISTINCT c.username, c.userid FROM " + self.trajectorytable + " AS b JOIN " + self.revisiontable + " as c ON b.revid1 = %s AND b.revid2 = c.revid AND a.domain = b.domain WHERE b.domain = %s";
        data = (revx,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def getfetched(self, pageid, domain):
        sql = "SELECT language FROM " + self.fetchedtable + " WHERE pageid = %s AND language = %s";
        data = (pageid,domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result[0][0]
        return None
    
    def getweight(self, revid, domain):
        sql = "select * from " + self.weighttable + " where revid = %s AND domain = %s;"
        if(self._execute(sql, (revid, domain))):
            result = self._crsrsanity()
            if result:
                return result[0]
        return None

    #####
    ### INSERTION FUNCTIONS
    #####

    def insertweight(self, revid, domain, dists, gradient):        
        sql = "INSERT INTO " + self.weighttable + " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (revid, domain, dists[0], dists[1], dists[2], dists[3],
        dists[4], dists[5], gradient, True)
        return self._execute(sql, data)

    def contentinsert(self, param):
        if self.getrevcontent(param[0],param[-1]):
            return False
        sql = "INSERT INTO " + self.contenttable + " VALUES (%s, %s, %s, %s);"
        return self._execute(sql, param)

    def indexinsert(self, param):
        if self.getrevinfo(param[0], param[-1]):
            return False
        sql = "INSERT INTO " + self.revisiontable + \
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        data = tuple(param)
        return self._execute(sql,data)

    def distinsert(self, param):
        sql = "INSERT INTO " + self.distancetable + \
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        return self._execute(sql,param)

    def trajinsert(self, rev1, rev2, distance, domain):
        sql = "INSERT INTO " + self.trajectorytable + " VALUES (%s, %s, %s, %s);"
        data = (rev1, rev2, distance, domain)
        return self._execute(sql,data)

    def fetchedinsert(self, param):
        if self.getfetched(param[0], param[-1]):
            return False
        sql = "INSERT INTO " + self.fetchedtable + " VALUES (%s, %s, %s);"
        return self._execute(sql, param)

    ##########
    ## UPDATE FUNCTIONS
    ##########

    def updateweight(self, column, value, revid, domain):        
        sql = "UPDATE " + self.weighttable + " SET " + column + " = %s WHERE revid = %s AND domain = %s"
        if(self._execute(sql, (value, revid, domain))):
            return True
        return False
    
    def bridgerevision(self, revid, parentid, domain):
        alterchild = self.getchild(revid, domain)
        sql = "UPDATE " + self.revisiontable + " SET parentid = %s WHERE revid = %s AND domain = %s;"
        data = (parentid, alterchild, domain) 
        if(self._execute(sql, data)):
            return True
        return False

    def completeweight(self, revid, domain):
        if not self.getweight(revid, domain):
            sql = "INSERT INTO " + self.weighttable + " VALUES (%s, %s, 0, 0, 0, 0, 0, 0, 0, %s)"
            data = (revid, domain, False)
            self._execute(sql, data)
            return False
        else:
            sql = "SELECT complete FROM " + self.weighttable + " WHERE revid = %s and domain = %s and complete = %s"
            data = (revid, domain, True)
            self._execute(sql, data)
            return True if self._crsrsanity() else False 

    def getresults(self, pageid, domain):
        sql = "SELECT revid, maths, citations, filesimages, links, structure, normal, gradient, username, t.distance, time FROM " + self.weighttable + " AS w JOIN " + self.revisiontable + " AS r USING (revid) JOIN " + self.trajectorytable + " AS t ON revid = revid2 AND r.pageid = %s AND r.domain = %s;"
        data = (pageid, domain)
        if(self._execute(sql, data)):
            result = self._crsrsanity()
            if result:
                return result
        return None

    ##########
    ## DUMP / PLOT SPECIFIC FUNCTIONS
    ##########
        
    def getrevidlog(self, pageid, domain):
        sql = "SELECT w.*, time FROM " + self.weighttable + " AS w JOIN " + self.revisiontable + " USING (revid, domain) WHERE pageid = %s AND domain = %s;"
        if(self._execute(sql, (pageid,domain))):
            result = self._crsrsanity()
            if result:
                return [list(w[:-2]) + [sum(w[2:-3])*w[-3]] + [w[-1]] for w in result]
        return None

    def getallrevs(self):
        sql = "SELECT DISTINCT revid, language FROM " + self.fetchedtable + " JOIN " + self.revisiontable + " USING (pageid) WHERE language = domain;"
        if(self._execute(sql, ())):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def getallscraped(self):
        sql = "SELECT DISTINCT pageid, domain FROM " + self.revisiontable + " ORDER BY pageid;"
        if(self._execute(sql, ())):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def getallfetched(self):
        sql = "SELECT title, pageid, language FROM " + self.fetchedtable + " ORDER BY title;"
        if(self._execute(sql, ())):
            result = self._crsrsanity()
            if result:
                return result
        return None
    
    def getaveragerevisioncounts(self):
        sql = "SELECT domain, COUNT(revid) / COUNT(DISTINCT pageid) AS count FROM " + self.revisiontable + " GROUP BY domain ORDER BY count;"
        if(self._execute(sql, ())):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def getaveragepagelengths(self):
        sql = "SELECT domain, sum(size) / count(size) AS av_length FROM " + self.revisiontable + " AS a WHERE NOT EXISTS (SELECT * FROM " + self.revisiontable + " AS b WHERE b.pageid = a.pageid AND b.domain = a.domain AND b.time > a.time) GROUP BY domain ORDER BY av_length;"
        if(self._execute(sql, ())):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def getdatadump(self, limit=None):
        sql = "SELECT w.revid, r.domain, w.maths, w.citations, w.filesimages, w.links, w.structure, w.normal, w.gradient, CASE WHEN r.parentid = 0 OR old.size IS NULL THEN r.size ELSE r.size - old.size END, c.content, oldcont.content, r.comment FROM " + self.fetchedtable + " AS f JOIN " + self.revisiontable + " AS r ON f.pageid = r.pageid AND f.language = r.domain JOIN " + self.weighttable + " AS w ON r.revid = w.revid AND r.domain = w.domain AND w.normal >= 0 JOIN " + self.contenttable + " AS c ON w.revid = c.revid AND w.domain = c.domain LEFT OUTER JOIN " + self.revisiontable + " AS old ON r.parentid = old.revid AND r.domain = old.domain LEFT OUTER JOIN " + self.contenttable + " AS oldcont ON r.parentid = oldcont.revid AND r.domain = oldcont.domain"
        if limit:
            sql += ' LIMIT ' + str(limit)
        sql += ';'
        if(self._execute(sql,())):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def getusersbyeditcount(self, domain):
        sql = "SELECT r.count, count(r.username) FROM (SELECT count(revid) AS count, username FROM " + self.revisiontable + " WHERE domain = %s GROUP BY username ORDER BY count DESC) AS r ORDER BY count DESC;"
        data = (domain,)
        if(self._execute(sql,())):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def geteditdistribution(self, domain=None):
        sql = "SELECT r.count AS edit_count, count(r.username) AS frequency FROM (SELECT count(rev.revid) AS count, rev.username FROM wikirevisions AS rev "
        if domain:
            sql += "WHERE domain = %s "
        sql += "GROUP BY username) AS r GROUP BY r.count ORDER BY r.count;"
        data = (domain,) if domain else ()
        if(self._execute(sql,data)):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def getregeditdistribution(self, domain=None):
        sql = "SELECT r.count AS edit_count, count(r.username) AS frequency FROM (SELECT count(rev.revid) AS count, rev.username FROM wikirevisions AS rev WHERE "
        if domain:
            sql += "domain = %s AND "
        sql += "userid > 0 GROUP BY username) AS r GROUP BY r.count ORDER BY r.count;"
        data = (domain,) if domain else ()
        if(self._execute(sql,data)):
            result = self._crsrsanity()
            if result:
                return result
        return None

    def gettexttypedistribution(self, domain=None):
        sql = "SELECT sum(maths), sum(citations), sum(filesimages), sum(links), sum(structure), sum(normal) FROM " + self.weighttable + " AS wik "
        if domain:
            sql += "WHERE domain = %s "
        sql += ";"
        data = (domain,) if domain else ()
        if(self._execute(sql,data)):
            result = self._crsrsanity()
            if result:
                return result
        return None

    ##########
    ## INTERNAL FUNCTIONS
    ##########

    def _execute(self, sql, data, montcarlo=5):
        try:
            self.crsr.execute(sql, data)
        except:
            print "Unexpected error:", sys.exc_info()
            self.cn.rollback()
        else:
            self.cn.commit()
            return True
        return False

    def _crsrsanity(self):
        cr = self.crsr.fetchall()
        return cr if (len(cr) > 0) else None 

    def __init__(self):
        with open('/homes/wm613/individual-project/WikiInterface/dbpas','r') as pasfil:
            self.password = pasfil.read().strip()
        self.cn = db.connect(host = self.host,
                             user = self.user,
                             password = self.password,
                             dbname = self.database)
        self.crsr = self.cn.cursor()

    def __del__(self):
        self.cn.close()
