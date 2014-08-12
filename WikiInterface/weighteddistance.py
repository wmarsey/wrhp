import database as db 
import Queue,threading,re
import lshtein as lv

def extract(start, stop, string):
    
    return string[start:stop], string[:start]+string[stop:]

def distancecalc(queue, reg, revid, domain, string1, string2):
    queue.put(".")
    dist = lv.fastlev.plaindist(string1, string2)
    dtb = db.Database()
    dtb.updateweight(reg,dist,revid,domain)
    queue.task_done()

class WDistanceCalc:
    q = Queue.Queue()
    waiting = 0;

    reg1 = re.compile('y')
    reg2 = re.compile('h')
    math1 = re.compile('<math>.*<\/math>')
    math2 = re.compile('\{\{math.*\}\}')
    bquote = re.compile('<blockquote>.*<\/blockquote>')
    cite = re.compile('\{\{cite.*\}\}')
    citeneed = re.compile('\{\{Citation needed.*\}\}')
    afile = re.compile('\[\[File((?!\]\]).)*\]\]')
    score = re.compile('<score>.*</score>')
    linkint = re.compile('\[\[(?!File)((?!\]\]).)*\]\]')
    linkext = re.compile('\[http.*\]')
    asof = re.compile('{{As of .*}}')
    table = re.compile('\{\|((?!\|\}).)*\|\}', re.S)
    h1 = re.compile('^= .* =$')
    h2 = re.compile('^== .* ==$')
    h3 = re.compile('^=== .* ===$')
    h4 = re.compile('^==== .* ====$')
    h5 = re.compile('^===== .* =====$')
    regexdict = {'maths':(math1,math2),
                 'citations': (bquote, cite, citeneed, asof),
                 'filesimages':(afile,score),
                 'links':(linkint, linkext),
                 'structure':(h1, h2, h3, h4, h5, table, asof)}

    def processdistance(self, revid, domain, string1, string2):
        #lists of lists of regexes
        #seperated by species
        with open('regexlog.txt','w') as log:
            for key,regs in self.regexdict.iteritems():
                compare = {'m1':'',
                           'm2':''}
                for r in regs:
                    while True:
                        m = r.search(string1)
                        if not m:
                            break
                        match, string1 = extract(m.start(), m.end(), string1)
                        compare['m1'] += match
                        message = "MATCH calculating for revid " + str(revid) + " slice " + str(m.start()) + " to " + str(m.end()) + "\n"
                        message += "text: " + match + "\n"
                        message += "pattern: " + r.pattern + "\n\n"
                        log.write(message)
                    while True:
                        m = r.search(string2)
                        if not m:
                            break
                        match, string2 = extract(m.start(), m.end(), string2)
                        compare['m2'] += match
                        message = "MATCH calculating for revid " + str(revid) + " \n"
                        message += "text: " + match + "\n"
                        message += "pattern: " + r.pattern + "\n\n"
                        log.write(message)
                #send off
                if len(compare['m1']) or len(compare['m2']):
                    message = "COMPARING SLICES\n"
                    message += "SLICE 1: " + compare['m1'] + "\n"
                    message += "SLICE 2: " + compare['m2'] + "\n"
                    log.write(message)
                    self.distancethread(revid, domain, key, compare['m1'], compare['m2'])
            #send off remainder
            self.distancethread(revid, domain, 'normal', string1, string2)
            #wait for completion
            self.q.join()

    def distancethread(self, revid, domain, reg, string1, string2):
        t = threading.Thread(target=distancecalc,args=(self.q,reg,revid,domain,string1,string2))
        t.daemon = True
        t.start()
