#!/usr/bin/env python3

#from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys

try:
    from pyvguicom import pgutils
    moddir = os.path.dirname(os.path.realpath(pgutils.__file__))
    #print("moddir", moddir)
    sys.path.append(moddir)
    #print(sys.path[-3:])
except:
    # Local
    base = os.path.dirname(os.path.realpath(__file__))
    moddir = os.path.join(base, "..", "pyvguicom")
    moddir2 = os.path.join(base, "..", "pyvguicom", "pyvguicom")
    #print("moddir", moddir)
    sys.path.append(moddir)
    sys.path.append(moddir2)
    from pyvguicom import pgutils

import  getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

try:
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify
except:
    print("No notify subsystem")

try:
    from playsound import playsound
except:
    pass
    def playsound(arg):
        print("Fake playsound")
        Gdk.beep()
        pass
    #print("No sound subsystem")

import gettext, locale
gettext.bindtextdomain('pyala', './locale/')
gettext.textdomain('pyala')
_ = gettext.gettext

sys.path.append('../pycommon')

import calfile, pycalsql

#calfname = "~/.local/share/evolution/calendar/system/calendar.ics"
calfname = "~/.pycal/caldata.sql"

def _asynsound():
    #print("Thread start")
    Gdk.beep()
    #playsound("/usr/share/sounds/freedesktop/stereo/complete.oga")
    playsound("/usr/share/sounds/freedesktop/stereo/complete.oga")
    #print("Thread end")

def play_sound():
    ttt = threading.Thread(None, _asynsound)
    ttt.start()

def _callback_func():
    pass
    print("Acknowledged")

def notify_sys(alname, alsub, ddd = ""):
    try:
        Notify.init("Calendar")
    except:
        print("Notify subsystem is not installed")
        return
    sss = " at " + ddd + "\n" + alname  + " \n" + alsub
    nnn = Notify.Notification.new("Calendar Alert", sss, "dialog-information")
    nnn.add_action("action_click", "Acknowledge Alarm", _callback_func, None)
    nnn.set_timeout(0)
    nnn.show()

def is_alarm_time(td2, aa):

    ret = False

    td3 = datetime.datetime.today()
    tdiff = td2 - td3

    if tdiff.total_seconds() < 0:
        return ret

    #print("ala time in future:", td2)
    #print("tdiff = ", tdiff, tdiff.total_seconds())

    if tdiff.total_seconds() < 100:
        ret = True

    return ret

def list_all(output, verbose = 0):

    res = []
    td3 = datetime.datetime.today()

    for aa in output:
        #print("out", aa) #print(str(aa[1]))
        idx = aa[2].find("M")
        if idx >= 0:
            mmm = int(aa[2][3:idx])
        else:
            mmm = int(aa[2])

        delta = datetime.timedelta(minutes = mmm)
        td2 = aa[1] - delta
        tdiff = td2 - td3
        if tdiff.total_seconds() >= 0:
            td4 = delta = datetime.timedelta(seconds = int(tdiff.total_seconds()))
            print (aa, "in", td4)

# ------------------------------------------------------------------------

def eval_all(output, verbose = 0):

    res = []
    for aa in output:
        if verbose:
            print("out", aa)
            print(str(aa[1]))

        idx = aa[2].find("M")
        if idx >= 0:
            mmm = int(aa[2][3:idx])
        else:
            mmm = int(aa[2])

        delta = datetime.timedelta(minutes = mmm)
        td2 = aa[1] - delta

        #print("td2 = ", td2)
        #if verbose > 0:
        #    print("Summ:", "'" + str(aa[0]) + "'", "Alrm:", str(aa[1]),
        #            "Trig:", mmm, "Action:", aa[3], "aluid", aa[4])

        if is_alarm_time(aa[1], aa):
            print("Alarm on:", aa)
            notify_sys(aa[0], aa[5])
            play_sound()
            res.append(aa)

    return res

def dblist_all(arg1, arg2):
    global pgdebug, config, sqldb

    ret = sqldb.getdata("%")

    return ret

# ------------------------------------------------------------------------

def help():

    print("pyala.py parse and intepret pycal alarm files")
    print("  Options:")
    print("      -f         show full screen")
    print("      -v         verbose")
    print("      -q         quiet")
    print("      -d [level] debug")
    print("      -x         clear config")
    print("      -c         show config")
    print("      -t         show timing")
    print("      -o         use stdout")
    print("      -g         test triggers")
    print("      -V         print Version")
    print("      -l         list pending alarms")
    print("      -h         print help")
    print("      -?         print help")

#pgdebug = 0
version = "1.0"

class Config():
    def __init__(self):
        self.test_trig = False

if __name__ == "__main__":

    global pgdebug, config, sqldb

    config = Config()

    opts = []; args = []
    longopt = ["help", ]
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h?fvxctVolgq", longopt)
    except getopt.GetoptError as err:
        print(("Invalid option(s) on command line:"), err)
        sys.exit(1)

    config.verbose = 0
    config.quiet = 0
    config.full_screen = 0
    config.list = 0
    config.debug = 0
    config.verbose = 0
    config.clear_config = 0
    config.show_config = 0
    config.show_timing = 0
    config.use_stdout = 0
    config.test_trig = 0

    for aa in opts:
        #print("aa", aa)
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
                print( sys.argv[0], _("Running at debug level"),  pgdebug)
            except:
                pgdebug = 0

        if aa[0] == "-h" or aa[0] == "--help": help();  exit(1)
        if aa[0] == "-?": help();  exit(1)
        if aa[0] == "-V": print("Version", version); exit(1)
        if aa[0] == "-f": config.full_screen = True
        if aa[0] == "-l": config.list = True
        if aa[0] == "-d": config.debug = int(aa[1])
        if aa[0] == "-v": config.verbose = True
        if aa[0] == "-q": config.quiet = True
        if aa[0] == "-x": config.clear_config = True
        if aa[0] == "-c": config.show_config = True
        if aa[0] == "-t": config.show_timing = True
        if aa[0] == "-o": config.use_stdout = True
        if aa[0] == "-g": config.test_trig = True

    if config.verbose:
        for aa in dir(config):
            if "__" not in aa:
                print(aa, "=", config.__getattribute__(aa))

    if config.test_trig:
        print("Testing pyala triggers. Verbose =", config.verbose)
        play_sound()
        notify_sys("Testing Notification", "Hello Sub")
        sys.exit(0)

    calfname2 = os.path.expanduser(calfname)

    # Pre eval calfile
    #try:
    #    res = calfile.eval_file(calfname2, config.verbose)
    #except:
    #    print("Cannot open caledar file:", "'" + calfname2 + "'")
    #    #print(sys.exc_info())
    #    sys.exit(0)

    try:
        sqldb = pycalsql.CalSQLite(calfname2)
    except:
        print("Cannot open/create calendar database.", calfname2, sys.exc_info())
        sys.exit(2)

    if not config.quiet:
        print("Started pyala ... CTRL-C to exit. Verbose =", config.verbose)
        print("Using calfname:", calfname2)

    xstat = os.stat(calfname2)
    res = []
    first = False
    while (True):
        if xstat.st_mtime != os.stat(calfname2).st_mtime or not first:
            first = True
            xstat = os.stat(calfname2)
            print("Calfile has changed, evaluating");

        else:
            #print("Calfile has not changed");
            pass

        #for aa in res:
        #    print(aa)

        if hasattr(config, "list"):
            if config.list:
                print("Listing alarms:")
                ret = dblist_all(res, 0)
                print(ret)
                break


        ala = eval_all(res)
        print("Alarm on:", ala)

        #notify_sys(aa)
        #play_sound()

        now = datetime.datetime.today()
        #print("Now: ", now)
        #time.sleep(60 - now.second)
        time.sleep(10);

# EOF
