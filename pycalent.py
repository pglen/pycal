#!/usr/bin/env python3

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform, random
import ctypes, datetime, sqlite3, warnings, math, pickle
from calendar import monthrange

import pycalent

sys.path.append('../common')
import pggui, pgutils, pgsimp, pgbox

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import cairo

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

check_fill = ("Notify", "Sound", "Popup", "Beep",  "Email")

def spinner(startx, endx, default = 1):

    adj2 = Gtk.Adjustment(startx, 1.0, endx, 1.0, 5.0, 0.0)
    spin2 = Gtk.SpinButton.new(adj2, 0, 0)
    spin2.set_value(default)
    spin2.set_wrap(True)
    return spin2

# ------------------------------------------------------------------------

class CalEntry(Gtk.Window):

    def __init__(self, hx, hy, self2, callb = None):

        #print("CalEntry init", hx, hy)

        Gtk.Window.__init__(self)
        self.callb = callb
        self.set_accept_focus(True);
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.alt = False
        self.uuid = pgutils.randstr(12)

        self.set_position(Gtk.WindowPosition.CENTER)

        xxxx, yyyy = self2.get_pointer()
        (nnn, ttt, pad, xx, yy) = self2.darr[hx][hy]

        # This was the font height on draw ...
        hhh2 = self2.rect.height / 60; hhh2 = min(hhh2, 12) + 6

        xdarr = self2.get_daydat(ttt)
        xdarrs = sorted(xdarr, key=lambda val: val[3][3] * 60 + val[3][4] )

        #print("xdarr", xdarr)
        #for sss in xdarr:
        #    if  sss[3][3] == ttt.hour and sss[3][4] == ttt.minute:
        #        print("found me", sss[3][3], sss[3][4])
        #try:
        #    idx = min(idx, len(xdarrs)-1)
        #    print("current",  xdarrs[idx])
        #except:
        #    pass

        idx = int(((yyyy - (hhh2 + 4)) - yy) // hhh2)
        print("len", len(xdarrs), "idx", idx)

        self.set_title("Calendar Item Entry")

        self.connect("button-press-event", self.area_button)
        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)

        vbox = Gtk.VBox();
        self.ptab = Gtk.Table(); self.ptab.set_homogeneous(False)
        self.ptab.set_col_spacings(4); self.ptab.set_row_spacings(4)

        ds = spinner(0, 31, ttt.day)
        mms = spinner(1, 12, ttt.month)
        ys = spinner(1995, 2100, ttt.year)

        row = 0; col = 0
        ds.set_sensitive(False); mms.set_sensitive(False); ys.set_sensitive(False);

        self.ptab.attach_defaults(pggui.Label("  "), col, col+1, row, row + 1); col += 1

        self.ptab.attach_defaults(pggui.Label(" D_ay: ", ds), col, col+1,  row, row + 1)  ; col += 1
        self.ptab.attach_defaults(ds, col, col+1,  row, row + 1)            ; col += 1

        self.ptab.attach_defaults(pggui.Label(" Mon_th: ", mms), col, col+1,  row, row + 1)     ; col += 1
        self.ptab.attach_defaults(mms,  col, col+1,  row, row + 1)              ; col += 1

        self.ptab.attach_defaults(pggui.Label(" Y_ear: ", ys),  col, col+1,  row, row + 1)     ; col += 1
        self.ptab.attach_defaults(ys,  col, col+1,  row, row + 1)              ; col += 1
        self.ptab.attach(pggui.Label("  "), col, col+1, row, row + 1,
                            Gtk.AttachOptions.EXPAND , Gtk.AttachOptions.EXPAND , 4, 4); col += 1

        nowh = ttt.hour; nowm = ttt.minute
        if ttt.hour == 0 and ttt.minute == 0:
            tnow = datetime.datetime.today()
            nowh = tnow.hour; nowm = tnow.minute

        hs = spinner(0, 23, nowh);  ms = spinner(0, 59, nowm);  dds = spinner(0, 1000, 60-nowm)

        row += 1; col = 0
        self.ptab.attach_defaults(pggui.Label("  "), col, col+1, row, row + 1); col += 1

        self.ptab.attach_defaults(pggui.Label(" Hour: ", hs), col, col+1,  row, row + 1)  ; col += 1
        self.ptab.attach_defaults(hs, col, col+1,  row, row + 1)            ; col += 1

        self.ptab.attach_defaults(pggui.Label(" Minute: ", ms), col, col+1,  row, row + 1)     ; col += 1
        self.ptab.attach_defaults(ms,  col, col+1,  row, row + 1)              ; col += 1

        self.ptab.attach_defaults(pggui.Label(" Duration: (min) ", ms), col, col+1,  row, row + 1)     ; col += 1
        self.ptab.attach_defaults(dds,  col, col+1,  row, row + 1)              ; col += 1

        self.ptab.attach(pggui.Label("  "), col, col+1, row, row + 1,
                            Gtk.AttachOptions.EXPAND , Gtk.AttachOptions.EXPAND , 4, 4); col += 1

        row += 1; col = 0

        self.nowarr = ((ds, mms, ys, hs, ms, dds))

        # ----------------------------------------------------------------

        self.dtab = Gtk.Table(); self.dtab.set_homogeneous(False)
        self.dtab.set_col_spacings(4); self.dtab.set_row_spacings(4)

        self.alarr = []
        for aa in range(3):
            row += 1; col = 0
            cb = Gtk.CheckButton()
            hs = spinner(0, 23); ms = spinner(0, 59)

            self.dtab.attach(pggui.Label("  "), col, col+1, row, row + 1,
                            Gtk.AttachOptions.FILL, Gtk.AttachOptions.FILL, 1, 1); col += 1

            self.dtab.attach_defaults(pggui.Label(" Alarm _%d:  Enabled: " % (aa+1), cb, "Enable / Disable"), col, col+1, row, row + 1); col += 1
            self.dtab.attach_defaults(cb, col, col+1, row, row + 1); col += 1

            self.dtab.attach_defaults(pggui.Label(" _Hour: "), col, col+1,  row, row + 1)  ; col += 1
            self.dtab.attach_defaults(hs, col, col+1,  row, row + 1)            ; col += 1

            self.dtab.attach_defaults(pggui.Label(" Minute: "), col, col+1,  row, row + 1)     ; col += 1
            self.dtab.attach_defaults(ms,  col, col+1,  row, row + 1)              ; col += 1

            hbox = Gtk.HBox(); cccarr = []
            for aa in check_fill:
                ccc = Gtk.CheckButton(aa)
                cccarr.append(ccc)
                hbox.pack_start(ccc, 0, 0, 0)

            self.dtab.attach_defaults(hbox,  col+3, col+6,  row, row + 1)              ; col += 6
            self.alarr.append([cb, hs, ms,  cccarr])

            #row += 1  ; col = 0
        self.dtab.attach_defaults(pggui.Label("  "), col, col+1, row, row + 1); col += 1

        # ----------------------------------------------------------------
        #sss = ttt.strftime("%m-%d-%y")
        sss = ttt.strftime("%a %d-%b-%Y")

        hbox = Gtk.HBox(); lab = pggui.Label(sss, font = "Sans 16")
        lab.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse("#222222"))

        hbox.pack_start(pggui.Label(" "), 0, 0, 4)
        hbox.pack_start(lab, 1, 1, 4)
        hbox.pack_start(pggui.Label(" "), 0, 0, 4)

        arrt = ((" _Subject: ", "aa"), (" _Description: ", "hello"), (" _Notes: ", "notes"))
        self.table = pggui.TextTable(arrt, textwidth=85)

        self.edit = pgsimp.SimpleEdit()
        self.edit.set_size_request(200, 200)

        if len(xdarrs) > idx:
            self.table.texts[0].set_text(xdarrs[idx][1][0])
            self.table.texts[1].set_text(xdarrs[idx][1][1])
            self.table.texts[2].set_text(xdarrs[idx][1][2])
            self.edit.set_text(xdarrs[idx][1][3])

        # ----------------------------------------------------------------
        # Assemble all of it

        vbox.pack_start(hbox, 0, 0, 2)
        vbox.pack_start(pggui.xSpacer(), 0, 0, 0)

        hbox3 = Gtk.HBox()
        hbox3.pack_start(pggui.Label(" "), 0, 0, 0)
        hbox3.pack_start(self.table, 0, 0, 4)
        hbox3.pack_start(pggui.Label(" "), 0, 0, 0)

        hbox4 = Gtk.HBox()
        hbox4.pack_start(pggui.Label(" "), 0, 0, 0)
        hbox4.pack_start(self.edit, 1, 1, 4)
        hbox4.pack_start(pggui.Label(" "), 0, 0, 0)

        vbox.pack_start(self.ptab, 0, 0, 4)
        #vbox.pack_start(pggui.xSpacer(), 0, 0, 0)

        vbox.pack_start(self.dtab, 0, 0, 4)
        vbox.pack_start(pggui.xSpacer(), 0, 0, 0)
        vbox.pack_start(hbox3, 0, 0, 4)

        hbox7 = Gtk.HBox()
        hbox7.pack_start(pggui.Label(" "), 0, 0, 4)
        hbox7.pack_start(pggui.Label("_Free form text:", self.edit), 0, 0, 4)
        hbox7.pack_start(pggui.Label(" "), 1, 1, 4)
        vbox.pack_start(hbox7, 0, 0, 4)

        vbox.pack_start(hbox4, 0, 0, 4)

        hbox6 = Gtk.HBox()
        bbb1 = pggui.WideButt("_Cancel", self.cancel)
        bbb2 = pggui.WideButt(" OK (E_xit)  ", self.ok)
        hbox6.pack_start(pggui.Label(" "), 1, 1, 0)
        hbox6.pack_start(bbb1, 0, 0, 2);   hbox6.pack_start(bbb2, 0, 0, 2)

        vbox.pack_start(hbox6, 0, 0, 4)

        self.add(vbox)

        self.show_all()
        self.set_modal(True)
        self.set_keep_above(True)

    def area_key(self, area, event):

        #print("Keyval: ", event.keyval)

        if  event.type == Gdk.EventType.KEY_PRESS:
            if event.keyval == Gdk.KEY_Alt_L or \
                    event.keyval == Gdk.KEY_Alt_R:
                self.alt = True;

        if event.keyval == Gdk.KEY_Tab:
            #print ("pedwin TREE TAB", event.keyval)
            pass

        if event.keyval == Gdk.KEY_Escape:
            #print (" ESC ", event.keyval)
            self.cancel(None)

        if event.keyval >= Gdk.KEY_1 and event.keyval <= Gdk.KEY_9:
            #print ("pedwin Alt num", event.keyval - Gdk.KEY_1)
            pass

        elif  event.type == Gdk.EventType.KEY_RELEASE:
            if event.keyval == Gdk.KEY_Alt_L or \
                  event.keyval == Gdk.KEY_Alt_R:
                self.alt = False;

    def ok(self, buff):
        if self.callb:
            self.callb("OK", self)
        self.destroy()
        pass

    def cancel(self, buff):
        if self.callb:
            self.callb("CANCEL", self)
        self.destroy()
        pass

    def area_button(self, butt, arg):
        #print("Button press in CalEntry")
        pass



