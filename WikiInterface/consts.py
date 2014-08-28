import sys, os
VERSION_NUMBER = "0.0.0.0.00.0.000.1"
BASEPATH = os.path.dirname(os.path.realpath(__file__)) #"/homes/wm613/individual-project/WikiInterface/"
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
    if reset:
        dotcount = 1
    if not (dotcount%50) and dotcount:
        sys.stdout.write('|')
    else:
        sys.stdout.write(dot)
    if final or (not (dotcount%50) and dotcount):
        sys.stdout.write('\n')
    dotcount = dotcount + 1
    sys.stdout.flush()
