import numpy as np
import sys, os, inspect
from sklearn import preprocessing as pr
from sklearn import svm, cross_validation
import datetime
import cPickle as pickle
from random import choice

here = inspect.getfile(inspect.currentframe()) # script filename (usually with path)
BASEPATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

sys.path.append("../")
import database as db

CLASSIFNUM = 2
FOLDS = 50

# ##import all from database
# def fetchdata():
#     log = ""
#     dtb = db.Database()
    
#     ##fetch revs, returns ((revid, domain),...,)
#     revs = dtb.getallrevs()
#     message = "revs:" + str(len(revs))
#     print message
#     print
#     log += message + '\n'
    
#     ##fetch contents
#     message = "fetching contents"
#     print message
#     log += message + '\n'
#     contents = ()
#     corruptcont = []
#     for i,r in enumerate(revs):
#         if not (i % 50):
#             sys.stdout.write(str(i)+'.')
#             sys.stdout.flush()
#         content = dtb.getrevcontent(r[0], r[1])
#         if content:
#             contents += (content,)
#         else:
#             corruptcont.append(i)
    
#     message = "contents: " + str(len(contents))
#     print '\n' + message
#     log += message + '\n'
#     message = "corrupt: " + str(len(corruptcont))
#     print message
#     log += message + '\n'
#     for c in reversed(corruptcont):
#         del revs[c]
#     message = "revs after deletion: " + str(len(revs))
#     print message
#     log += message + '\n'
    
#     ##fetch weights
#     weights = ()
#     for r in revs:
#         weight = dtb.getweight(r[0], r[1])
#         if weight:
#             weights += (weight,)
#         else:
#             message = "error fetching weights", r[0], r[1]
#             print message
#             log += message + '\n'
    
#     ##check revids    
#     for i, r in enumerate(revs):
#         if r[0] != weights[i][0] or r[1] not in weights[i][1]:
#             message = "error, data mismatch, iteration" + str(i) + '\n'
#             print "error, data mismatch, iteration", i
#             print type(r[0]), r[0], "not", type(weights[i][0]), weights[i][0], weights[i][0], "or", type(r[1]), len(r[1]), r[1], "not", type(weights[i][1]), len(weights[i][1]), weights[i][1]
#             sys.exit(-1)

#     ##strip revid, domain and completeness from weights
#     weights = tuple(tuple(w[2:-1]) for w in weights)

#     for i, w in enumerate(weights):
#         for v, ww in enumerate(w):
#             if not isinstance(ww, int) and not isinstance(ww, long) and not isinstance(ww, float):
#                 message = "error in feature" + str(v) + "of sample" + str(i)
#                 print message
#                 log += message + '\n'
#                 print ww, "is not an int or a long it is", type(ww)
#                 sys.exit(-1)

#     ##check lengths
#     if len(revs) != len(weights) \
#             or len(revs) != len(contents) \
#             or len(contents) != len(weights):
#         print "error, data mismatch", len(revs), len(contents), len(weights)
#         sys.exit(-1)

#     timestamp= str(datetime.datetime.now()).split('.')[0].replace(' ','_')
#     extension = ".npy"

#     d = BASEPATH + '/' + timestamp
#     print "inspecting folder", d
#     if not os.path.exists(d):
#         print "creating folder", d
#         os.makedirs(d)

#     with open(BASEPATH + '/' + timestamp + "/data_log" + extension, 'wb') as d:
#         d.write(log)

#     with open(BASEPATH + '/' + timestamp + "/data_weights" + extension, 'wb') as d:
#         np.save(d, weights)

#     with open(BASEPATH + '/' + timestamp + "/data_revs" + extension, 'wb') as d:
#         np.save(d, revs)

#     with open(BASEPATH + '/' + timestamp + "/data_contents" + extension, 'wb') as d:
#         np.save(d, contents)

#     return revs, weights, contents


def fetchdatadump(): 
    alldata = None
    dtb = db.Database()
    alldata = dtb.getdatadump()

    print "recieved", len(alldata), "entries"
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

    print "compressing to file"
    timestamp= str(datetime.datetime.now()).split('.')[0].replace(' ','_')
    extension = ".npy"
    d = BASEPATH + '/' + timestamp
    if not os.path.exists(d):
        print "creating folder", d
        os.makedirs(d)
    
    rfile = BASEPATH + '/' + timestamp + "/data_revs" + extension
    wfile = BASEPATH + '/' + timestamp + "/data_weights" + extension
    confile = BASEPATH + '/' + timestamp + "/data_contents" + extension
    comfile = BASEPATH + '/' + timestamp + "/data_comments" + extension
    with open(rfile, 'wb') as d:
        pickle.dump(revs,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", rfile
    with open(wfile, 'wb') as d:
        pickle.dump(weights,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", wfile
    with open(confile, 'wb') as d:
        pickle.dump(contents,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", confile
    with open(comfile, 'wb') as d:
        pickle.dump(comments,d,protocol=pickle.HIGHEST_PROTOCOL)
    print "wrote to", comfile
        
    return revs, weights, contents, comments

##classify
####choose a rule for classification
def classify(weights, contents, comments, classnum):
    ##for example, 
    scores = []
    if classnum == 0:
        print "Classification type: classification good is gradient >= 0.7"
        print "Expected success: 100% (the gradient is one of the supplied weights)"
        for i, w in enumerate(weights):
            if w[-1] < 0.7:
                scores.append(0)
            else:
                scores.append(1)
            if not (i % 1000):
                sys.stdout.write('.')
                sys.stdout.flush()
        sys.stdout.write('\n')
        sys.stdout.flush()
    elif classnum == 1:
        print "Classification type: classify as good if randomly-picked vowel appears in comments"
        print "Expected success: about 50% (NB there bias towards latin alphabet in dataset"
        vowel = choice(['a','e','i','o','u'])
        print "(Chosen vowel:", vowel, ")"
        for i,c in enumerate(comments):
            if vowel in c:
                scores.append(1)
            else:
                scores.append(0)
            if not (i % 1000):
                sys.stdout.write('.')
                sys.stdout.flush()
        sys.stdout.write('\n')
        sys.stdout.flush()

    return scores

def preparedata(weights, targets):

    targets = np.array(targets)

    ##standardize weights
    print "standardizing weights"
    weights = pr.scale(np.array(weights))

    return weights, targets

##feed into sklearn
def train(data, target, foldnum):
    clf = svm.SVC(kernel = "linear", verbose = False, C = 1)
    scores = cross_validation.cross_val_score(clf, data, target, cv=foldnum)
    return sum(scores) / len(scores)

def main():
    print
    print "--------------------VALIDATION HAPPENING--------------------"
    print "fetching data from database"
    revisions, weights, contents, comments = fetchdatadump() 
    print "done, fetched", len(revisions), "revisions"
    print
    for c in xrange(CLASSIFNUM):
        print "classifying"
        classifications = classify(weights, contents, comments, c)
        print "done"
        print 
        print "preparing data"
        pweights, pclassifications = preparedata(weights, classifications)
        print "done"
        print

        print "training"    
        performance = train(pweights, pclassifications, FOLDS)
        print "Performance over", FOLDS, "folds:", performance
    
if __name__=="__main__":
    main()
    sys.exit(0)
