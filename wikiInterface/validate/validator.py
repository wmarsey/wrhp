from __future__ import division
import numpy as np
import sys, os, inspect
from sklearn.preprocessing import scale
from sklearn.linear_model import Lasso, SGDClassifier
from sklearn import cross_validation
import datetime
import cPickle as pickle
from random import choice, shuffle
import re
import matplotlib.pyplot as plt

here = inspect.getfile(inspect.currentframe()) # script filename (usually with path)
BASEPATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

sys.path.append(os.path.abspath('..'))
import database as db

CLASSIFNUM = 12
FOLDS = 10

##########
## Fetch from database, pickle 
##########
def fetchdatadump(flags, classnum): 
    extension = '.pickle'
    dfile = BASEPATH + '/data/alldata' + str(classnum) + extension
    
    ##get data
    alldata = None
    dtb = db.WikiDatabase()
    
    if classnum == 0:
        print "Test: can we predict gradient from weights?"
        alldata = dtb.gettrainingdata1()
    if classnum == 1:
        print "Test: can we predict gradient from weights and size?"
        alldata = dtb.gettrainingdata2()
    if classnum == 2:
        print "Test: can we predict gradient from weights and time change?"
        alldata = dtb.gettrainingdata3()
    if classnum == 3:
        print "Test: can we predict gradient from summed weights and size?"
        alldata = dtb.gettrainingdata4()    
    if classnum == 4:
        print "Test: can we predict gradient from weights and username edit count over the whole english wiki?"
        alldata = dtb.gettrainingdata5()
    if classnum == 5:
        print "Test: can we predict gradient from weights and username edit count over the whole english wiki?"
        alldata = dtb.gettrainingdata6()
    if classnum == 7:
        print "Test: can we predict gradient from weights? (classification)"
        alldata = dtb.gettrainingdata1()
    if classnum == 8:
        print "Test: can we predict gradient from weights and size? (classification)"
        alldata = dtb.gettrainingdata2()
    if classnum == 9:
        print "Test: can we predict gradient from weights and time change? (classification)"
        alldata = dtb.gettrainingdata3()
    if classnum == 10:
        print "Test: can we predict gradient from summed weights and size? (classification)"
        alldata = dtb.gettrainingdata4()    
    if classnum == 11:
        print "Test: can we predict gradient from weights and username edit count over the whole english wiki? (classification)"
        alldata = dtb.gettrainingdata5()
    if classnum == 12:
        print "Test: can we predict gradient from weights and username edit count over the whole english wiki? (classification)"
        alldata = dtb.gettrainingdata6()

    print "recieved", len(alldata), "cases"

    ##pick a random subgroup if asked
    if flags['clip']:
        print "picking", flags['clip'], "random entries"
        shuffle(alldata)
        alldata = alldata[:flags['clip']]

    print "splitting"
    weights, classifications = zip(*[[list(w[:-1]),\
                                          (0 if w[-1] < 0.5 else 1) \
                                          if classnum > 5 else w[-1]] \
                                         for w in alldata])
    for i in range(len(weights)):
        for v in range(len(weights[i])):
            weights[i][v] = float(weights[i][v])
    print "got", len(weights[0]), "weights"

    return weights, classifications 

##########
## some data processing necessary 
##########
def preparedata(weights, classifications):
    print "standardizing weights, numpyfying classifications"
    return scale(np.array(weights)), np.array(classifications)

##########
## Prepare and train using sklearn 
##########
def train(data, target, foldnum, classnum):

    if classnum > 5:
        model = SGDClassifier(loss="hinge", penalty="l2")
    else:
        model = Lasso() 
    scores = cross_validation.cross_val_score(model, data, target, cv=foldnum,verbose=1,n_jobs=-1)  
    
    return sum(scores) / len(scores)

##########
## Simple argument processing 
##########
def flagargs(a):
    if '--load' in a and '--clip-' in a:
        print "Can't use 'load' and 'clip' arguments together right now!"
        sys.exit(-1)
    results = {'load': True if "--load" in a else False,
               'clip': a[a.index("--clip") + 1] if "--clip" in a else None,
               'limit': a[a.index("--limit") + 1] if "--limit" in a else None}
    return results

##########
## Runs tests 
##########
def main():
    flags = flagargs(sys.argv)
    print
    print "--------------------VALIDATION HAPPENING--------------------"
    for c in xrange(CLASSIFNUM):
        weights, classifications = fetchdatadump(flags, c) 
        pweights, ptargets = preparedata(weights, classifications)
        print "training"    
        performance = train(pweights, ptargets, FOLDS, c)
        print "Performance over", FOLDS, "folds:", performance
        print
    
if __name__=="__main__":
    main()
    sys.exit(0)
