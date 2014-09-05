from sys import stdout
from os import path
VERSION_NUMBER = "0.0.0.0.00.0.000.1"
BASEPATH = path.dirname(path.realpath(__file__)) #"/homes/wm613/individual-project/WikiInterface/"
WEIGHTLABELS = ["maths",
                "headings",
                "quotes", 
                "files/images",
                "links",
                "citations",
                "normal"]

dotcount = 1
def dot(reset=False, final=False, slash=False):
    dot = '.'
    
    if slash:
        dot = '-'
    
    global dotcount
    
    if not (dotcount%50) and dotcount:
        stdout.write('|')
    else:
        stdout.write(dot)
    
    if final or (not (dotcount%50) and dotcount):
        stdout.write('\n')
    
    if final:
        dotcount = 1
    else:
        dotcount = dotcount + 1
    
    stdout.flush()
