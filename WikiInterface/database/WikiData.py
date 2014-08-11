import psycopg2 as db
import sys
import re
import random

class Database:
    host = 'db-new.doc.ic.ac.uk'
    port = '5432'
    database = 'wm613'
    user = 'wm613'
    password = ''
    contenttable = "wikicontent"
    revisiontable = "wikirevisions"
    distancetable = "wikidistance"
    trajectorytable = "wikitrajectory"
    fetchedtable = "wikifetched"
    difftable = "wikidiff"
    cn = None
    crsr = None

    def __init__(self):
        with open('/homes/wm613/individual-project/WikiInterface/dbpas','r') as pasfil:
            self.password = pasfil.read().strip()
        self.cn = db.connect(host = self.host,
                             user = self.user,
                             password = self.password,
                             dbname = self.database)
        self.crsr = self.cn.cursor()

    def crsrsanity(self):
        cr = self.crsr.fetchall()
        return cr if (len(cr) > 0) else None 

    def revexist(self, revid, parentid, domain):
        sql = "SELECT revid, parentid FROM " + self.revisiontable + " WHERE revid = %s AND parentid = %s AND domain = %s;"
        data = (revid, parentid, domain)
        if(self._execute(sql, data)):
            result = self.crsrsanity()
            if result:
                return True
        return False

    def getparent(self, revid, domain):
        sql = "SELECT parentid FROM " + self.revisiontable + " WHERE revid = %s AND domain = %s;"
        data = (revid,domain)
        if(self._execute(sql, data)):
            result = self.crsrsanity()
            if result:
                return result[0][0]
        return -1

    def getchild(self, parentid, domain):
        sql = "SELECT revid FROM " + self.revisiontable + " WHERE parentid = %s AND domain = %s;"
        data = (parentid,domain)
        if(self._execute(sql, data)):
            result = self.crsrsanity()
            if result:
                return result[0][0]
        return -1

    def bridgerevision(self, revid, parentid):
        alterchild = self.getchild(revid)
        sql = "UPDATE " + self.revisiontable + " SET parentid = %s WHERE revid = %s;"
        data = (parentid,alterchild)
        if(self._execute(sql, data)):
            return True
        return False

    def gettime(self, data):
        sql = "SELECT time FROM " + self.revisiontable + " WHERE revid = %s;"
        if(self._execute(sql, data)):
            return self.crsrsanity()[0][0]
        return None
    
    def gettrajheight(self, data):
        sql = "SELECT distance FROM " + self.trajectorytable + " WHERE revid2 = %s;"
        if(self._execute(sql, data)):
            result = self.crsrsanity()
            if result:
                return result[0][0]
        return None
        
    def getextantrevs(self, pageid, domain):
        #print "looking for", pageid, domain
        sql = "SELECT revid FROM " + self.revisiontable + " WHERE pageid = %s AND domain = %s ORDER BY time DESC;"
        data = (pageid,domain)
        if(self._execute(sql,data)):
            result = self.crsrsanity()
            if result:
                return [e[0] for e in result]
        return None

    def gettimestamp(self, revid):
        sql = "SELECT time FROM " + self.revisiontable + " WHERE revid = %s;"
        data = (revid,)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()

    def getyoungestrev(self, pageid):
        sql = "SELECT revid FROM " + self.revisiontable + " AS a WHERE pageid = %s AND NOT EXISTS (SELECT * FROM " + self.revisiontable + " AS b WHERE pageid = %s AND b.time > a.time);"
        data = (pageid,pageid)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()
        return None

    def getrevcontent(self, revid, domain):
        sql = "SELECT content FROM " + self.contenttable + " WHERE revid = %s AND domain = %s;"
        data = (revid,domain)
        if(self._execute(sql, data)):
            result = self.crsrsanity()
            if result:
                return result[0][0]
        return None

    def getrevinfo(self, revid, domain):
        sql = "select revid from " + self.revisiontable + " where revid = %s AND domain = %s;"
        data = (revid,domain)
        if(self._execute(sql, data)):
            return self.crsr.fetchall()
        return None

    def getrevfull(self, titles="random", revids=None, userids=None):
        sql = "SELECT * from " + self.contenttable + " AS a JOIN " + self.revisiontable + " AS b ON a.revid = b.revid AND a.revid = %s;"
        data = (revid,)
        if(self._execute(sql, data)):
            return self.crsr.fetchall()
        return None

    def getdist(self, revid):
        sql = "SELECT distance from " + self.distancetable + " WHERE revid = %s;"
        data = (revid,)
        if(self._execute(sql, data)):
            try:
                result = self.crsrsanity()
                if result:
                    return result[0][0]
            except:
                print "error", revid
                pass
        return -1
    
    def gettraj(self, param):
        #print "looking for", param[0], param[1]
        sql = "SELECT distance from " + self.trajectorytable + " WHERE revid1 = %s AND revid2 = %s;"
        data = (param[0],param[1])
        if(self._execute(sql, data)):
            try:
                result = self.crsrsanity()
                if result:
                    return result[0][0]
            except:
                print "error", param[0], param[1]
                pass
        return -1

    def getrandom(self):
        sql = "SELECT * FROM (SELECT DISTINCT title, pageid FROM " + self.fetchedtable + ") AS w OFFSET random()*(SELECT count(*) FROM (SELECT DISTINCT title FROM " + self.fetchedtable + ") AS w2) LIMIT 1;"
        while True:
            if(self._execute(sql,())):
                try: 
                    result = self.crsr.fetchall()[0]
                except:
                    pass
                else:
                    return result[0], result[1]
        return None

    def gettrajectory(self, revid):
        sql = "SELECT time, distance FROM " + self.revisiontable + " JOIN " + self.trajectorytable + " ON revid2 = revid WHERE revid1 = %s ORDER BY time;"
        data = (revid,)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()

    def getgrowth(self, revid):
        sql = "SELECT time, size FROM " + self.revisiontable + " AS a JOIN " + self.trajectorytable + " AS b ON b.revid2 = a.revid WHERE revid1 = %s ORDER BY time;"
        data = (revid,)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()

    def getuserchange(self, pageid):
        sql = "SELECT username, sum(distance), sum(maths), sum(headings), sum(quotes), sum(filesimages), sum(links), sum(citations), sum(normal) FROM " + self.distancetable + " AS a JOIN " + self.revisiontable + " AS b ON a.revid = b.revid AND b.pageid = %s GROUP BY username;"
        data = (pageid,)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()
        return None
    
    def getusereditcounts(self, revx):
        sql = "SELECT username, count(distance) FROM " + self.distancetable + " AS a JOIN " + self.revisiontable + " AS b ON a.revid = b.revid AND b.pageid = %s GROUP BY username;"
        data = (revx,)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()
        return None  

    def getuserinfo(self, revx):
        sql = "SELECT DISTINCT c.username, c.userid FROM " + self.trajectorytable + " AS b JOIN " + self.revisiontable + " as c ON b.revid1 = %s AND b.revid2 = c.revid";
        data = (revx,)
        if(self._execute(sql,data)):
            return self.crsrsanity()
        return None 
    
    def existencequery(self, sql, data):
        self.crsr._execute(sql, data)
        return cursor.fetchall()

    def getfetched(self, pageid):
        sql = "SELECT language FROM " + self.fetchedtable + " WHERE pageid = %s";
        if(self._execute(sql, (pageid,))):
            result = self.crsrsanity()
            if result:
                return result[0][0]
        return None

    def fetchedinsert(self, param):
        if self.getfetched(param[0]):
            return False
        sql = "INSERT INTO " + self.fetchedtable + " VALUES (%s, %s, %s);"
        return self._execute(sql, param)

    def getdiff(self, params):
        sql = "SELECT * FROM " + self.difftable + " WHERE fromrev = %s AND torev = %s AND line = %s AND action = %s;";
        if(self._execute(sql, params)):
            result = self.crsrsanity()
            if result:
                return True
        return False

    # def getdifftexts(self, oldrev, newrev):
    #     texts = []
    #     for a in ("deleted", "added"):
    #         sql = "SELECT diff FROM " + self.difftable + " WHERE fromrev = %s AND torev = %s AND action = %s;"
    #         textpile = ""
    #         if(self._execute(sql, (oldrev, newrev, a))):
    #             result = self.crsrsanity()
    #             if result:
    #                 #print a, len(result), result
    #                 for r in result:
    #                     #print r[0]
    #                     textpile = textpile + r[0]
    #                 #texts.append(result[0][0])
    #                 # linepile = ""
    #                 # print a, result[0][0], result[0][1]
    #                 # lines = result[0][1][1:-1].split(',')
    #                 # print a, result[0][0], len(lines), lines
    #                 # for line in result[0][0]:
    #                 #     linepile = linepile + line + "\n"
    #                 # texts.append(linepile)
    #         texts.append(textpile)
    #     return texts

    # def diffinsert(self, param):
    #     if self.getdiff(param[:-2]):
    #         return False
    #     sql = "INSERT INTO " + self.difftable + " VALUES (%s, %s, %s, %s, %s, %s);"
    #     return self._execute(sql, param)

    def contentinsert(self, param):
        #print "inserting content", param[0],param[-1]
        if self.getrevcontent(param[0],param[-1]):
            return False
        sql = "INSERT INTO " + self.contenttable + " VALUES (%s, %s, %s, %s);"
        return self._execute(sql, param)

    def indexinsert(self, param):
        #print "inserting index", param[0],param[-1]
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

    def trajinsert(self, data):
        sql = "INSERT INTO " + self.trajectorytable + " VALUES (%s, %s, %s);"
        return self._execute(sql,data)

    def _execute(self, sql, data, montcarlo=5):
        for _ in xrange(montcarlo):
            try:
                self.crsr.execute(sql, data)
            except:
                print "Unexpected error:", sys.exc_info()
                self.cn.rollback()
            else:
                self.cn.commit()
                return True
        print "sql execution failed"
        return False

    def __del__(self):
        self.cn.close()
