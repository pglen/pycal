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

import pyala, pycal

# ------------------------------------------------------------------------
#  Define Application Main Window claass

class MainWindow():

    def __init__(self):

        self.full = False
        self.fcount = 0
        self.statuscount = 0
        self.alt = False
        #register_stock_icons()

        global mained
        mained = self

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print disp
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        # Resort to old means of getting screen w / h
        if www == 0 or hhh == 0:
            www = Gdk.screen_width(); hhh = Gdk.screen_height();

        # Create the toplevel window
        self.mywin = Gtk.Window()

        #self.mywin.set_title("Calendar Alarm Monitor")
        self.mywin.set_title("Python Calendar")

        self.mywin.set_position(Gtk.WindowPosition.CENTER)
        mwh = min(www, hhh)
        self.mywin.set_default_size(7*mwh/8, 5*mwh/8)
        self.mywin.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.mywin.connect("unmap", OnExit)
        self.populate()
        self.mywin.show_all()

    def populate(self):
        self.vbox = Gtk.VBox()

        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label("    "), 1, 1, 0)
        hbox.pack_start(Gtk.Button(" <<<  "), 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox.pack_start(Gtk.Button(" <<  "), 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox.pack_start(Gtk.Button(" Today "), 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox.pack_start(Gtk.Button(" >>  "), 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox.pack_start(Gtk.Button(" >>>  "), 0, 0, 0)
        hbox.pack_start(Gtk.Label("    "), 1, 1, 0)
        xxx = Gtk.Button.new_with_mnemonic(" E_xit ")
        xxx.connect("clicked", OnExit, self)
        hbox.pack_start(xxx, 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)

        self.vbox.pack_start(hbox, 0, 0, 0)
        self.cal = pycal.CalCanvas()
        self.vbox.pack_start(self.cal, 1, 1, 0)

        self.mywin.add(self.vbox)


def     OnExit(butt, arg = None, prompt = True):

    #butt.mywin.set_title("Exiting ...")
    Gtk.main_quit()

# ------------------------------------------------------------------------

def help():

    print("Helping")

pgdebug = 0
version = "1.0"

if __name__ == "__main__":

    #global pgdebug

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
        if aa[0] == "-f": full_screen = True
        if aa[0] == "-v": verbose = True
        if aa[0] == "-x": clear_config = True
        if aa[0] == "-c": show_config = True
        if aa[0] == "-t": show_timing = True
        if aa[0] == "-o": use_stdout = True

    print("Started pyalagui")

    mainwin = MainWindow()

    Gtk.main()


