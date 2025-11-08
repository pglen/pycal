#!/usr/bin/env python3

#from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

#try:
#    gi.require_version('Notify', '0.7')
#    from gi.repository import Notify
#except:
#    print("No notify subsystem")

mydir = os.path.dirname(os.path.realpath(__file__))
#print("mydir", mydir)
os.chdir(mydir)

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

from pyvguicom import pggui, pgutils, pgsimp, pgbox
import pyala, pycal, pycallog, calfile

class flydlg(Gtk.Window):

    def __init__(self, parent):
        #GObject.GObject.__init__(self)
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)
        self.set_transient_for(parent)
        self.add(Gtk.Label.new("\n\n      Press F11 to unfullscreen     \n\n") )
        self.set_modal(True)
        self.set_decorated(False)
        self.show_all()
        GLib.timeout_add(1200, self.keytime)

    def keytime(self):
        self.destroy()

# ------------------------------------------------------------------------
#  Define Application Main Window claass

class MainWindow():

    def __init__(self):

        self.full = False
        self.fcount = 0
        self.statuscount = 0
        self.alt = False
        self.fullscreen = False
        self.got_warn = False

        pggui.register_stock_icons()

        global mained
        mained = self
        xxx, yyy, www, hhh = pggui.screen_dims_under_cursor()
        # Create the toplevel window
        self.mywin = Gtk.Window()
        self.logwin = pycallog.LogWin()
        self.mywin.set_icon_from_file("pycal.png")
        #self.mywin.set_hide_titlebar_when_maximized(True)

        self.mywin.connect("key-press-event", self.keypress)

        #self.mywin.set_title("Calendar Alarm Monitor")
        self.mywin.set_title("Python Calendar")

        self.mywin.set_position(Gtk.WindowPosition.CENTER)
        mwh = min(www, hhh)
        self.mywin.set_default_size(3*www/4, 3*hhh/4)
        self.mywin.set_size_request(200, 200)
        self.mywin.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.mywin.connect("unmap", OnExit)
        self.populate()
        self.mywin.show_all()

    def fwmonth(self, butt):
        m2 = self.cal.xdate.month + 1; y2 = self.cal.xdate.year
        if m2 > 12: y2 += 1; m2 = 1
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

    def weekview(self, butt):
        pass

    def bwyear(self, butt):
        m2 = self.cal.xdate.month; y2 = self.cal.xdate.year - 1
        startd = datetime.datetime(y2, m2, 1)
        self.cal.set_date(startd)

    def fwyear(self, butt):
        m2 = self.cal.xdate.month; y2 = self.cal.xdate.year + 1
        startd = datetime.datetime(y2, m2, 1)
        self.cal.set_date(startd)

    def moon_toggle(self, butt):
        self.cal.moon = butt.get_active()
        self.cal.invalidate()

    def holy_toggle(self, butt):
        self.cal.holy = butt.get_active()
        self.cal.invalidate()

    def def_toggle(self, butt):
        self.cal.defc = butt.get_active()
        self.cal.invalidate()

    def keypress(self, win, event):

        #print ("key", event.string, "val", event.keyval, "state", event.state)
        #print("hw", event.hardware_keycode)

        '''
        if  event.state & Gdk.ModifierType.SHIFT_MASK:
            print("SHIFT")
        if  event.state & Gdk.ModifierType.CONTROL_MASK:
            print("CONTROL")
        if  event.state & Gdk.ModifierType.MOD1_MASK:
            print("ALT")
        '''
        if event.keyval == Gdk.KEY_F11:
            if  self.fullscreen:
                self.mywin.unfullscreen()
            else:
                self.mywin.fullscreen()
                if not self.got_warn:
                    flydlg(self.mywin)
                    self.got_warn = True
            self.fullscreen = not self.fullscreen
        return False

    def populate(self):

        self.vbox = Gtk.VBox(); self.vbox.set_spacing(4)

        hbox = Gtk.HBox()

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        menu = ("Open", "Close", "Dump Cal", "Show Log", "Test alarms", "Exit")
        self.menu = pggui.MenuButt(menu, self.menucom, None)
        #hbox.pack_start(self.menu, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        self.check = Gtk.CheckButton.new_with_label("Moon"); self.check.set_active(True)
        self.check.connect("toggled", self.moon_toggle)
        hbox.pack_start(self.check, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        self.check2 = Gtk.CheckButton.new_with_label("Holiday"); self.check2.set_active(True)
        self.check2.connect("toggled", self.holy_toggle)
        hbox.pack_start(self.check2, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 1, 1, 0)
        bbb6 = Gtk.Button.new_with_label(" Day "); bbb6.connect("clicked", self.weekview)
        hbox.pack_start(bbb6, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        bbb7 = Gtk.Button.new_with_label(" Week "); bbb7.connect("clicked", self.weekview)
        hbox.pack_start(bbb7, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 1, 1, 0)
        bbb5 = Gtk.Button.new_with_label(" <<<  "); bbb5.connect("clicked", self.bwyear)
        hbox.pack_start(bbb5, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        bbb2 = Gtk.Button.new_with_label(" <<  "); bbb2.connect("clicked", self.bwmonth)
        hbox.pack_start(bbb2, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        bbb3 = Gtk.Button.new_with_label(" This Month "); bbb3.connect("clicked", self.thismonth)
        hbox.pack_start(bbb3, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        bbb1 = Gtk.Button.new_with_label(" >>  "); bbb1.connect("clicked", self.fwmonth)
        hbox.pack_start(bbb1, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        bbb4 = Gtk.Button.new_with_label(" >>>  "); bbb4.connect("clicked", self.fwyear)
        hbox.pack_start(bbb4, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 1, 1, 0)
        bbb8 = Gtk.Button.new_with_label(" Month "); bbb6.connect("clicked", self.weekview)
        hbox.pack_start(bbb8, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        bbb9 = Gtk.Button.new_with_label(" Year "); bbb7.connect("clicked", self.weekview)
        hbox.pack_start(bbb9, 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 1, 1, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        self.check3a = Gtk.CheckButton.new_with_label("Default   "); self.check3a.set_active(True)
        hbox.pack_start(self.check3a, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        self.check3 = Gtk.CheckButton.new_with_label("Personal"); self.check3.set_active(True)
        hbox.pack_start(self.check3, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        self.check4 = Gtk.CheckButton.new_with_label("Work  "); self.check4.set_active(True)
        hbox.pack_start(self.check4, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        xxx = Gtk.Button.new_with_mnemonic(" E_xit ")
        xxx.connect("clicked", OnExit, self)
        hbox.pack_start(xxx, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        #self.vbox.pack_start(Gtk.Label("s"), 0, 0, 0)
        self.vbox.pack_start(pggui.xSpacer(2), 0, 0, 0)

        self.vbox.pack_start(hbox, 0, 0, 0)
        self.cal = pycal.CalCanvas()
        self.cal.mainwin = self
        self.vbox.pack_start(self.cal, 1, 1, 0)
        #self.cal.calc_curr()
        self.mywin.add(self.vbox)

    # --------------------------------------------------------------------
    def menucom(self, paren, menu, item):

        #print("menu called", menu, "item", item)
        if item == 0:
            print("Open")
        if item == 1:
            print("Save")
        if item == 2:
            if config.verbose:
                print("Cal dump:",  mained.cal.xarr)
            ddd = self.cal.sql.getall("%")
            print("SQL all:")
            for aa in ddd:
                print(aa)

        if item == 3:
            print("Showing log")    #,  mained.cal.get_daydat(datetime.datetime.today() ))
            self.logwin.show_log()
        if item == 4:
            pyala.play_sound()
            ddd = datetime.datetime.today()
            dddd = str(ddd.hour) + ":" + str(ddd.minute)
            pyala.notify_sys("Test alarm notifyer", "Test description appears here.", dddd)
            pgutils.message("\nTesting Popup Dialog\n" + "Test dialog description would appear here.",
                                title =  "Alarm at " + dddd )
        if "xit" in menu:
            OnExit(self)

def     OnExit(butt, arg = None, prompt = True):

    global mained
    #mained.mywin.set_title("Exiting ...")
    #pgutils.usleep(100)

    rootwin = mained.mywin.get_screen().get_root_window()
    disp =  mained.mywin.get_display()
    cur = Gdk.Cursor.new_for_display(disp, Gdk.CursorType.ARROW)
    rootwin.set_cursor(cur)

    mainwin.logwin.append_logwin("Ended app: %s\r" % (datetime.datetime.today().ctime()) )
    #print("Exited")
    Gtk.main_quit()

pgdebug = 0
version = "1.0"

calfname = os.path.expanduser("~" + os.sep + ".pycal" + os.sep + "caldata.sql")

# ------------------------------------------------------------------------

optx =  [
         ("V", "version",   "b",    bool,  False, "Show version."),
         ("v", "verbose",   "+",    int,   0, "Increase verbosity level."),
         ("d", "debug",     "=",    int,   0,   "Debug level (0-9) default=0",),
         ("f", "fname",     "=",    str,   calfname, "Calendar file name." ),
         ("l", "list",      "b",    bool,  False, "List file" ),
         ("q", "quiet",     "b",    bool,  False, "Less output" ),
         ("c", "show",      "b",    bool,  False, "Show data" ),
         ("t", "timing",     "b",   bool,  False, "Show timing details" ),
        ]

if __name__ == "__main__":

    global config

    import comline
    comline.prologue = "GUI for pycal."
    comline.epilogue = "Mandatory option arguments are for both short and long form."
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
    ddir = os.path.dirname(config.fname)
    try:
        if not os.path.isdir(ddir):
            os.mkdir(ddir)
    except:
        print("Cannot make calendar data dir.", data_dir)
        sys.exit(1)

    if config.verbose:
        print("Using calfname:", config.fname)

    astrofname = os.path.join(os.path.expanduser(calfile.locdir), "astrocal.ics")
    usafname = os.path.join(os.path.expanduser(calfile.locdir), "us_en.ics")
    #usafname = os.path.join(os.path.expanduser(calfile.locdir), "US_Holidays.ics")

    #print("Started pyalagui")
    mainwin = MainWindow()
    mainwin.cal.set_dbfile(config.fname, config)
    mainwin.cal.set_moonfile(astrofname)
    mainwin.cal.set_usafile(usafname)
    mainwin.logwin.append_logwin("Started app: %s\r" % (datetime.datetime.today().ctime()) )

    mainwin.cal.grab_focus()
    Gtk.main()
    #print("Ended pyalagui")

# EOF
