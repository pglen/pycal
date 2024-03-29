#!/usr/bin/env python

# ------------------------------------------------------------------------
# Log window. Special as it hides instead of dies.
# Intercepts stdout; printing show both in stdout and this window

#from __future__ import absolute_import
#from __future__ import print_function

import  time, datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

#from . import peddoc, pedync, pedconfig
#from .pedutil import *

# Adjust to taste. Estimated memory usage is 50 * MAX_LOG bytes
# Fills up slowly, so not a big issue. Delete ~/.pyedit/pylog.txt if
# you would like to free / limit the memory used by the log

MAX_LOG  = 2000

# Print as 'print' would, but replicate to log. This class replicate stdout
# and replicates stdout to regular fd, and puts an entry onto accum.

logwin = None

class fake_stdout():

    def __init__(self, old_stdout):

        self.old_stdout = sys.stdout
        self.flag = True
        self.dt = datetime.datetime(1990, 1, 1);

    def flush(self, *args):
        pass

    def write(self, *args):
        strx = ""
        if self.flag:
            dt2 = self.dt.now()
            strx =  dt2.strftime("%d/%m/%y %H:%M:%S ")
            self.flag = False

        for aa in args:
            if type(aa) == 'tuple':
                for bb in aa:
                    self.old_stdout.write(str(bb) + " ")
                    strx += str(bb)
            else:
                self.old_stdout.write(str(aa))
                strx +=  str(aa)

        if strx.find("\n") >= 0:
            self.flag = True

        self.limit_loglen()
        self.old_stdout.flush()

        global logwin;

        if logwin:
            logwin.append_logwin(strx)


    def limit_loglen(self):
        pass

        '''global accum
        xlen = len(accum)
        if xlen == 0: return
        if xlen  <  MAX_LOG: return
        self.old_stdout.write("limiting loglen " + str(xlen))
        for aa in range(MAX_LOG / 5):
            try:
                del (accum[0])
            except:
                pass
       '''

# Persistance for logs. Disable if you wish.

def  save_log():
    pass

def load_log():
    pass

iconfile = "pycal.png"

# A quick window to display what is in accum

class   LogWin():


    def __init__(self):
        self.win2 = Gtk.Window()

        global logwin
        logwin = self

        self.win2.set_position(Gtk.WindowPosition.CENTER)
        self.win2.set_default_size(800, 600)

        tit = "pyedpro:log"
        self.win2.set_title(tit)
        self.win2.set_events(Gdk.EventMask.ALL_EVENTS_MASK )

        self.win2.connect("key-press-event", self._area_key, self.win2)
        self.win2.connect("key-release-event", self._area_key, self.win2)
        self.win2.connect("delete-event", self._area_delete, self.win2)
        self.win2.connect("delete-event", self._area_destroy, self.win2)

        self.win2.lab = Gtk.TextView()
        self.win2.lab.set_editable(False)

        scroll = Gtk.ScrolledWindow(); scroll.add(self.win2.lab)
        frame = Gtk.Frame(); frame.add(scroll)
        self.win2.add(frame)

    def closewin(self, win):
        print("close", win)

    def show_log(self):
        try:
            win2.set_icon_from_file(iconfile)
        except:
            print("Cannot load log icon:", iconfile)

        self.win2.show_all()

    # Turn close into minimze
    def _area_delete(self, area, event, dialog):
        #print("delete", event)
        self.win2.hide()
        return True

    def _area_destroy(self, area, event, dialog):
        #print("destroy", event)
        return True

    def _area_focus(self, area, event, dialog):
        print("focus", event)

    def append_logwin(self, strx):
        tb = self.win2.lab.get_buffer()
        iter = tb.get_end_iter()
        tb.insert(iter, strx)

    # ------------------------------------------------------------------------

    def _area_key(self, area, event, dialog):

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Escape:
                #print "Esc"
                area.destroy()

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Return:
                #print "Ret"
                area.destroy()

            if event.keyval == Gdk.KEY_Alt_L or \
                    event.keyval == Gdk.KEY_Alt_R:
                area.alt = True;

            if event.keyval == Gdk.KEY_x or \
                    event.keyval == Gdk.KEY_X:
                if area.alt:
                    area.destroy()

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                area.alt = False;

def show_logwin():
    global logwin
    logwin.show_log()

def create_logwin():
    global logwin
    logwin = LogWin()

# EOF

