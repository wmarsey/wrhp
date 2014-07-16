import urllib
import lxml.html

code = urllib.urlopen("http://dumps.wikimedia.org/enwiki/latest/").read()
html = lxml.html.fromstring(code)
result = html.find_class("s")
total = 0.0
e = 0
for p in result[1:]:
    t = p.text_content()
    f = 0.0
    if t[-1] == "M":
        f = float(t[:-1])
        e = 1048576
    if t[-1] == "G":
        f = float(t[:-1])
        e = 1073741824
    if t[-1] == "K":
        f = float(t[:-1])
        e = 1024
    total += f * e
total /= 1073741824
print str(total) + "G, compressed"
