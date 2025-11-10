#!/usr/bin/env python

# ------------------------------------------------------------------------
# Get script file

import  os, sys, time, datetime

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

class CalFsel():

    def __init__(self, self2, butt, event):

        self.fname = ""
        #print("browse for script called", butt, event)
        # Traditional choose file
        but =   "Cancel (E_xit)", Gtk.ButtonsType.CANCEL,\
                        "Select Script", Gtk.ButtonsType.OK
        self.fc = Gtk.FileChooserDialog(title="Select Script",
                    transient_for=self2,
                        action=Gtk.FileChooserAction.OPEN)
        self.fc.add_buttons(*but)
        self.fc.set_default_response(Gtk.ButtonsType.OK)
        self.fc.set_current_folder(os.getcwd())
        self.fc.connect("response", self.done_open_fc)
        self.fc.connect("key-press-event", self._area_key)
        self.fc.connect("key-release-event", self._area_key)
        self.fc.run()

    def done_open_fc(self, win, resp):
        #print ("done_open_fc", win, resp)
        if resp == Gtk.ButtonsType.OK:
            #print("calfsel OK")
            fname = win.get_filename()
            if not fname:
                #print "Must have filename"
                #self.update_statusbar("No filename specified")
                pass
            elif os.path.isdir(fname):
                #self.update_statusbar("Changed to %s" % fname)
                #os.chdir(fname)
                #win.set_current_folder(fname)
                return
            else:
                #print("got filename", fname)
                #self.script.set_text(fname)
                #self.scrcheck.set_active(True)
                self.fname = fname
                win.destroy()
        if resp == Gtk.ButtonsType.CANCEL or resp == Gtk.ButtonsType.YES_NO:
            #print("calfsel Cancel")
            self.fname = ""
            pass
        self.fc.destroy()

    def _area_key(self, area, event):

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Escape:
                #print "Esc"
                area.destroy()

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Return:
                #print "Ret"
                pass

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

# EOF
