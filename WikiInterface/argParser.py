import re

class ArgParser():
    params = {'title': None,
              'revid': 0,
              'userid': 0,
              'domain':None,
              'weights':None,
              'user':None,
              'oldrevid':None,
              'pageid':None,
              'username':None,
              'revid':None,
              'scrapemin':50,
              'plotpath':None}

    flags = {'scrape': False,
             'trundle':False,
             'view':False,
             'plot':False,
             'iplot':False,
             'launch':False,
             'dbrepair':False}

    aoptions = [('--domain','domain',False),
                ('--pageid','pageid',True),
                ('--oldrevid','oldrevid',True),
                ('--revid', 'revid', True),
                ('--title','title',False),
                ('--scrapemin', 'scrapemin',True),
                ('--username', 'user',False),
                ('--plotpath', 'plotpath',False),
                ('--pageid', 'pageid', False)]
    foptions = [('s','scrape'),
                ('p', 'plot'),
                ('i', 'iplot'),
                ('v', 'launch'),
                ('r', 'dbrepair')]

    argv = None

    def __init__(self, arguments):
        self.argv = arguments

    def run(self):
        
        self._arg_valid_check()

        if not self._arg_sanity():
            return None, None

        self._flag_sanity()

        self._arg_comb_check()

        self._echo_params()

        return self.params, self.flags


    def print_help():
        with open("../README", "r") as helpfile:
            print helpfile.read()
    
    ##HANDLES COMMAND-LINE ARGUMENTS
    def _arg_valid_check(self):
        ##invalid parameters / arguments
        for i, arg in enumerate(self.argv):
            if arg[0] == '-':
                if arg[1] != '-':
                    if arg[1] not in [e[0] for e in self.foptions]:
                        raise ValueError("argument " + arg + " is invalid")
                else:
                    if arg not in [e[0] for e in self.aoptions] and arg != "--trundle":
                            raise ValueError("argument " + arg + " is invalid")
            else:
                if i > 0 and self.argv[i] != '-' and self.argv[i][1] != '-':
                    if self.argv[i-1][0] == '-' and self.argv[i-1][1] != '-':
                        raise ValueError("argument " + self.argv[i-1] + " does not take paramaters")
                    
                    for v in range(len(self.argv[:i]),-1,-1):
                        if self.argv[v][0] == '-':
                            if self.argv[v][1] != '-':
                                raise ValueError("multiple values given for " + self.argv[i-1] + ", which does not take parameters")
                            else:
                                raise ValueError("multiple values given for " + self.argv[i-1])

    def _arg_comb_check(self):
        ##invalid combinations
        p = self.params
        f = self.flags
        
        if not p['domain']:
            if p['title'] or p['user'] or\
                    p['oldrevid'] or p['pageid'] or p['revid']:
                raise ValueError("--domain argument must be specified")

        if p['user']:
            if p['revid'] or p['oldrevid']:
                raise ValueError("cannot use argument --username with --revid or --oldrevid")

        if not p['revid'] and p['oldrevid']:
            raise ValueError("must use argument --oldrevid with --revid together")

        if f['launch'] and (f['scrape'] or f['plot'] or f['iplot'] or f['dbrepair']):
            raise ValueError("launch mode must without other modes enabled")

        if f['dbrepair'] and (f['scrape'] or f['plot'] or f['iplot'] or f['launch']):
            raise ValueError("dbrepair mode must without other modes enabled")

        if (p['title'] or p['pageid'] or f['launch']) and f['trundle']:
            raise ValueError("trundle argument cannot be used in viewing mode, or with pageid or title parameters specified")

        if (p['revid'] or p['oldrevid'] or p['user']) and not f['launch']:
            raise ValueError("--revid, --oldrevid or --username params only used with -v option.")

    def _arg_sanity(self):
        a = self.argv[1:]

        if "--help" in a:
            self.print_help()
            return None
        if "--version" in a:
            print "Version:", VERSION_NUMBER
            return None
        for o in self.aoptions:
            if o[0] in a:
                try:
                    val = a[a.index(o[0]) + 1]
                except IndexError:
                    raise ValueError("no parameter set for argument " + o[0])
                if val[0] == '-':
                    raise ValueError("no parameter set for argument " + o[0])
                if o[2]:
                    val = int(val)
                self.params[o[1]] = val
        return True

    def _flag_sanity(self):
        for arg in self.argv:
            if re.search("^-[A-Za-z]$", arg):
                for ch in arg[1:]:
                    for o in self.foptions:
                        if ch == o[0]:
                            self.flags[o[1]] = True
            if arg == "--trundle":
                self.flags['trundle'] = True

    def _echo_params(self):
        print "-----------------PARAMETERS------------------"

        for k,v in self.params.iteritems():
            if v:
                print ":\t".join([k,str(v)])
        for k,v in self.flags.iteritems():
            if v:
                print k, "flag set"

    def _silencer():
        if "-S" in self.argv:
            devnull = open(os.devnull, 'w')
            sys.stdout = devnull
            self.argv.pop(self.argv.index('-S'))
        elif "-SS" in self.argv:
            devnull = open(os.devnull, 'w')
            sys.stdout, sys.stderr = devnull, devnull
            self.argv.pop(self.argv.index('-SS'))
