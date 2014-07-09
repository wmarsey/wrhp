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
    cn = None
    crsr = None

    def __init__(self):
        with open('/homes/wm613/individual-project/code/dbpas','r') as pasfil:
            self.password = pasfil.read().strip()
        self.cn = db.connect(host = self.host,
                             user = self.user,
                             password = self.password,
                             dbname = self.database)
        self.crsr = self.cn.cursor()

    def crsrsanity(self):
        return self.crsr.fetchall() if (len(self.crsr.fetchall()) > 0) else None 

    def revexist(self, revid, parentid):
        sql = "SELECT revid, parentid FROM " + self.revisiontable + " WHERE revid = %s AND parentid = %s;"
        data = (revid, parentid)
        if(self._execute(sql, data)):
            result = self.crsr.fetchall()
            if len(result) > 0:
                return True
        return False

    def getparent(self, revid):
        sql = "SELECT parentid FROM " + self.revisiontable + " WHERE revid = %s;"
        data = (revid,)
        if(self._execute(sql, data)):
            result = self.crsr.fetchall()
            if len(result) > 0:
                return result[0][0]
        return -1

    def getchild(self, parentid):
        sql = "SELECT revid FROM " + self.revisiontable + " WHERE parentid = %s;"
        data = (parentid,)
        if(self._execute(sql, data)):
            result = self.crsr.fetchall()
            if len(result) > 0:
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
            return crsrsanity()[0]
        return None
    
    def gettrajheight(self, data):
        sql = "SELECT distance FROM " + self.trajectorytable + " WHERE revid2 = %s;"
        if(self._execute(sql, data)):
            return crsrsanity()[0]
        return None
        
    def getextantrevs(self, pageid):
        sql = "SELECT revid FROM " + self.revisiontable + " WHERE pageid = %s ORDER BY revid;"
        data = (pageid,)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()
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

    def getrevcontent(self, revid):
        sql = "SELECT content FROM " + self.contenttable + " WHERE revid = %s;"
        data = (revid,)
        if(self._execute(sql, data)):
            return self.crsr.fetchall()
        return None

    def getrevinfo(self, revid):
        sql = "select revid from " + self.revisiontable + " where revid = %s;"
        data = (revid,)
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
                result = self.crsr.fetchall()
                return None if not len(result) else result[0][0]
            except:
                print "error", revid
                pass
        return None
    
    def gettraj(self, param):
        sql = "SELECT distance from " + self.trajectorytable + " WHERE revid1 = %s AND revid2 = %s;"
        data = (param[0],param[1])
        if(self._execute(sql, data)):
            try:
                result = self.crsr.fetchall()
                return None if not len(result) else result[0][0]
            except:
                print "error", param[0], param[1]
                pass
        return None

    def getrevid(self, title):
        sql = "SELECT revid FROM " + self.contenttable + " WHERE title = %s LIMIT 1;"
        data = (title,)
        if(self._execute(sql,data)):
            return self.crsrsanity()
        return None 

    def getrandom(self):
        sql = "SELECT * FROM (SELECT DISTINCT title, pageid FROM " + self.contenttable + ") AS w OFFSET random()*(SELECT count(*) FROM (SELECT DISTINCT title FROM " + self.contenttable + ") AS w2) LIMIT 1;"
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
        sql = "SELECT time, size FROM " + self.revisiontable + " AS a JOIN " + self.trajectorytable + " ON revid2 = a.revid WHERE revid1 = %s ORDER BY time;"
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
    
    def existencequery(self, sql, data):
        self.crsr._execute(sql, data)
        return cursor.fetchall()

    def contentinsert(self, param):
        if self.getrevcontent(param[0]):
            print "content already exists"
            return False
        sql = "INSERT INTO " + self.contenttable + " VALUES (%s, %s, %s, %s);"
        data = (param[0],param[1],param[2],param[3])
        return self._execute(sql,data)

    def indexinsert(self, param):
        if self.getrevinfo(param[0]):
            print "content already exists"
            return False
        sql = "INSERT INTO " + self.revisiontable + \
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        data = (param[0], 
                param[1], 
                param[2], 
                param[3], 
                param[4], 
                param[5], 
                param[6], 
                param[7])
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
