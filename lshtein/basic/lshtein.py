def printg(x,y,g):
    result = ""
    for ch in y:
        result = result + ch + "  "
    print "       ", result
    for r in range(len(g)):
        s = " "
        if r != 0:
            s = x[r-1]
        print s, " ", g[r]

def printpserve(i,j,e):
    if e[i][j] == " ":
        if i == 0 and j > 0:
            print "insert", y[0]
        if j == 0 and i > 0:
            print "delete", x[0]
        return
    if e[i][j] == "keep":
        printpserve(i-1, j-1, e)
        print e[i][j], x[i-1]
    elif e[i][j] == "swap":
        printpserve(i-1, j-1, e)
        print e[i][j], x[i-1], "for", y[i-1]
    elif e[i][j] == "delete":
        printpserve(i-1,j,e)
        print e[i][j], x[i-1]
    else:
        printpserve(i,j-1,e)
        print e[i][j], y[j-1]    

def printp(x,y,e):
    print "edit operation:"
    i,j = len(e)-1, len(e[0])-1
    return printpserve(i,j,e)
    

##naive version
def levdist1(x,y):
    m = len(x) + 1
    n = len(y) + 1
    d = [[0]*(n) for _ in xrange(m)]
    e = [[" "]*(n) for _ in xrange(m)]
    for i in xrange(m):
        d[i][0] = i
    for j in xrange(n):
        d[0][j] = j
    j = 1
    while j < n:
        i = 1
        while i < m:
            c = (x[i-1] != y[j-1])
            dl = d[i-1][j] + 1
            ins = d[i][j-1] + 1
            sbs = d[i-1][j-1] + c
            d[i][j] = min(ins, dl, sbs)
            if ins < dl and ins - 1 < sbs:
                e[i][j] = "insert"
            elif dl <= sbs:
                e[i][j] = "delete"
            else:
                if(x[i-1] != y[j-1]):
                    e[i][j] = "swap"
                else:
                    e[i][j] = "keep"
            i += 1
        j += 1
    printg(x,y,d)
    printp(x,y,e)        
    return d[m-1][n-1]

##some space optimisation, base cases
def levdist2(x,y):
    if len(x) < len(y):
        return levenshtein(y, x)
    if len(y) == 0:
        return len(x)
    row = xrange(len(y) + 1)
    for i, xch in enumerate(x):
        newrow = [i + 1]
        for j, ych in enumerate(y):
            c = (xch != ych)
            ins = row[j + 1] + 1 #insertions
            dl = newrow[j] + 1 #deletions
            sbs = row[j] + c #substitutions
            newrow.append(min(ins, dl, sbs))
        row = newrow 
    return row[-1]

x = "empirical"
y = "imperial"
l = levdist1(x, y)    
print "Levenstein distance between", x, "and", y, "is", l
x = "mperial"
y = "empirical"
l = levdist1(x, y)    
print "Levenstein distance between", x, "and", y, "is", l
x = "bank"
y = "book"
l = levdist1(x, y)
print "Levenstein distance between", x, "and", y, "is", l

x = "empirical"
y = "imperial"
l = levdist2(x, y)    
print "Levenstein distance between", x, "and", y, "is", l
x = "bank"
y = "book"
l = levdist2(x, y)
print "Levenstein distance between", x, "and", y, "is", l
