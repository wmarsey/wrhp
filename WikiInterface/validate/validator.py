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

def fetchdatadump(clip=None): 
    alldata = None
    dtb = db.Database()
    alldata = dtb.getdatadump()

    print "recieved", len(alldata), "entries"
    
    if clip:
        print "picking", clip, "random entries"
        shuffle(alldata)
        alldata = alldata[:clip]

    print "splitting" 
    revs = []
    weights = []
    contents = []
    comments = []
    for i,d in enumerate(alldata):
        rev, weight, content, comment = list(d[:2]),list(d[2:-2]),d[-2],d[-1]
        revs.append(rev)
        weights.append(weight)
        contents.append(content)
        comments.append(comment)
    print "done"
    print

    for i, w in enumerate(weights):
        for v,ww in enumerate(w):
            if ww == None:
                print ww, i, v

    # print "compressing to file"
    # timestamp= str(datetime.datetime.now()).split('.')[0].replace(' ','_')
    # extension = ".npy"
    # d = BASEPATH + '/' + timestamp
    # if not os.path.exists(d):
    #     print "creating folder", d
    #     os.makedirs(d)
    
    # rfile = BASEPATH + '/' + timestamp + "/data_revs" + extension
    # wfile = BASEPATH + '/' + timestamp + "/data_weights" + extension
    # confile = BASEPATH + '/' + timestamp + "/data_contents" + extension
    # comfile = BASEPATH + '/' + timestamp + "/data_comments" + extension
    # with open(rfile, 'wb') as d:
    #     pickle.dump(revs,d,protocol=pickle.HIGHEST_PROTOCOL)
    # print "wrote to", rfile
    # with open(wfile, 'wb') as d:
    #     pickle.dump(weights,d,protocol=pickle.HIGHEST_PROTOCOL)
    # print "wrote to", wfile
    # with open(confile, 'wb') as d:
    #     pickle.dump(contents,d,protocol=pickle.HIGHEST_PROTOCOL)
    # print "wrote to", confile
    # with open(comfile, 'wb') as d:
    #     pickle.dump(comments,d,protocol=pickle.HIGHEST_PROTOCOL)
    # print "wrote to", comfile
        
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
            # if count > largest:
            #     largest = count
        # for i,s in enumerate(scores):
        #     scores[i] = s / largest
        #     if not (i % 10000):
        #         sys.stdout.write('.')
        #         sys.stdout.flush()
        # sys.stdout.write('\n')
        # sys.stdout.flush()

    elif classnum == 2:
        largest = 0
        print "Classification type: sum of weights, times gradient"
        for i,w in enumerate(weights):
            tsum = sum(w[:-1])
            gradient = w[-1]
            num = tsum * gradient
            #if tsum < 0:
            #    print w[:-1]
            #if gradient < 0:
            #    print gradient
            # if num > largest:
            #     largest = num
            scores.append(num)
            #if not (i % 1000):
             #   sys.stdout.write('.')
              #  sys.stdout.flush()
        #sys.stdout.write('\n')
        #sys.stdout.flush()
        # for i,s in enumerate(scores):
        #     scores[i] = s / largest
        #     if not (i % 10000):
        #         sys.stdout.write('.')
        #         sys.stdout.flush()
        # sys.stdout.write('\n')
        # sys.stdout.flush()

        
    elif classnum == 3:
        largest = 0
        print "Classification type: smaller changes better than bigger ones"
        for i,w in enumerate(weights):
            tsum = sum(w[:-3])
            gradient = w[-2]
            num = tsum * gradient
            #if tsum < 0:
            #    print w[:-1]
            #if gradient < 0:
            #    print gradient
            if num > largest:
                largest = num
            scores.append(num)
        # for i,s in enumerate(scores):
        #     scores[i] = 1 - (s / largest)
        #     if not (i % 10000):
        #         sys.stdout.write('.')
        #         sys.stdout.flush()
        # sys.stdout.write('\n')
        # sys.stdout.flush()

    elif classnum == 4:
        print "classification type: non-normal is good."
        for i, w in enumerate(weights):
            scores.append(sum(w[:-3]))

    elif classnum == 5:
        print "classification type: maths is good."
        for i, w in enumerate(weights):
            scores.append(w[0])

    elif classnum == 6:
        print "classification type: weight 2 is good only listen to that. (Weight 2 is rare?)"
        for i, w in enumerate(weights):
            scores.append(w[1])
            #sys.stdout.write(str(w[1])+'.')
            #sys.stdout.flush()

    elif classnum == 7:
        print "classification type: gradient super important."
        for i, w in enumerate(weights):
            scores.append(w[-2]*100)

    elif classnum == 8:
        print "classification type: normal important."
        for i, w in enumerate(weights):
            scores.append(w[-3])

    elif classnum == 9:
        print "classification type: only if getting bigger."
        for i, w in enumerate(weights):
            scores.append(0 if w[-1] < 0 else w[-1])

    elif classnum == 10:
        print "classification type: only if getting smaller."
        for i, w in enumerate(weights):
            scores.append(0 if w[-1] > 0 else (w[-1] * -1))

    return scores

def preparedata(weights):
    ##standardize weights
    print "standardizing weights"
    weights = pr.scale(np.array(weights))

    return weights

##feed into sklearn
def train(data, target, foldnum):
    
    clf = linear_model.Lasso()
    scores = cross_validation.cross_val_score(clf, data, target, cv=foldnum)
    return sum(scores) / len(scores)

def main():
    print
    print "--------------------VALIDATION HAPPENING--------------------"
    print "fetching data from database"
    revisions, weights, contents, comments = fetchdatadump() 
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
