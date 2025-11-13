#!/usr/bin/env python3

''' Parse the command line.

    The options are determined types:
        int, str, bool
    The options have operators:
        int increment               "+"
        int assign                  "="
        str assign                  "="
        bool set / reset / reverse  "b"
    The options have defaults:
        The default must be the correct type
    The results are retured in the "Config" class.
    If the config.parseerror is non empty, an error cooured, and
    the error description is in the parseerror string.
    The config.argx arguments are filled in with arguments.
    (else it is empty)

    Parser is parsing according to GNU conventions, args and
    options can be mixed.
'''

def parse(argv, optx):

    config = Config() ;
    config.progname = argv[0]
    opts = ""; lopts = []

    optx.append(("h", "help",      "b",    bool,  False, "Help (this screen)"),)
    optx.append(("?", "help",      "b",    bool,  False, "Help (alias to -h)"),)

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
    import getopt
    try:
        opts, config.xargs = getopt.gnu_getopt(argv[1:], opts, lopts)
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

    if config.help:
        help(argv[0], optx)

    return config;

def strxpad(strx, lenx = 12):
    #print("strxpad", strx, lenx)
    if len(strx) >= lenx:
        return strx
    else:
        return strx + " " * (lenx - len(strx))

prologue = "program to do something."
epilogue = "The program closing statements."

def help(pname, optx):
    import os
    print(os.path.basename(pname), prologue)
    for aa in optx:
        comp = "      " + strxpad("-" + aa[0], 5) + strxpad("--" + aa[1])
        if aa[2] == "=":
            comp += strxpad(aa[1] + "_val")
        else:
            comp += strxpad(" ")
        print(comp, aa[5])
    print(epilogue)

class Config():
    ''' Hold the return data '''
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

def printobj(conf):

    ''' For testing '''
    for aa in dir(conf):
            if "__" not in aa:
                print(" conf:", aa, "=", conf.__getattribute__(aa)) #, end = "\t")

if __name__ == "__main__":

    # Option name, -- long/var name -- action -- type name -- default
    optx =  [
     ("d", "debug",     "=",    int,   0,   "Debug level (0-9) default=0", ),
     ("f", "fname",     "=",    str,   "untitled", "File Name for out data. Test."),
     ("a", "arr",       "=",    str,   "",  "Array test for comline",),
     ("t", "trace",     "=",    str,   "None", "Trace flag string.",),
     ("v", "verbose",   "+",    int,   0,   "Increase verbosity level.",),
     ("V", "version",   "b",    bool,  False,   "Show version.",),
     ("b", "back",      "b",    bool,  False, "Back one flag, test.",),
     ]
    import sys
    config = parse(sys.argv, optx)
    if config.parseerror:
        print(config.parseerror)
        sys.exit(1)

    if config.help:
        sys.exit(0)

    if config.version:
        print("Version 1.0", end = " ")
        if config.verbose:
            print("built on Sat 08.Nov.2025", end = " ")
        print()
        sys.exit(0)

    if config.verbose:
        print("dump options:")
        printobj(config)

# EOF
