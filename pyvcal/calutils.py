#!/usr/bin/env python3

import warnings

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import cairo

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

def flatten(var):
    strx = ""
    try:
        for aa in var:
            strx += aa
    except:
        pass
    strx = strx.replace("\\n", "\n")
    strx = strx.replace("\\", "\n")
    return strx

def isiterable(p_object):

    try:
        it = iter(p_object)
    except TypeError:
        return False
    return True

def printit(varx, sp = " "):

    print("printit")

    if type(varx) == str:
        print(sp, "'" + varx + "'", end = " ")
    elif type(varx) == int:
        print(sp, "(int)", varx, end = " ")
    elif type(varx) == float:
        print(sp, "(float)", varx, end = " ")
    elif isiterable(varx):
        for aa in varx:
            printit(aa, sp + "  ")
        print()
    else:
        print(sp, varx, end = " ")

def get_rule_str(mmm, rr):

    out = ""
    mstr = "BYMONTH=" + mmm
    if mstr in rr:
        idx =  rr.find("BYDAY=")
        if idx != -1:
            idx += 6
            #print("byday", rr[idx:])
            idx2 =  rr[idx:].find(";")
            if  idx2 == -1:
                idx2 =  rr[idx:].find(";")
            if  idx2 != -1:
                out = rr[idx:idx+idx2]

    #print("get_rule_str()", mmm, rr, "out=", out)
    return out

class CalPopup(Gtk.Window):

    def __init__(self, strx):
        Gtk.Window.__init__(self)
        self.set_accept_focus(False); self.set_decorated(False)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.connect("button-press-event", self.area_button)

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#cfcfcf"))

        vbox = Gtk.VBox(); hbox = Gtk.HBox()
        lab = pggui.Label(strx)
        lab.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse("#222222"))
        hbox.pack_start(lab, 0, 0, 4)

        vbox.pack_start(hbox, 0, 0, 4)
        self.add(vbox)

    def area_button(self, butt, arg):
        #print("Button press in tooltip")
        pass

class MsgDlg(Gtk.Window):

    def __init__(self, title, message, subject):

        warnings.simplefilter("ignore")
        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)
        warnings.simplefilter("default")

        try:
            self.set_icon_from_file("images/pycal_ala.png")
        except:
            #print("load icon", sys.exc_info())
            pass

        #self.set_transient_for(parent)
        self.set_title(title)

        msg = Gtk.Label.new(message)
        warnings.simplefilter("ignore")
        msg.override_font(Pango.FontDescription.from_string("Arial 16"))
        warnings.simplefilter("default")

        subj = Gtk.Label.new(subject)

        self.vbox = Gtk.VBox()

        self.vbox.pack_start(Gtk.Label.new(""), 1, 1, 0)

        hbox2 = Gtk.HBox()
        hbox2.pack_start(Gtk.Label.new(""), 1, 1, 8)
        hbox2.pack_start(msg, 0, 0, 8)
        hbox2.pack_start(Gtk.Label.new(""), 1, 1, 8)
        self.vbox.pack_start(hbox2, 0, 0, 8)

        hbox = Gtk.HBox()
        hbox.pack_start(Gtk.Label.new(""), 1, 1, 8)
        hbox.pack_start(subj, 0, 0, 8)
        hbox.pack_start(Gtk.Label.new(""), 1, 1, 8)
        self.vbox.pack_start(hbox, 0, 0, 8)

        self.vbox.pack_start(Gtk.Label.new(""), 1, 1, 0)
        self.add(self.vbox)
        self.set_default_size(300, 200)
        #self.set_decorated(False)
        #self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.connect("key-press-event", self.keypress)
        self.show_all()

    def keypress(self, win, key):
        #print("key", key.keyval)
        if key.keyval == Gdk.KEY_Escape:
            self.destroy()

# EOF
