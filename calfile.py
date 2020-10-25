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

#gi.require_version('Notify', '0.7')
#from gi.repository import Notify

#from playsound import playsound

caldir = "~/.local/share/evolution/calendar/system/"
locdir = "~/.pycal/"

# ------------------------------------------------------------------------
# This is a hacked version of the calendar file format parser.
# Gets an array that contains most of the parsed data we are interested in

def eval_file(calfile, verbose = 0):

    output = []

    #if verbose > 0:
    #    print("Processing calfile", calfile)

    summ = None ;   startdt = None;     trig = None;    audio = None;
    aluid = None;   desc = None;        rrule = None

    try:
        fp = open(calfile, "rt")
    except:
        print("Cannot open calfile", calfile)
        return  output

    start = False ;     start2 = False;     wastzname = False
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

        if verbose > 4:
            print("----- line", line, end = "\n")
        comp = line.split(":")
        if verbose > 3:
            print("  --- data", comp, end = "\n")

        if "TZNAME" in comp[0]:
            if not wastzname:
                if verbose > 2:
                    print (line)
                wastzname = True

        if "END" in comp[0] and "VEVENT" in comp[1]:
            start = False

            if verbose > 0:
                print("Summ:", summ, "Alarm:", startdt, "Trig:", trig,
                        "Action:", audio, "Alarmuid:", aluid, "Description:", desc)

            output.append((summ, startdt, trig, audio, aluid, desc, rrule))

            summ = None ;    startdt = None;    trig = None
            audio = None;    aluid = None;      desc = None
            rrule = None

        if start:

            #if "CREATED:" in comp[0]:
            #    print (line)

            try:
                if "SUMMARY" in comp[0]:
                    if verbose > 2:
                        print ("Summary", line )
                    summ = comp[1]

                if "DESCRIPTION" in comp[0]:
                    if verbose > 2:
                        print ("desc", comp[1] )
                    desc = comp[1]

                if "RRULE" in comp[0]:
                    if verbose > 2:
                        print ("rrule", "summ", summ, comp[1])
                    rrule = comp[1:]

                if "DTSTART;TZID" in comp[0]:
                    if verbose > 2:
                        print ("dstart tz", line, comp )
                    startdt = parsedatetime(comp[1])
                    #print (comp )

                elif "DTSTART;VALUE" in comp[0]:
                    if verbose > 2:
                        print ("dstart val", line )
                    startdt = parsedate(comp[1])
                    #print (comp )

                elif "DTSTART" in comp[0]:
                    #print ("dstart", line )
                    startdt = parsedate(comp[1])
                    #print (comp )

            except:
                print("Cannot parse line:", line)
                print("Cannot parse arr:", comp)
                print(sys.exc_info())

            if "END"  in comp[0] and "VALARM" in comp[1]:
                start2 = False

            if start2:
                #print("   Valarm", comp[0])
                if "TRIGGER;" in comp[0]:
                    trig = comp[1]
                    #print("Trigger", trig)
                if "ACTION" in comp[0]:
                    audio = comp[1:]
                if  "ALARM-UID" in comp[1]:
                    aluid = comp[1]

            if "BEGIN" in comp[0] and "VALARM" in comp[1]:
                start2 = True

        if "BEGIN" in comp[0] and "VEVENT" in comp[1]:
            start = True

    fp.close()
    return output


def is_time(td2, aa):

    td3 = datetime.datetime.today()
    tdiff = td2 - td3
    if tdiff.total_seconds() < 0:
        return

    #print("tdiff = ", tdiff, tdiff.total_seconds())
    if tdiff.total_seconds() < 100:
        print("Alarm on:", aa)
        #notify_sys(aa)
        #play_sound()


#           0123 45 67 8 90 12 34
# Formats:  2020 04 30 T 18 45 00

def parsedatetime(strx):

    strx = strx.strip()

    #print("Parser", strx,
    #    "'%s' '%s' '%s'   -- " % (strx[0:4], strx[4:6], strx[6:8]),
    #        "'%s' '%s' '%s'" % (strx[9:11], strx[11:13], strx[13:15]))

    try:
        dt = datetime.datetime(int(strx[0:4]), int(strx[4:6]), int(strx[6:8]),
                                int(strx[9:11]), int(strx[11:13]), int(strx[13:15]) )
    except:
        print(sys.exc_info())
        print("Bad date/time2:", "'" + strx + "'")

    #print(dt)
    return dt

def parsedate(strx):

    #print("Parser", strx,
    #    "%s %s %s   -- " % (strx[0:4], strx[4:6], strx[6:8]))

    strx = strx.strip()

    try:

        dt = datetime.datetime(int(strx[0:4]), int(strx[4:6]), int(strx[6:8]))
    except:
        print("Bad date:", strx)

    #print(dt)
    return dt

# ------------------------------------------------------------------------

if __name__ == "__main__":

    #calfile = os.path.join(os.path.expanduser(caldir), "calendar.ics")
    calfile = os.path.join(os.path.expanduser(locdir), "astrocal.ics")

    try:
        arr = eval_file(calfile)
        #print("arr", arr)
        for bb in arr:
            #summ, startdt, trig, audio, aluid, desc
            print("Summ:", bb[0], "Start:", bb[1], "Trig:", bb[2], "aluid:", bb[3], "\ndesc", bb[4])
            pass

    except:
        print("Cannot open / read parse caledar file.")
        print(sys.exc_info())
        raise

    #xstat = os.stat(calfile);





