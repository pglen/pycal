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

import pyala, pycal, pycallog, calfile

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
        self.logwin = pycallog.LogWin()
        self.mywin.set_icon_from_file("pycal.png")

        #self.mywin.set_title("Calendar Alarm Monitor")
        self.mywin.set_title("Python Calendar")

        self.mywin.set_position(Gtk.WindowPosition.CENTER)
        mwh = min(www, hhh)
        self.mywin.set_default_size(3*www/4, 3*hhh/4)
        self.mywin.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.mywin.connect("unmap", OnExit)
        self.populate()
        self.mywin.show_all()

    def fwmonth(self, butt):
        m2 = self.cal.xdate.month + 1; y2 = self.cal.xdate.year
        if m2 > 12: y2 += 1; m2 = 12
        startd = datetime.datetime(y2, m2, 1)
        #print("startd fw", startd)
        self.cal.set_date(startd)

    def bwmonth(self, butt):
        m2 = self.cal.xdate.month - 1; y2 = self.cal.xdate.year
        if m2 < 1: y2 -= 1; m2 = 12
        startd = datetime.datetime(y2, m2, 1)
        #print("startd bw", startd)
        self.cal.set_date(startd)

    def thismonth(self, butt):
        startd = datetime.datetime.today()
        self.cal.set_date(startd)

    def bwyear(self, butt):
        m2 = self.cal.xdate.month; y2 = self.cal.xdate.year - 1
        startd = datetime.datetime(y2, m2, 1)
        self.cal.set_date(startd)

    def fwyear(self, butt):
        m2 = self.cal.xdate.month; y2 = self.cal.xdate.year + 1
        startd = datetime.datetime(y2, m2, 1)
        self.cal.set_date(startd)

    def populate(self):

        self.vbox = Gtk.VBox(); self.vbox.set_spacing(4)
        hbox = Gtk.HBox()

        hbox.pack_start(Gtk.Label("  "), 0, 0, 0)
        self.menu = pggui.MenuButt(("Open", "Close", "Dump Cal", "Show Log", "Exit"), self.menucom)
        hbox.pack_start(self.menu, 0, 0, 0)

        hbox.pack_start(Gtk.Label("    "), 1, 1, 0)
        bbb5 = Gtk.Button(" <<<  "); bbb5.connect("clicked", self.bwyear)
        hbox.pack_start(bbb5, 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        bbb2 = Gtk.Button(" <<  "); bbb2.connect("clicked", self.bwmonth)
        hbox.pack_start(bbb2, 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        bbb3 = Gtk.Button(" This Month "); bbb3.connect("clicked", self.thismonth)
        hbox.pack_start(bbb3, 0, 0, 0)
        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        bbb1 = Gtk.Button(" >>  "); bbb1.connect("clicked", self.fwmonth)
        hbox.pack_start(bbb1, 0, 0, 0)

        hbox.pack_start(Gtk.Label(" "), 0, 0, 0)
        bbb4 = Gtk.Button(" >>>  "); bbb4.connect("clicked", self.fwyear)
        hbox.pack_start(bbb4, 0, 0, 0)
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

    # --------------------------------------------------------------------
    def menucom(self, menu, item):
        #print("menu called", menu, item)

        if item == 0:
            print("Open")
        if item == 1:
            print("Save")
        if item == 2:
            #print("Cal dump",  mained.cal.xarr)
            print("SQL all\n", self.cal.sql.getall("%"))
        if item == 3:
            print("Showing log")    #,  mained.cal.get_daydat(datetime.datetime.today() ))
            self.logwin.show_log()

        if "xit" in menu:
            OnExit(self)

def     OnExit(butt, arg = None, prompt = True):

    global mained
    #mained.mywin.set_title("Exiting ...")
    #pgutils.usleep(100)
    mained.mywin.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))

    mainwin.logwin.append_logwin("Ended app: %s\r" % (datetime.datetime.today().ctime()) )
    #print("Exited")
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

    data_dir = os.path.expanduser("~/.pycal")
    try:
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)
    except:
        print("Cannot make calendar data dir.")
        sys.exit(1)

    calfname = data_dir + os.sep + "caldata.sql"
    astrofname = os.path.join(os.path.expanduser(calfile.locdir), "astrocal.ics")
    #usafname = os.path.join(os.path.expanduser(calfile.locdir), "us_en.ics")
    usafname = os.path.join(os.path.expanduser(calfile.locdir), "US_Holidays.ics")

    #print("Started pyalagui")
    mainwin = MainWindow()
    mainwin.cal.set_dbfile(calfname)
    #mainwin.cal.set_moonfile(astrofname)
    mainwin.cal.set_usafile(usafname)
    mainwin.logwin.append_logwin("Started app: %s\r" % (datetime.datetime.today().ctime()) )
    Gtk.main()
    #print("Ended pyalagui")

# EOF






