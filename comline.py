#!/usr/bin/env python3

import getopt

def printobj(conf):
    for aa in dir(conf):
            if "__" not in aa:
                print(" conf:", aa, "=", conf.__getattribute__(aa)) #, end = "\t")
class Config():
    def __init__(self):
        self.parseerror = ""
        pass

def assn(config, aa, bb):

    if bb[2] == "+":
        #print("increment", bb[1])
        val = getattr(config, bb[1], 0)
        setattr(config, bb[1], val + 1)
    elif bb[2] == "b":
        #print("bool", aa, "--", bb)
        setattr(config, bb[1], not bb[4])
    elif bb[2] == "=":
        #print("assign", aa, "--", bb, ";;;", bb[3] )
        if bb[3] == type(0):
            try:
                val = int(aa[1])
            except:
                config.parseerror = "Must be an integer arg for '%s'" % aa[0]
                #return
        else:
            val = aa[1]
        setattr(config, bb[1], val)

def parse(argv, optx):

    config = Config() ;
    config.progname = argv[0]
    opts = ""; lopts = []

    # Set defaults
    for aaa in optx:
        #print("defx:", "aaa", aaa, aaa[3], type(aaa[4]))
        if aaa[3] != type(aaa[4]):
            config.parseerror = "Invalid init type at option: '-%s'" % aaa[0]
            #return
        if aaa[1]:
            nnn = aaa[1]
        else:
            nnn = aaa[0]
        setattr(config, nnn, aaa[4])

    # Option name, -- long/var name -- action -- type -- default
    for aa in optx:
        opts += aa[0]
        if aa[2] == "=":
            opts += ":"
        if aa[1]:
            lll = aa[1]
            if aa[2] == "=":
                lll += "="
            lopts.append(lll)

    #print("opts:", opts, "lopts:", lopts)
    xargs = []
    try:
        opts, xargs = getopt.gnu_getopt(argv[1:], opts, lopts)
    except getopt.GetoptError as err:
        config.parseerror = "Invalid option(s) on command line: %s" % err

    for aa in opts:
        #print("aa", aa)
        for bb in optx:
            #print("  bb", bb)
            if aa[0] == "-" + bb[0]:
                #print("short match", aa, bb)
                assn(config, aa, bb)
            if aa[0] == "--" + bb[1]:
                #print("long match", aa, bb)
                assn(config, aa, bb)

    config.xargs = xargs
    return config;

if __name__ == "__main__":

    # Option name, -- long/var name -- action -- type name -- default
    optx =  [
                 ("v", "verbose",   "+",    int,   0, ),
                 ("d", "debug",     "=",    int,   0, ),
                 ("f", "fname",     "=",    str,   "untitled", ),
                 ("a", "arr",       "=",    str,   "", ),
                 ("b", "back",      "b",    bool,  False, ),
                 ("h", "help",      "b",    bool,  False, ),
            ]

    import sys
    config = parse(sys.argv, optx)
    if config.parseerror:
        print(config.parseerror)
        sys.exit(1)

    if config.help:
        print("Help")
        sys.exit(1)

    print("dump output:")
    printobj(config)

# EOF
