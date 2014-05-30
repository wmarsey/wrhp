class LevDistBasic:
    e = [] #edit operation array
    t = [] #grid array
    x = "" #string1
    y = "" #string2
    m = 0 #length string1
    n = 0 #length string2
    dist = 0 #Levenshtein distance
    ed = [] #the edit operation, calculated in _calculate()
    
    def __init__(self, _x, _y):
        self.x = _x
        self.y = _y
        self.m = len(_x)
        self.n = len(_y)     
        self.t = [[0]*(self.n+1) for _ in xrange(self.m+1)]
        self.e = [[" "]*(self.n+1) for _ in xrange(self.m+1)]
        self.dist = self._calculate()
    
    def __str__(self):
        return str(self.distance())

    def distance(self):
        return self.dist

    def strings(self):
        return self.x, self.y
    
    def table(self):
        return self.t
    
    def operation(self):
        return self.ed
        
    ##ADD WARNING for long strings / deal with them
    def showtable(self):
        result = ""
        for ch in self.y:
            result = result + ch + "  "
        print "       ", result
        for r in range(len(self.t)):
            s = ' '
            if r:
                s = self.x[r-1]
            print s, ' ', self.t[r]
    
    def showop(self):
        for i, op in enumerate(self.ed):
            l = str(i) + ": "
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

    def _ed(self):
        i, j = len(self.e)-1, len(self.e[0])-1
        self._ed_recursive(i,j)

    def _ed_recursive(self,i,j):
        if self.e[i][j] == ' ':
            if i == 0 and j > 0:
                self.ed.append(('D', self.y[0]))
            if j == 0 and i > 0:
                self.ed.append(('D', self.x[0]))
            return
        if self.e[i][j] == 'K':
            self._ed_recursive(i-1, j-1)
            self.ed.append((self.e[i][j], self.x[i-1]))
        elif self.e[i][j] == 'S':
            self._ed_recursive(i-1, j-1)
            self.ed.append((self.e[i][j], (self.x[i-1] + ',' + self.y[j-1])))
        elif self.e[i][j] == 'D':
            self._ed_recursive(i-1,j)
            self.ed.append((self.e[i][j], self.x[i-1]))
        else:
            self._ed_recursive(i,j-1)
            self.ed.append((self.e[i][j], self.y[j-1]))   

    def _calculate(self):
        for i in xrange(self.m+1):
            self.t[i][0] = i
        for j in xrange(self.n+1):
            self.t[0][j] = j
        j = 1
        while j < self.n+1:
            i = 1
            while i < self.m+1:
                c = (self.x[i-1] != self.y[j-1])
                dl = self.t[i-1][j] + 1
                ins = self.t[i][j-1] + 1
                sbs = self.t[i-1][j-1] + c
                self.t[i][j] = min(ins, dl, sbs)
                if ins < dl and ins < sbs:
                    self.e[i][j] = 'I'
                elif dl <= sbs:
                    self.e[i][j] = 'D'
                else:
                    if(self.x[i-1] != self.y[j-1]):
                        self.e[i][j] = 'S'
                    else:
                        self.e[i][j] = 'K'
                i += 1
            j += 1
        self._ed()
        return self.t[self.m][self.n]
