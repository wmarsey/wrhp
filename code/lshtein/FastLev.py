import sys
import random 

class FastLev:
    x = "" #string1
    y = "" #string2
    m = 0 #length string1
    n = 0 #length string2
    dist = 0 #Levenshtein distance
    
    def __init__(self, _x, _y):
        self.x = _x
        self.y = _y
        self.m = len(self.x)
        self.n = len(self.y)     
        self.dist = self._calculate()
    
    def __str__(self):
        return str(self.distance())

    def distance(self):
        return self.dist

    def strings(self):
        return self.x, self.y
    
    def operation(self):
        return self.ed

    def _calculate(self):
        lrow = None
        crow = [0] + range(1, self.n + 1)
        for i in xrange(self.m):
            lrow, crow = crow, [i+1] + [0] * self.n
            j = 1
            while j < self.n+1:
                dl = lrow[j] + 1
                ins = crow[j - 1] + 1
                sub = lrow[j - 1] + (self.x[i] != self.y[j-1])
                crow[j] = min(dl, ins, sub)
                j = j + 1
        return crow[-1]

def main():
    words = ["string", "strung", "pork", "book", "books", "spork"]
    for _ in xrange(0,6):
        x = random.choice(words)
        y = random.choice(words)
        lev = FastLev(x,y)
        print "distance between", x, "and", y, "is", lev
        del lev

if __name__ == "__main__":
    main()
