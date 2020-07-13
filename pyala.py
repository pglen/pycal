#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

gi.require_version('Notify', '0.7')
from gi.repository import Notify

from playsound import playsound

_calfile = "~/.local/share/evolution/calendar/system/calendar.ics"
calfile = os.path.expanduser(_calfile)

output = []

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

def notify_sys(aa):
    Notify.init("Calendar")
    nnn = Notify.Notification.new("Calendar Alert", "Alarm: " + aa[0]  + " - " + aa[5],  "dialog-information")
    nnn.add_action("action_click", "Acknowledge Alarm", _callback_func, None)
    #nnn.set_urgency(0)
    nnn.show()
    nnn.uninit()

def parsedatetime(strx):
    #print("Parser", strx,
    #    "%s %s %s   -- " % (strx[0:4], strx[4:6], strx[6:8]),
    #    "%s %s %s" % (strx[9:11], strx[11:13], strx[13:15]))
    try:

        dt = datetime.datetime(int(strx[0:4]), int(strx[4:6]), int(strx[6:8]),
                                int(strx[9:11]), int(strx[11:13]), int(strx[13:15]) )
    except:
        print("bad date:", strx)

    #print(dt)
    return dt

def parsedate(strx):
    #print("Parser", strx,
    #    "%s %s %s   -- " % (strx[0:4], strx[4:6], strx[6:8])
    try:

        dt = datetime.datetime(int(strx[0:4]), int(strx[4:6]), int(strx[6:8]))
    except:
        print("bad date:", strx)

    #print(dt)
    return dt

def eval_file():

    #global summ, startdt, trig, audio, aluid, desc, output

    summ = None
    startdt = None
    trig = None
    audio = None
    aluid = None
    desc = None

    fp = open(calfile, "rt")

    start = False
    start2 = False
    wastzname = False

    line2 = ""
    while True:
        if line2 == "":
            line = fp.readline()
            if not line:
                break
            line = line.strip("\r\n")
        else:
            line = line2

        # Slurp next
        line2 = fp.readline()
        if not line2:
            break

        line2 = line2.strip("\r\n")
        if line2[0] == " ":
            #print("slurp:", line2)
            line += " " + line2
            line2 = ""

        #print("  ----- line", line, end = "\n")
        comp = line.split()
        #print("  --- data", comp, end = "\n")

        if "TZNAME:" in comp[0]:
            if not wastzname:
                #print (line)
                wastzname = True

        if "END:VEVENT" in comp[0]:
            start = False

        if start:
            #if "CREATED:" in comp[0]:
            #    print (line)

            if "SUMMARY:" in comp[0]:
                #print (line )
                summ = line.split(":")[1]

            if "DESCRIPTION:" in comp[0]:
                #print (line )
                desc = line.split(":")[1]

            if "DTSTART;TZID" in comp[0]:
                #print (line )
                startdt = parsedatetime(comp[1])
                #print (comp )

            if "DTSTART;VALUE" in comp[0]:
                #print (line )
                startdt = parsedate(line.split(":")[1])
                #print (comp )

            if "END:VALARM" in comp[0]:
                start2 = False
                #print("Summ:", summ, "Alarm:", startdt, "Trig:", trig, "Action:", audio)
                output.append((summ, startdt, trig, audio, aluid, desc))

            if start2:
                #print("   Valarm", comp[0])
                if "TRIGGER;" in comp[0]:
                    trig = comp[0].split(":")[1]
                    #print("Trigger", trig)
                if "ACTION" in comp[0]:
                    audio = comp[0].split(":")[1]
                if  "ALARM-UID" in comp[0]:
                    aluid = comp[0].split(":")[1]

            if "BEGIN:VALARM" in comp[0]:
                start2 = True

        if "BEGIN:VEVENT" in comp[0]:
            start = True
    fp.close()

def is_time(td2, aa):

    td3 = datetime.datetime.today()
    tdiff = td2 - td3
    if tdiff.total_seconds() < 0:
        return

    #print("tdiff = ", tdiff, tdiff.total_seconds())
    if tdiff.total_seconds() < 100:
        print("Alarm on:", aa)
        notify_sys(aa)
        play_sound()

def eval_all():

    for aa in output:
        idx = aa[2].find("M")
        mmm = int(aa[2][3:idx])
        #print("Summ:", "'" + aa[0] + "'", "Alrm:", aa[1], "Trig:", mmm, "Action:", aa[3]) #, "aluid", aa[4])

        delta = datetime.timedelta(minutes = mmm)
        td2 = aa[1] - delta
        #print("td2 = ", td2)

        is_time(td2, aa)

# ------------------------------------------------------------------------

def help():

    print("pyala.py parse and intepret pycal alarm files")
    print("  Options:")
    print("      -f     show full screen")
    print("      -v     verbose")
    print("      -x     clear config")
    print("      -c     show config")
    print("      -t     show timing")
    print("      -o     use stdout")
    print("      -V     print Version")
    print("      -h     print help")
    print("      -?     print help")

pgdebug = 0
version = "1.0"

class Config():
    pass

if __name__ == "__main__":

    #global pgdebug
    global config

    config = Config()
    opts = []; args = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:h?fvxctVo")
    except getopt.GetoptError as err:
        print(_("Invalid option(s) on command line:"), err)
        sys.exit(1)

    for aa in opts:
        if aa[0] == "-d":
            try:
                pgdebug = int(aa[1])
                print( sys.argv[0], _("Running at debug level"),  pgdebug)
            except:
                pgdebug = 0

        if aa[0] == "-h": help();  exit(1)
        if aa[0] == "-?": help();  exit(1)
        if aa[0] == "-V": print("Version", version); \
            exit(1)
        if aa[0] == "-f": config.full_screen = True
        if aa[0] == "-v": config.verbose = True
        if aa[0] == "-x": config.clear_config = True
        if aa[0] == "-c": config.show_config = True
        if aa[0] == "-t": config.show_timing = True
        if aa[0] == "-o": config.use_stdout = True

    print("Started pyala ... CTRL-C to exit")

    try:
        eval_file()
    except:
        print("Cannot open / read caledar file.")
        raise

    xstat = os.stat(calfile);

    while (True):

        if xstat.st_mtime != os.stat(calfile).st_mtime:
            eval_file()
            xstat = os.stat(calfile)
        else:
            #print("Calfile not changed");
            pass

        eval_all()
        now = datetime.datetime.today()
        #print("Now: ", now)
        time.sleep(60 - now.second)

# EOF
