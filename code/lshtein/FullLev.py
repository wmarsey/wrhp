import sys
import copy
import cPickle

INDIC = {
    'insert':'I',
    'delete':'D',
    'swap':'S',
    'keep':'K'
    }

class FullLev:
    x = "" #string1
    y = "" #string2
    m = 0 #length string1
    n = 0 #length string2
    dist = 0 #Levenshtein distance
    ed = [] #the edit operation, calculated in _calculate()
    isFile = False
    dots = 0
    
    def __init__(self, _x, _y, isFile=False):
        self.x = self._variablehandle(_x)
        self.y = self._variablehandle(_y)
        self.m = len(self.x)
        self.n = len(self.y)     
        self.dist, self.ed = self._calculate()
    
    def __str__(self):
        return str(self.distance())

    def distance(self):
        return self.dist

    def strings(self):
        return self.x, self.y
    
    def operation(self):
        return self.ed

    def dot(self):
        self.dots = self.dots + 1 
        sys.stdout.write('.')
        if not (self.dots % 100):
            sys.stdout.write('|')
        if not (self.dots % 1000):
            sys.stdout.write('_.-~^`')
    
    def showop(self):
        for i, op in enumerate(self.ed):
            l = str(i+1) + ": "           
            ins, keep, swap, dl = INDIC 

            if op[0] == INDIC[ins]:
                l += "insert " + op[-1]
            elif op[0] == INDIC[keep]:
                l += "keep " + op[-1]
            elif op[0] == INDIC[dl]:
                l += "delete " + op[-1]
            elif op[0] == INDIC[swap]:
                l += "swap " + op[-1][0] + " for " + op[-1][-1]
            else:
                return "FAIL: incorrect operation"
            print l 

    def _variablehandle(self,v):
        if not isinstance(v, str):
            try:
                return v.read()
            except:
                try:
                    return str(v)
                except:
                    print "Argument cannot be of type" + type(v)
                    raise
                pass
        return v

    def _calculate(self):
        self.dot()
        lrow = None
        crow = [{'ed':list(),'len':0} for _ in xrange(self.n+1)]
        for i in xrange(self.n):
            self.dot()
            crow[i+1] = cPickle.loads(cPickle.dumps(crow[i]))
            crow[i+1]['ed'].append((INDIC['insert'],self.y[i]))
            crow[i+1]['len'] = crow[i+1]['len'] + 1
        for i in xrange(self.m):
            self.dot()
            lrow, crow = crow, [{'ed':list(),'len':0} for _ in xrange(self.n+1)]
            crow[0] = cPickle.loads(cPickle.dumps(lrow[0]))
            crow[0]['ed'].append((INDIC['delete'],self.x[i]))
            crow[0]['len'] = crow[0]['len'] + 1
            j = 1
            while j < self.n+1:
                c = (self.x[i] != self.y[j-1])
                dl = lrow[j]['len'] + 1
                ins = crow[j-1]['len'] + 1
                sub = lrow[j-1]['len'] + c
                if ins < dl and ins < sub:
                    crow[j] = cPickle.loads(cPickle.dumps(crow[j-1]))
                    crow[j]['ed'].append((INDIC['insert'],self.y[j-1]))
                    crow[j]['len'] = crow[j]['len'] + 1
                elif dl < sub:
                    crow[j] = cPickle.loads(cPickle.dumps(crow[j-1]))
                    crow[j]['ed'].append((INDIC['delete'],self.x[i]))
                    crow[j]['len'] = crow[j]['len'] + 1
                else:
                    crow[j] = cPickle.loads(cPickle.dumps(lrow[j-1]))
                    if(self.x[i] != self.y[j-1]):
                        crow[j]['ed'].append((INDIC['swap'],self.x[i] + self.y[j-1]))
                        crow[j]['len'] = crow[j]['len'] + 1
                    else:
                        crow[j]['ed'].append((INDIC['keep'],self.x[i]))
                self.dot()
                j = j+1
        return crow[-1]['len'], crow[-1]['ed']
