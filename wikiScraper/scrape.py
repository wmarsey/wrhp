import requests
import time
import json
import csv
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

if RATE_LIMIT and RATE_LIMIT_LAST_CALL and \
        RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT > datetime.now():
    wait_time = (RATE_LIMIT_LAST_CALL + RATE_LIMIT_MIN_WAIT) - datetime.now()
    time.sleep(int(wait_time.total_seconds()))
    
r = requests.get(API_URL, params=params, headers=headers)
    
if RATE_LIMIT:
    RATE_LIMIT_LAST_CALL = datetime.now()

r = r.json()
childid =  r['query']['pages']['13692155']['revisions'][0]['revid']
parentid = childid

#open("index.csv", 'w').close()
#open("contents.csv", 'w').close()
index_f = open("index.csv", "ab")
contents_f = open("contents.csv", "ab")
index = csv.writer(index_f)
contents = csv.writer(contents_f)
#index.writerow(["REVISION","USER","USERID","TIMSTAMP","SIZE","COMMENT"]) 
#contents.writerow(["REVISION","CONTENT"])


while childid != 273102:
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

    #{"query": {"pages": {"13692155": {"ns": 0, "pageid": 13692155, "revisions": [{"comment": "over linking", "*": CONTENT, "tags": [], "timestamp": "2014-05-05T05:06:31Z", "contentformat": "text/x-wiki", "userid": 1988889, "revid": 607121768, "contentmodel": "wikitext", "user": "Snowded", "parentid": 607105175, "size": 118813}], "title": "Philosophy"}}}}

    childid =  r['query']['pages']['13692155']['revisions'][0]['revid']
    parentid = r['query']['pages']['13692155']['revisions'][0]['parentid']
    user = r['query']['pages']['13692155']['revisions'][0]['user']
    userid = r['query']['pages']['13692155']['revisions'][0]['userid']
    size = r['query']['pages']['13692155']['revisions'][0]['size']
    timestamp = r['query']['pages']['13692155']['revisions'][0]['timestamp']
    comment = "" #comments stop eventually
    try:
        comment = r['query']['pages']['13692155']['revisions'][0]['comment']
    except:
        comment = ""    
    content = r['query']['pages']['13692155']['revisions'][0]['*']

    index.writerow([childid, user.encode("UTF-8"), userid, timestamp, size, comment.encode("UTF-8")])
    contents.writerow([childid, content.encode("UTF-8")])

    print str(i) + " " + str(childid) + " " + str(timestamp)
    i = i + 1

print "revid is:" 
print childid

index_f.close()
contents_f.close()
