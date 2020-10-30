#!/usr/bin/env python3

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform, random, warnings
import ctypes, datetime, sqlite3, warnings, math, pickle, uuid
from calendar import monthrange

import pycalent

sys.path.append('../pycommon')
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

# ------------------------------------------------------------------------

class CalEntry(Gtk.Window):

    def __init__(self, xxxx, yyyy, self2, callb = None):

        #print("CalEntry init", hx, hy)

        warnings.simplefilter("ignore")

        Gtk.Window.__init__(self)
        self.callb = callb
        self.set_accept_focus(True);
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.alt = False
        self.alarr = []

        hx, hy = self2.hit_test(xxxx, yyyy)

        #self.uuid = pgutils.randstr(12)
        self.uuid = uuid.uuid4()
        self.self2 = self2

        self.self2.mainwin.logwin.append_logwin(
                            "Popup: %s\r" % (datetime.datetime.today().ctime()) )

        self.set_position(Gtk.WindowPosition.CENTER)

        #xxxx, yyyy = self2.get_pointer()
        (nnn, ttt, pad, xx, yy) = self2.darr[hx][hy]

        # This was the font height on draw ...
        hhh2 = self2.rect.height / 60; hhh2 = min(hhh2, 12) + 6

        xdarr = self2.get_daydat(ttt)
        xdarrs = sorted(xdarr, key=lambda val: val[1][3] * 60 + val[1][4] )

        idx = int(((yyyy - (hhh2 + 4)) - yy) // hhh2) + self2.scrollday

        print("len", len(xdarrs), "idx", idx, "ign", self2.scrollday)

        title = "Calendar Item Entry"
        if idx >= len(xdarrs):
            title += " (New) "
            xdat = []
        else:
            xdat = xdarrs[idx]
            title += " %02d:%02d " % (xdat[1][3], xdat[1][4])

        self.set_title(title)

        #print ("xdat loading", xdat)

        self.connect("button-press-event", self.area_button)
        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)

        self.row = 0; self.col = 0
        vbox = Gtk.VBox();

        # ----------------------------------------------------------------

        hbox5 = self.make_scriptline()

        self.row = 0; self.col = 0
        hbox, self.dtab = self.make_dtab(ttt, xdarrs, idx, xdat)

        self.row = 0; self.col = 0
        self.ptab = self.make_ptab(ttt, xdarrs, idx)

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

        vbox.pack_start(hbox5, 0, 0, 4)

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

    # --------------------------------------------------------------------

    def make_dtab(self, ttt, xdarrs, idx, xdat):

        dtab = Gtk.Table(); #dtab.set_homogeneous(False)
        dtab.set_col_spacings(4); dtab.set_row_spacings(4)

        for aa in range(3):
            self.row += 1; self.col = 0
            cb2 = Gtk.CheckButton()
            if xdat:
                cb2.set_active(xdat[3][aa][0])
            hs2 = pggui.Spinner(0, 23, 0);
            if xdat:
                hs2.set_value(xdat[3][aa][1])
            ms2 = pggui.Spinner(0, 59, 0);
            if xdat:
                ms2.set_value(xdat[3][aa][2])

            #if aa == 0:
            #    if xdarrs[idx][1] == 0 and xdarrs[idx][2] == 0:
            #        hs2.set_value(nowh)
            #        ms2.set_value(nowm)

            dtab.attach(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1,
                            Gtk.AttachOptions.FILL, Gtk.AttachOptions.FILL, 1, 1); self.col += 1

            dtab.attach_defaults(pggui.Label(" Alarm _%d:  Enabled: " % (aa+1), cb2, "Enable / Disable"), self.col, self.col+1, self.row, self.row + 1); self.col += 1
            dtab.attach_defaults(cb2, self.col, self.col+1, self.row, self.row + 1); self.col += 1

            dtab.attach_defaults(pggui.Label(" _Hour: "), self.col, self.col+1,  self.row, self.row + 1)  ; self.col += 1
            dtab.attach_defaults(hs2, self.col, self.col+1,  self.row, self.row + 1)            ; self.col += 1

            dtab.attach_defaults(pggui.Label(" Minute: "), self.col, self.col+1,  self.row, self.row + 1)     ; self.col += 1
            dtab.attach_defaults(ms2,  self.col, self.col+1,  self.row, self.row + 1)              ; self.col += 1

            hbox = Gtk.HBox();
            cccarr = []
            for bb in range(len(check_fill)):
                ccc = Gtk.CheckButton(check_fill[bb])

                if xdat:
                      ccc.set_active(xdat[3][aa][3][bb])

                cccarr.append(ccc)
                hbox.pack_start(ccc, 0, 0, 0)

            dtab.attach_defaults(hbox,  self.col+3, self.col+6,  self.row, self.row + 1)              ; self.col += 6
            self.alarr.append([cb2, hs2, ms2, cccarr])

            #self.row += 1  ; self.col = 0
        dtab.attach_defaults(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1); self.col += 1

        # ----------------------------------------------------------------
        #sss = ttt.strftime("%m-%d-%y")
        tnow = datetime.datetime.today()
        nowh = tnow.hour; nowm = tnow.minute
        sss = "%s %02d:%02d" % (ttt.strftime("%a %d-%b-%Y"), nowh, nowm )

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
            self.table.texts[0].set_text(xdarrs[idx][2][0])
            self.table.texts[1].set_text(xdarrs[idx][2][1])
            self.table.texts[2].set_text(xdarrs[idx][2][2])
            self.edit.set_text(xdarrs[idx][2][3])

        return hbox, dtab

    # --------------------------------------------------------------------

    def make_ptab(self, ttt, xdarrs, idx):

        ptab = Gtk.Table(); #self.ptab.set_column_homogeneous(False)
        ptab.set_col_spacings(4); ptab.set_row_spacings(4)

        ds = pggui.Spinner(0, 31, ttt.day)
        mms = pggui.Spinner(1, 12, ttt.month)
        ys = pggui.Spinner(1995, 2100, ttt.year)

        ds.set_sensitive(False); mms.set_sensitive(False); ys.set_sensitive(False);

        ptab.attach_defaults(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1); self.col += 1

        ptab.attach_defaults(pggui.Label(" D_ay: ", ds), self.col, self.col+1,  self.row, self.row + 1)  ; self.col += 1
        ptab.attach_defaults(ds, self.col, self.col+1,  self.row, self.row + 1)            ; self.col += 1

        ptab.attach_defaults(pggui.Label(" Mon_th: ", mms), self.col, self.col+1,  self.row, self.row + 1)     ; self.col += 1
        ptab.attach_defaults(mms,  self.col, self.col+1,  self.row, self.row + 1)              ; self.col += 1

        ptab.attach_defaults(pggui.Label(" Y_ear: ", ys),  self.col, self.col+1,  self.row, self.row + 1)     ; self.col += 1
        ptab.attach_defaults(ys,  self.col, self.col+1,  self.row, self.row + 1)              ; self.col += 1
        ptab.attach(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1,
                            Gtk.AttachOptions.EXPAND , Gtk.AttachOptions.EXPAND , 4, 4); self.col += 1

        #nowh = ttt.hour; nowm = ttt.minute
        if idx >= len(xdarrs):
            tnow = datetime.datetime.today()
            nowh = tnow.hour; nowm = tnow.minute
            # See if there is an entry, step forward
            for ff in range(10):
                got = False
                for fff in xdarrs:
                    if fff[1][3] == nowh:
                        if fff[1][4] == nowm + ff:
                            got = True
                            break

                # Assign, contain
                if not got:
                    nowm += ff
                    nowm = nowm % 59
                    break
            durm = 60-nowm
        else:
            nowh = xdarrs[idx][1][3]
            nowm = xdarrs[idx][1][4]
            durm = xdarrs[idx][1][5]

        def change_hs(val):
            #print("change_hs", val)
            if self.alarr:
                self.alarr[0][1].set_value(val)

        def change_ms(val):
            #print("change_ms", val)
            if self.alarr:
                self.alarr[0][2].set_value(val)

        def change_dds(val):
            #print("change_dds", val)
            pass

        hs  = pggui.Spinner(0, 23, nowh, change_hs);
        ms  = pggui.Spinner(0, 59, nowm, change_ms);
        dds = pggui.Spinner(0, 1000, durm, change_dds)

        def set_hs(val):
            #print("set_hs", val)
            hs.set_value(int(val))

        def set_ms(val):
            #print("set_ms", val)
            ms.set_value(int(val))

        def set_dds(val):
            #print("set_dds", val)
            dds.set_value(int(val))

        self.row += 1; self.col = 0
        ptab.attach_defaults(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1); self.col += 1
        ptab.attach_defaults(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1); self.col += 1
        ptab.attach_defaults(pgsimp.HourSel(set_hs), self.col, self.col+1,  self.row, self.row + 1) ; self.col += 1
        ptab.attach_defaults(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1); self.col += 1
        ptab.attach_defaults(pgsimp.MinSel(set_ms), self.col, self.col+1,  self.row, self.row + 1) ; self.col += 1
        ptab.attach_defaults(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1); self.col += 1
        ptab.attach_defaults(pgsimp.MinSel(set_dds), self.col, self.col+1,  self.row, self.row + 1) ; self.col += 1

        self.row += 1; self.col = 0
        ptab.attach_defaults(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1); self.col += 1

        ptab.attach_defaults(pggui.Label(" Hour: ", hs), self.col, self.col+1,  self.row, self.row + 1)  ; self.col += 1
        ptab.attach_defaults(hs, self.col, self.col+1,  self.row, self.row + 1)            ; self.col += 1

        ptab.attach_defaults(pggui.Label(" Minute: ", ms), self.col, self.col+1,  self.row, self.row + 1)     ; self.col += 1
        ptab.attach_defaults(ms,  self.col, self.col+1,  self.row, self.row + 1)              ; self.col += 1

        ptab.attach_defaults(pggui.Label(" Duration: (min) ", ms), self.col, self.col+1,  self.row, self.row + 1)     ; self.col += 1
        ptab.attach_defaults(dds,  self.col, self.col+1,  self.row, self.row + 1)              ; self.col += 1

        ptab.attach(pggui.Label("  "), self.col, self.col+1, self.row, self.row + 1,
                            Gtk.AttachOptions.EXPAND , Gtk.AttachOptions.EXPAND , 4, 4); self.col += 1

        self.row += 1; self.col = 0

        self.nowarr = ((ds, mms, ys, hs, ms, dds))

        return ptab

    # --------------------------------------------------------------------

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

    def make_scriptline(self):
        hbox5 = Gtk.HBox()
        hbox5.pack_start(pggui.Label(" "), 0, 0, 4)
        hbox5.pack_start(pggui.Label(" Execute Script:"), 0, 0, 4)
        hbox5.pack_start(Gtk.CheckButton("Enabled"), 0, 0, 4)
        self.script = Gtk.Entry()
        hbox5.pack_start(self.script, True, True, 4)
        hbox5.pack_start(Gtk.Button("Browse"), 0, 0, 4)
        return hbox5

    def ok(self, buff):

        if not self.callb:
            self.destroy()
            return

        self.self2.mainwin.logwin.append_logwin(
                                "Saved: %s %s\r" % (self.uuid, datetime.datetime.today().ctime()) )
        #print("UUID:", self.uuid)
        txtarr = []
        #print ("got data", end = " ")
        for bb in self.table.texts:
            #print(bb.get_text(), end = " ")
            txtarr.append(bb.get_text())

        txtarr.append(self.edit.get_text())
        #print("Free form:", self.edit.get_text())

        # Cleanse controls out of the data, assemble it
        xnowarr = [];  xalarr = []
        for cc in self.alarr:
            #print("cc", cc[0].get_active(), cc[1].get_value(), \
            #cc[2].get_value(),  end = " ")
            idx = 0; ddd = []
            # Last entry
            for dd in cc[3]:
                #print("%s=%d" % (check_fill[idx].strip(), dd.get_active()), end = " ")
                ddd.append(dd.get_active())
                idx += 1

            # Assemble, append
            ccc = (cc[0].get_active(), int(cc[1].get_value()), \
                        int(cc[2].get_value()),  ddd)
            xalarr.append(ccc)
            #print()

        #print("Now array:", end = " ")
        for ww in self.nowarr:
            #print(ww.get_value(), end = " ")
            xnowarr.append(int(ww.get_value()))
        #print()

        arrx = (self.uuid.hex, tuple(xnowarr), txtarr, xalarr)
        self.callb("OK", arrx)
        self.destroy()

    def cancel(self, buff):
        if self.callb:
            self.callb("CANCEL", self)
        self.destroy()
        pass

    def area_button(self, butt, arg):
        #print("Button press in CalEntry")
        pass

if __name__ == "__main__":
    print("This is a module file, use pycalgui.py")

# EOF






