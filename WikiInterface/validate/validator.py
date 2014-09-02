from __future__ import division
import numpy as np
import sys, os, inspect
from sklearn import preprocessing as pr
from sklearn import svm, cross_validation, linear_model
import datetime
import cPickle as pickle
from random import choice, shuffle
import re
import matplotlib.pyplot as plt

here = inspect.getfile(inspect.currentframe()) # script filename (usually with path)
BASEPATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

sys.path.append("../")
import database as db

CLASSIFNUM = 4
FOLDS = 5

def fetchdatadump(flags, classnum): 
    extension = '.pickle'
    dfile = BASEPATH + '/data/alldata' + str(classnum) + extension
    
    ##if asked and files exist, load from files
    if flags['load']:
        filepaths = (wfile,)
        for f in filepaths:
            if not os.path.isfile(f):
                print "file", f, "not found, fetching afresh"
                break
        else:
            data = ()
            for f in filepaths:
                data += (pickle.load(open(f, 'rb')),)
                print "loaded file", f
            print "done"
            print 
            return data

    ##get data
    alldata = None
    dtb = db.Database()
    
    if classnum == 0:
        print "Test: can we predict gradient from weights?"
        alldata = dtb.gettrainingdata1(flags['limit'])
    if classnum == 1:
        print "Test: can we predict gradient from weights just on english wikipedia?"
        alldata = dtb.gettrainingdata1(flags['limit'])
    if classnum == 2:
        print "Test: can we predict gradient from weights and username edit count on each article?"
        alldata = dtb.gettrainingdata2(flags['limit'])
    if classnum == 3:
        print "Test: can we predict gradient from weights and username edit count over the whole english wiki?"
        alldata = dtb.gettrainingdata3(flags['limit'], domain='en')
    print "recieved", len(alldata), "cases"

    ##pick a random subgroup if asked
    if flags['clip']:
        print "picking", flags['clip'], "random entries"
        shuffle(alldata)
        alldata = alldata[:flags['clip']]

    print "saving to file"
    with open(dfile, 'wb') as d:
        pickle.dump(alldata,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", dfile
    print
    print "splitting"
    weights, classifications = zip(*[[list(w[:-1]),w[-1]] for w in alldata])
    for i in range(len(weights)):
        for v in range(len(weights[i])):
            weights[i][v] = float(weights[i][v])
    print
    print "got", len(weights[0]), "weights"

    return weights, classifications 

##extra data stuff
def preparedata(weights, classifications):
    ##standardize weights
    print "standardizing weights, numpyfying classifications"
    return pr.scale(np.array(weights)), np.array(classifications)

##feed into sklearn
def train(data, target, foldnum):

    model = linear_model.SGDRegressor(penalty='elasticnet', 
                                      shuffle=True, 
                                      fit_intercept=False) 
    model.fit(data, target)
    print model
    scores = cross_validation.cross_val_score(model, data, target, cv=foldnum)  
    
    return sum(scores) / len(scores)

##sort out sys.argv
def flagargs(a):
    if '--load' in a and '--clip-' in a:
        print "Can't use 'load' and 'clip' arguments together right now!"
        sys.exit(-1)
    results = {'load': True if "--load" in a else False,
               'clip': a[a.index("--clip") + 1] if "--clip" in a else None,
               'limit': a[a.index("--limit") + 1] if "--limit" in a else None}
    return results

# def thatplt():
#     dtb = db.Database()
#     fig = plt.figure()
#     ax1 = fig.add_subplot(111)
#     x,y = zip(*dtb.getcounttogradient())
#     ax1.scatter(x,y, c='b', label='blue')
#     x,y = zip(*dtb.getlinkstogradient())
#     ax1.scatter(x,y, c='g', label='green')
#     fig.show()

def main():
    flags = flagargs(sys.argv)
    print
    print "--------------------VALIDATION HAPPENING--------------------"
    for c in xrange(CLASSIFNUM):
        weights, classifications = fetchdatadump(flags, c) 
        pweights, ptargets = preparedata(weights, classifications)
        print "training"    
        performance = train(pweights, ptargets, FOLDS)
        print "Performance over", FOLDS, "folds:", performance
        print
    
if __name__=="__main__":
    main()
    sys.exit(0)
