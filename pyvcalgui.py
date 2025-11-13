#!/usr/bin/env python3

import  os, sys, getopt, time, warnings, datetime

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

VERSION = "1.0.3"

#mydir = os.path.dirname(os.path.realpath(__file__))
#os.chdir(mydir)
#print("mydir:", mydir)
#for aa in sys.path:
#    print(aa)

from pyvcal import calutils
anchordir = os.path.dirname(os.path.realpath(calutils.__file__))
sys.path.append(anchordir)
from pyvcal import pyala, pycal, pycallog, calfile, comline

from pyvguicom import pgutils
moddir = os.path.dirname(os.path.realpath(pgutils.__file__))
sys.path.append(moddir)
from pyvguicom import pggui, pgsimp, pgbox

class flydlg(Gtk.Window):

    def __init__(self, parent):
        #GObject.GObject.__init__(self)
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)
        self.set_transient_for(parent)
        self.add(Gtk.Label.new("\n\n      Press F11 to unfullscreen     \n\n") )
        self.set_modal(True)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.show_all()

        GLib.timeout_add(2000, self.keytime)

    def keytime(self):
        self.destroy()

# ------------------------------------------------------------------------
#  Define Application Main Window claass

class MainWindow():

    def __init__(self, config):

        self.full = False
        self.fcount = 0
        self.statuscount = 0
        self.alt = False
        self.fullscreen = False
        self.got_warn = False

        pggui.register_stock_icons()
        xxx, yyy, www, hhh = pggui.screen_dims_under_cursor()

        # Create the toplevel window
        self.mywin = Gtk.Window()
        self.logwin = pycallog.LogWin(config)
        try:
            self.mywin.set_icon_from_file(config.icon)
        except:
            pass

        self.mywin.connect("key-press-event", self.keypress)
        self.mywin.set_title("Python Calendar")

        self.mywin.set_position(Gtk.WindowPosition.CENTER)
        mwh = min(www, hhh)
        self.mywin.set_default_size(3*www/4, 3*hhh/4)
        self.mywin.set_size_request(200, 200)
        self.mywin.set_events(Gdk.EventMask.ALL_EVENTS_MASK )
        self.mywin.connect("unmap", OnExit, self)
        self.populate()
        self.mywin.show_all()
        pycallog.load_log(logfname)

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
        warnings.simplefilter("ignore")
        #menu = ("Open", "Close", "Dump Cal", "Show Log", "Test alarms", "Exit")
        menu = ("Dump Cal", "Show Log", "Test alarms", "Exit")
        self.menu = pggui.MenuButt(menu, self.menucom, None)
        warnings.simplefilter("default")
        hbox.pack_start(self.menu, 0, 0, 0)

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

        #hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        #self.check3a = Gtk.CheckButton.new_with_label("Default   ");
        #self.check3a.set_active(True)
        #hbox.pack_start(self.check3a, 0, 0, 0)
        #hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        self.check3 = Gtk.CheckButton.new_with_label("Personal");
        self.check3.set_active(True)
        hbox.pack_start(self.check3, 0, 0, 0)
        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)

        hbox.pack_start(Gtk.Label.new(" "), 0, 0, 0)
        self.check4 = Gtk.CheckButton.new_with_label("Work");
        self.check4.set_active(True)
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
        self.cal = pycal.CalCanvas(config)
        self.cal.mainwin = self
        self.vbox.pack_start(self.cal, 1, 1, 0)
        #self.cal.calc_curr()
        self.mywin.add(self.vbox)

    # --------------------------------------------------------------------
    def menucom(self, paren, menu, item):

        #print("menu called", menu, "item", item)
        #if item == 0:
        #    pass
        #    print("Open")
        #if item == 1:
        #    pass
        #    #print("Save")
        #    #pycallog.save_log(logfname)
        if item == 0:
            if config.verbose:
                print("Cal dump:",  mained.cal.xarr)
            ddd = self.cal.sql.getall("%")
            print("SQL all:")
            for aa in ddd:
                print(aa)

        if item == 1:
            #print("Showing log")
            self.logwin.show_log()

        if item == 2:
            pyala.play_sound()
            ddd = datetime.datetime.today()
            dddd = str(ddd.hour) + ":" + str(ddd.minute)
            pyala.notify_sys("Test alarm notifier", "Test description appears here.", dddd)
            pggui.message("\nTesting Popup Dialog\n" + "Test dialog description would appear here.",
                                title =  "Alarm at " + dddd )
        if "xit" in menu:
            OnExit(self)

def     OnExit(butt, mainwin, prompt = True):

    mainwin.mywin.set_title("Exiting ...")
    mainwin.logwin.append_logwin("Ended app: %s\r" % (datetime.datetime.today().ctime()) )
    pycallog.save_log(logfname)
    pggui.usleep(100)

    rootwin = mainwin.mywin.get_screen().get_root_window()
    disp =  mainwin.mywin.get_display()
    cur = Gdk.Cursor.new_for_display(disp, Gdk.CursorType.ARROW)
    rootwin.set_cursor(cur)

    #print("Exited")
    Gtk.main_quit()

version = "1.0"

calfname = os.path.expanduser("~" + os.sep + ".pycal" + os.sep + "caldata.sql")
logfname = os.path.expanduser("~" + os.sep + ".pycal" + os.sep + "callog.txt")

# ------------------------------------------------------------------------

optx =  [
         ("V", "version",   "b",    bool,  False, "Show version."),
         ("v", "verbose",   "+",    int,   0, "Increase verbosity level."),
         ("d", "debug",     "=",    int,   0,   "Debug level (0-9) default=0",),
         ("f", "fname",     "=",    str,   calfname, "Calendar file name." ),
         ("l", "list",      "b",    bool,  False, "List file" ),
         ("g", "log",       "=",    int,   1, "Log level. (0-9) Defult=1" ),
         ("q", "quiet",     "b",    bool,  False, "Less output" ),
         ("c", "show",      "b",    bool,  False, "Show data" ),
         ("t", "timing",     "b",   bool,  False, "Show timing details" ),
        ]

def  mainfunc():

    global  config

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

    # Add icon files to config
    config.icon = "pyvcal/images/pycal.png"
    config.logicon = "pyvcal/images/pycal_log.png"

    if config.debug > 5:
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

    calnames = "astrocal.ics", "holidays.ics"

    #print("Started pyalagui")
    mainwin = MainWindow(config)

    mainwin.logwin.append_logwin("Started app: %s\n" % (datetime.datetime.today().ctime()) )
    mainwin.cal.set_dbfile(config.fname, config)

    mainwin.cal.set_moonfile(anchordir + os.sep + "ics" + os.sep + calnames[0])
    mainwin.cal.set_usafile(anchordir + os.sep + "ics" + os.sep + calnames[1])

    mainwin.cal.grab_focus()
    Gtk.main()
    if config.debug > 2:
        print("Ended pyalagui")
    sys.exit(0)

if __name__ == "__main__":

    mainfunc()

# EOF
