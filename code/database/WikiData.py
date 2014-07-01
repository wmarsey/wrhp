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
    revisiontable = "wikiauthors"
    distancetable = "wikidistance"
    trajectorytable = "wikitrajectory"
    cn = None
    crsr = None

    def __init__(self):
        with open('dbpas','r') as pasfil:
            self.password = pasfil.read().strip()
        self.cn = db.connect(host = self.host,
                             user = self.user,
                             password = self.password,
                             dbname = self.database)
        self.crsr = self.cn.cursor()

    def crsrsanity(self):
        return self.crsr.fetchall() if (len(self.crsr.fetchall()) > 0) else None 

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
#return self.crsrsanity()

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

    def getdist(self, param):
        sql = "SELECT distance from " + self.distancetable + " WHERE revid1 = %s AND revid2 = %s;"
        data = (param[0],param[1])
        if(self._execute(sql, data)):
            try:
                result = self.crsr.fetchall()
                return None if not len(result) else result[0][0]
            except:
                print "error", param[0], param[1]
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
        data = ()
        if(self._execute(sql,data)):
            result = self.crsr.fetchall()[0]
            print result[0], result[1]
            return result[0], result[1]
        return None

    def gettrajectory(self, revid):
        sql = "SELECT time, distance FROM " + self.revisiontable + " JOIN " + self.trajectorytable + " ON revid2 = revid WHERE revid1 = %s"
        data = (revid,)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()

    def getgrowth(self, revid):
        sql = "SELECT time, char_length(content) distance FROM " + self.revisiontable + " AS a JOIN " + self.distancetable + " ON revid2 = a.revid JOIN " + self.contenttable + " AS b ON revid2 = b.revid WHERE revid1 = %s"
        data = (revid,)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()

    def getuserchange(self, pageid):
        sql = "SELECT username, sum(distance) FROM " + self.distancetable + " AS a JOIN " + self.revisiontable + " AS b ON a.revid2 = b.revid AND b.pageid = %s GROUP BY username;"
        data = (pageid,)
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
        sql = "INSERT INTO " + self.revisiontable + " VALUES (%s, %s, %s, %s, %s, %s, %s);"
        data = (param[0], param[1], param[2], param[3], param[4], param[5], param[6])
        return self._execute(sql,data)

    def distinsert(self, param):
        if self.getdist([param[0], param[1]]):
            print "distance already stored"
            return False
        sql = "INSERT INTO " + self.distancetable + " VALUES (%s, %s, %s);"
        data = (param[0], param[1], param[2])
        return self._execute(sql,data)

    def trajinsert(self, param):
        if self.gettraj([param[0], param[1]]):
            print "distance already stored"
            return False
        sql = "INSERT INTO " + self.trajectorytable + " VALUES (%s, %s, %s);"
        data = (param[0], param[1], param[2])
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
