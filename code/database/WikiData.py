import psycopg2 as db
import sys
import re

class Database:
    host = 'db-new.doc.ic.ac.uk'
    port = '5432'
    database = 'wm613'
    user = 'wm613'
    password = ''
    contenttable = "wikicontent"
    revisiontable = "wikiauthors"
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

    def getextantrevs(self, pageid):
        sql = "SELECT revid FROM " + self.revisiontable + " WHERE pageid = %s ORDER BY revid;"
        data = (pageid,)
        if(self._execute(sql,data)):
            return self.crsr.fetchall()
        return None

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
        if self.getrevcontent(param[0]):
            print "content already exists"
            return False
        sql = "INSERT INTO " + self.revisiontable + " VALUES (%s, %s, %s, %s, %s, %s, %s);"
        data = (param[0], param[1], param[2], param[3], param[4], param[5], param[6])
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
