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

sys.path.append('../common')

import pggui, pgutils

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

        self.mywin.set_icon_from_file("pycal.png")

        #self.mywin.set_title("Calendar Alarm Monitor")
        self.mywin.set_title("Python Calendar")

        self.mywin.set_position(Gtk.WindowPosition.CENTER)
        mwh = min(www, hhh)
        self.mywin.set_default_size(7*mwh/8, 5*mwh/8)
        self.mywin.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.mywin.connect("unmap", OnExit)
        self.populate()
        self.mywin.show_all()

    def fwmonth(self, butt):
        try:
            startd = datetime.datetime(self.cal.xdate.year, (self.cal.xdate.month + 1), 1)
        except:
            startd = datetime.datetime(self.cal.xdate.year + 1, 1, 1)

        #print("startd", startd)
        self.cal.set_date(startd)

    def bwmonth(self, butt):
        startd = datetime.datetime(self.cal.xdate.year, (self.cal.xdate.month - 1), 1)
        #print("startd", startd)
        self.cal.set_date(startd)

    def thismonth(self, butt):
        startd = datetime.datetime.today()
        self.cal.set_date(startd)

    def populate(self):

        self.vbox = Gtk.VBox(); #self.vbox.set_spacing(4)
        hbox = Gtk.HBox()

        hbox.pack_start(Gtk.Label("  "), 0, 0, 0)
        self.menu = pggui.MenuButt(("Open", "Close", "Exit"), self.menucom)
        hbox.pack_start(self.menu, 0, 0, 0)

        hbox.pack_start(Gtk.Label("    "), 1, 1, 0)
        hbox.pack_start(Gtk.Button(" <<<  "), 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        bbb2 = Gtk.Button(" <<  "); bbb2.connect("clicked", self.bwmonth)
        hbox.pack_start(bbb2, 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        bbb3 = Gtk.Button(" Today "); bbb3.connect("clicked", self.thismonth)
        hbox.pack_start(bbb3, 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        bbb1 = Gtk.Button(" >>  "); bbb1.connect("clicked", self.fwmonth)
        hbox.pack_start(bbb1, 0, 0, 0)

        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox.pack_start(Gtk.Button(" >>>  "), 0, 0, 0)
        hbox.pack_start(Gtk.Label("    "), 1, 1, 0)
        xxx = Gtk.Button.new_with_mnemonic(" E_xit ")
        xxx.connect("clicked", OnExit, self)
        hbox.pack_start(xxx, 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)

        self.vbox.pack_start(hbox, 0, 0, 0)
        self.cal = pycal.CalCanvas()
        self.cal.mainwin = self
        self.vbox.pack_start(self.cal, 1, 1, 0)
        #self.cal.calc_curr()
        self.mywin.add(self.vbox)

    def menucom(self, menu, item):
        print("menu", menu, item)

        if item == 2:
            OnExit(self)


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

    #print("Started pyalagui")

    mainwin = MainWindow()

    Gtk.main()







