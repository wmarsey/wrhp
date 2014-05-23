import requests
import time
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from decimal import Decimal

API_URL = 'http://en.wikipedia.org/w/api.php'
RATE_LIMIT = False
RATE_LIMIT_MIN_WAIT = None
RATE_LIMIT_LAST_CALL = None
USER_AGENT = 'wikipedia (https://github.com/goldsmith/Wikipedia/)'

#https://en.wikipedia.org/w/api.php?action=query&prop=revisions|extracts&revids=609181558

params = {
    'format': 'json',
    'action': 'query',
    'prop': 'revisions',
    'titles': 'Philosophy'
}

headers = {
    'User-Agent': USER_AGENT
}
 
i = 0

list = open("list.txt", "a")

if RATE_LIMIT and RATE_LIMIT_LAST_CALL and \
        RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT > datetime.now():
    wait_time = (RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT) - datetime.now()
    time.sleep(int(wait_time.total_seconds()))
    
r = requests.get(API_URL, params=params, headers=headers)
    
if RATE_LIMIT:
    RATE_LIMIT_LAST_CALL = datetime.now()

r = r.json()

childid =  r['query']['pages']['13692155']['revisions'][0]['revid']
parentid = r['query']['pages']['13692155']['revisions'][0]['parentid']
#extract = r['query']['pages']['13692155']['extract']

print i
#print "child, parent:" 
#print childid
#print parentid
#print extract
print

i = i + 1

while parentid is not None:
    params = {
        'format': 'json',
        'action': 'query',
        'prop': 'revisions',
        'rvprop': 'userid|user|ids|flags|tags|size|comment|contentmodel|timestamp|content'
    }

    params['revids'] = parentid

    if RATE_LIMIT and RATE_LIMIT_LAST_CALL and \
            RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT > datetime.now():
        wait_time = (RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT) - datetime.now()
        time.sleep(int(wait_time.total_seconds()))
    
    r = requests.get(API_URL, params=params, headers=headers)
    
    if RATE_LIMIT:
        RATE_LIMIT_LAST_CALL = datetime.now()

    r = r.json()

    childid =  r['query']['pages']['13692155']['revisions'][0]['revid']
    parentid = r['query']['pages']['13692155']['revisions'][0]['parentid']
    #extract = r['query']['pages']['13692155']['extract'] ##this is the current article?!

#    print type(extract)

    file = open('pages/' + str(childid) + '.txt', 'w')
    
    json.dump(r, file)

    #file.write(r.encode('UTF-8'))
    file.close()

    list.write("\n" + str(childid))

    print i
#    print "child, parent:" 
    #print childid
    #print parentid
    #print extract
    print 

    i = i + 1
