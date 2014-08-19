from __future__ import division
import numpy as np
import sys, os, inspect
from sklearn import preprocessing as pr
from sklearn import svm, cross_validation, linear_model
import datetime
import cPickle as pickle
from random import choice, shuffle

here = inspect.getfile(inspect.currentframe()) # script filename (usually with path)
BASEPATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

sys.path.append("../")
import database as db

CLASSIFNUM = 11
FOLDS = 20

def fetchdatadump(flags): 
    rfile = BASEPATH + '/data/revs' + extension
    wfile = BASEPATH + '/data/weights' + extension
    confile = BASEPATH + '/data/contents' + extension
    oldconfile = BASEPATH + '/data/oldcontents' + extension
    comfile = BASEPATH + '/data/comments' + extension
    
    ##if asked and files exist, load from files
    if flags['load']:
        filepaths = (rfile, wfile, confile, comfile)
        for f in filepaths:
            if not os.path.isfile(fname):
                print "file", fname, "not found, fetching afresh"
                break
        else:
            data = ()
            for f in filepaths:
                data += (pickle.load(f),)
                print "loaded file", f
            print "done"
            print 
            return data

    ##get data
    alldata = None
    dtb = db.Database()
    alldata = dtb.getdatadump()
    print "recieved", len(alldata), "entries"

    ##pick a random subgroup if asked
    if flags['clip']:
        print "picking", flags['clip'], "random entries"
        shuffle(alldata)
        alldata = alldata[:flags['clip']]

    ##break up tuples returned from database
    print "splitting" 
    revs = []
    weights = []
    contents = []
    oldcontents = []
    comments = []
    for i,d in enumerate(alldata):
        rev, weight, content, pcontent, comment = list(d[:2]),list(d[2:-3]),d[-3], d[-2],d[-1]
        revs.append(rev)
        weights.append(weight)
        contents.append(content)
        oldcontents.append(pcontent)
        comments.append(comment)
    print "done"
    print

    ##check to make sure database left join didn't go funny
    for i, w in enumerate(weights):
        for v,ww in enumerate(w):
            if ww == None:
                print ww, i, v
                
    ##save files
    print "saving to file"
    with open(rfile, 'wb') as d:
        pickle.dump(revs,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", rfile
    with open(wfile, 'wb') as d:
        pickle.dump(weights,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", wfile
    with open(confile, 'wb') as d:
        pickle.dump(contents,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", confile
    with open(oldconfile, 'wb') as d:
        pickle.dump(oldcontents,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", oldconfile
    with open(comfile, 'wb') as d:
        pickle.dump(comments,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", comfile
        
    return revs, weights, contents, comments

def classify(weights, contents, comments, classnum):
    scores = []

    if classnum == 0:
        print "Classification type: classification is same as gradient"
        print "Expected success: v high (the gradient is one of the supplied weights)"
        for i, w in enumerate(weights):
            scores.append(w[-1])

    elif classnum == 1:
        largest = 0
        print "Classification type: number of times random vowel appears in comments"
        print "Expected success: v low (hard to guess)"
        vowel = choice(['a','e','i','o','u'])
        print "(Chosen vowel:", vowel, ")"
        for i,c in enumerate(comments):
            count = 0
            for ch in c:
                if vowel == ch:
                    count += 1
            scores.append(count)

    elif classnum == 2:
        largest = 0
        print "Classification type: sum of weights, times gradient"
        print "Expected success: unsure"
        for i,w in enumerate(weights):
            tsum = sum(w[:-3])
            gradient = w[-2]
            num = tsum * gradient
            scores.append(num)
        
    elif classnum == 3:
        largest = 0
        print "Classification type: smaller changes better than bigger ones"
        print "Expected success: unsure"
        for i,w in enumerate(weights):
            tsum = sum(w[:-3])
            gradient = w[-2]
            num = tsum * gradient
            if num > largest:
                largest = num
            scores.append(num)

    elif classnum == 4:
        print "classification type: non-normal is good."
        print "Expected success: high"
        for i, w in enumerate(weights):
            scores.append(sum(w[:-3]))

    elif classnum == 5:
        print "classification type: maths is good."
        print "Expected success: high"
        for i, w in enumerate(weights):
            scores.append(w[0])

    elif classnum == 6:
        print "classification type: weight 2 is good only listen to that. (Weight 2 is rare?)"
        print "Expected success: high if ML can adjust to rare features"
        for i, w in enumerate(weights):
            scores.append(w[1])

    elif classnum == 7:
        print "classification type: gradient important."
        print "Expected success: high if data preprocessing if working"
        for i, w in enumerate(weights):
            scores.append(w[-2]*100)

    elif classnum == 8:
        print "classification type: normal important."
        print "Expected success: high"
        for i, w in enumerate(weights):
            scores.append(w[-3])

    elif classnum == 9:
        print "classification type: only if getting bigger."
        print "Expected success: high if ML can respond well to negative and positive"
        for i, w in enumerate(weights):
            scores.append(0 if w[-1] < 0 else w[-1])

    elif classnum == 10:
        print "classification type: only if getting smaller."
        print "Expected success: high if ML can respond well to negative and positive"
        for i, w in enumerate(weights):
            scores.append(0 if w[-1] > 0 else (w[-1] * -1))

    elif classnum == 11:
        print "Classification type: if there is more maths now than before"
        for c in comments:
            scores.append(contentprocess(c, classnum))

    return scores

def contentprocess(c, classnum):
    if classnum == 11:
        

##extra data stuff
def preparedata(weights):
    ##standardize weights
    print "standardizing weights"
    return pr.scale(np.array(weights))

##feed into sklearn
def train(data, target, foldnum):
    ##Lasso model for sparse data
    model = linear_model.Lasso()
    ##cross_val_score to automomate splitting test data
    scores = cross_validation.cross_val_score(model, data, target, cv=foldnum)
    return sum(scores) / len(scores)

##sort out sys.argv
def flagargs(a):
    if '--load' in a and '--clip-' in a:
        print "Can't use 'load' and 'clip' arguments together right now!"
        sys.exit(-1)
    return {'load':if "--load" in a,
            'clip': a[a.index("--clip")] if "--clip" in a else None}

def main():
    flags = flagargs(sys.argv)
    print
    print "--------------------VALIDATION HAPPENING--------------------"
    print "fetching data from database"
    revisions, weights, contents, comments = fetchdatadump(flags) 
    print "done, fetched", len(revisions), "revisions"
    print
    pweights = preparedata(weights)
    for c in xrange(CLASSIFNUM):
        print "classifying"
        classifications = classify(weights, contents, comments, c)
        print "training"    
        performance = train(pweights, np.array(classifications), FOLDS)
        print "Performance over", FOLDS, "folds:", performance
        print
    
if __name__=="__main__":
    main()
    sys.exit(0)
