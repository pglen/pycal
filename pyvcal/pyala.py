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

def list_all(output):

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

def eval_all(output):

    global  config

    res = []
    for aa in output:
        if config.verbose:
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

def dblist_all():
    global config, sqldb
    ret = sqldb.getdata("%", True)
    return ret

version = "1.0"

optx =  [
                 ("V", "version",   "b",    bool,  False, "Show version."),
                 ("v", "verbose",   "+",    int,   0, "Increase verbosity level."),
                 ("d", "debug",     "=",    int,   0,   "Debug level (0-9) default=0",),
                 ("f", "fname",     "=",    str,   calfname, "Calendar file name." ),
                 ("l", "list",      "b",    bool,  False, "List file" ),
                 ("q", "quiet",     "b",    bool,  False, "Less output" ),
                 ("c", "show",      "b",    bool,  False, "Show data" ),
                 ("t", "timing",     "b",   bool,  False, "Show timing details" ),
                 ("g", "trig",       "b",   bool,  False, "Test triggers" ),
                 ("i", "interval",   "=",   int,   10,    "Time interval between scans" ),
            ]

if __name__ == "__main__":

    global config, sqldb

    import comline
    comline.prologue = "Alarm engine for pycalgui."
    comline.epilogue = ""
    config = comline.parse(sys.argv, optx)

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

    if config.debug > 1:
        for aa in dir(config):
            if "__" not in aa:
                print(" config:", aa, "=", config.__getattribute__(aa))

    if config.trig:
        if config.verbose:
            print("Testing pyala triggers. Verbose =", config.verbose)
        play_sound()
        notify_sys("Testing Notification", "Hello Sub")
        sys.exit(0)

    calfname2 = os.path.expanduser(config.fname)

    # Pre eval calfile
    #try:
    #    res = calfile.eval_file(config.fname2, config.verbose)
    #except:
    #    print("Cannot open caledar file:", "'" + calfname2 + "'")
    #    #print(sys.exc_info())
    #    sys.exit(0)

    try:
        sqldb = pycalsql.CalSQLite(calfname2, config)
    except:
        print("Cannot open/create calendar database.", calfname2, sys.exc_info())
        sys.exit(2)

    if not config.quiet:
        print("Started pyala ... CTRL-C to exit")

    if config.verbose:
        print("Using calfname:", calfname2)

    if config.list:
        print("Listing alarms:")
        ret = dblist_all()
        print(ret)
        sys.exit(0)

    # Start scanning
    xstat = os.stat(calfname2)
    res = []
    first = False
    while (True):
        if xstat.st_mtime != os.stat(calfname2).st_mtime or not first:
            first = True
            xstat = os.stat(calfname2)
            if config.verbose:
                print("Calfile has changed, evaluating");
            ala = eval_all(res)
            if config.verbose:
                print("Alarm on:", ala)
            #notify_sys(aa)
            #play_sound()

        if config.verbose > 2:
            now = datetime.datetime.today()
            print("Now: ", now)
        #time.sleep(60 - now.second)
        time.sleep(config.interval);

# EOF
