#!/usr/bin/env python3

#from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys

from pyvguicom import pgutils
moddir = os.path.dirname(os.path.realpath(pgutils.__file__))
sys.path.append(moddir)

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

#sys.path.append('../pycommon')

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

# EOF
