import sys

class LevDistBasic:
    x = "" #string1
    y = "" #string2
    m = 0 #length string1
    n = 0 #length string2
    dist = 0 #Levenshtein distance
    ed = [] #the edit operation, calculated in _calculate()
    isFile = False
    
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
    
    def showop(self):
        for i, op in enumerate(self.ed):
            l = str(i+1) + ": "
            if op[0] == 'I':
                l += "insert " + op[-1]
            elif op[0] == 'K':
                l += "keep " + op[-1]
            elif op[0] == 'D':
                l += "delete " + op[-1]
            elif op[0] == 'S':
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
        lrow = None
        crow = [list() for _ in xrange(self.n+1)]
        for i in xrange(self.n):
            ed = list(crow[i])
            crow[i+1] = ed
            crow[i+1].append(('I',self.y[i]))
        printrow(crow)
        for i in xrange(self.m):
            lrow, crow = crow, [list() for _ in xrange(self.n+1)]
            crow[0] = list(lrow[0])
            crow[0].append(('D',self.x[i]))
            j = 1
            while j < self.n+1:
                c = (self.x[i] != self.y[j-1])
                dl = len(lrow[j]) + 1
                ins = len(crow[j-1]) + 1
                sub = len(lrow[j-1]) + c
                if ins < dl and ins < sub:
                    crow[j] = list(crow[j-1])
                    crow[j].append(('I',self.y[j-1]))
                    # print "(", i+1, ",", j, ")", "insert"
                elif dl < sub:
                    crow[j] = list(crow[j-1])
                    crow[j].append(('D',self.x[i]))
                    # print "(", i+1, ",", j, ")", "delete"
                else:
                    # print "(", i+1, ",", j, ")", "swapkeep"
                    crow[j] = list(lrow[j-1])
                    if(self.x[i] != self.y[j-1]):
                        crow[j].append(('S',self.x[i] + self.y[j-1]))
                j = j+1
            printrow(crow)
        return len(crow[-1]), crow[-1]
