#!/usr/bin/env python3

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform, random
import ctypes, datetime, sqlite3, warnings, math, pickle
from calendar import monthrange

sys.path.append('../common')
import pggui, pgutils, pgsimp, pgbox

# Spec:

'''MINYEAR <= year <= MAXYEAR,
        1 <= month <= 12,
        1 <= day <= number of days in the given month and year,
        0 <= hour < 24,
        0 <= minute < 60,
        0 <= second < 60,
        0 <= microsecond < 1000000,'''

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import cairo

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

daystr = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
monstr = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
            "Oct", "Nov", "Dec")


def spinner(startx, endx, default = 1):

    adj2 = Gtk.Adjustment(startx, 1.0, endx, 1.0, 5.0, 0.0)
    spin2 = Gtk.SpinButton.new(adj2, 0, 0)
    spin2.set_value(default)
    spin2.set_wrap(True)
    return spin2


class CalEntry(Gtk.Window):

    def __init__(self, hx, hy, self2, callb = None):

        #print("CalEntry init", hx, hy)

        Gtk.Window.__init__(self)
        self.callb = callb
        self.set_accept_focus(True);
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.alt = False

        mx2, my2 = self2.get_pointer()
        hhh2 = self2.rect.height / 60
        hhh2 = min(hhh2, 12) + 6
        (nnn, ttt, pad, xx, yy) = self2.darr[hx][hy]
        arr = self2.xtext[hx][hy]
        idx = int(((my2 - (hhh2 + 6)) - yy) // hhh2)
        idx = min(idx, len(arr)-1)
        #strx = arr[idx]

        sss = ttt.strftime("%m-%d-%y")
        self.set_title("Calendar Item Entry for " + sss)

        row = 0; col = 0
        self.connect("button-press-event", self.area_button)
        self.connect("key-press-event", self.area_key)
        self.connect("key-release-event", self.area_key)

        #self.connect("unrealize", self.dest_me)
        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#efefef"))

        vbox = Gtk.VBox();
        self.ptab = Gtk.Table(); self.ptab.set_homogeneous(False)
        self.ptab.set_col_spacings(4); self.ptab.set_row_spacings(4)

        ds = spinner(0, 31, ttt.day)
        mms = spinner(1, 12, ttt.month)
        ys = spinner(1995, 2100, ttt.year)

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

        row += 1; col = 0
        self.ptab.attach_defaults(pggui.Label("  "), col, col+1, row, row + 1); col += 1
        self.ptab.attach_defaults(pggui.Label("  "), col, col+1, row, row + 1); col += 1

        nowh = ttt.hour; nowm = ttt.minute
        if ttt.hour == 0 and ttt.minute == 0:
            tnow = datetime.datetime.today()
            nowh = tnow.hour; nowm = tnow.minute

        hs = spinner(0, 24, nowh);  ms = spinner(0, 31, nowm)

        self.ptab.attach_defaults(pggui.Label(" Hour: ", hs), col, col+1,  row, row + 1)  ; col += 1
        self.ptab.attach_defaults(hs, col, col+1,  row, row + 1)            ; col += 1

        self.ptab.attach_defaults(pggui.Label(" Minute: ", ms), col, col+1,  row, row + 1)     ; col += 1
        self.ptab.attach_defaults(ms,  col, col+1,  row, row + 1)              ; col += 1

        self.ptab.attach(pggui.Label("  "), col, col+1, row, row + 1,
                            Gtk.AttachOptions.EXPAND , Gtk.AttachOptions.EXPAND , 4, 4); col += 1

        row += 1; col = 0
        self.ptab.attach(pggui.Label("  "), col, col+1, row, row + 1,
                            Gtk.AttachOptions.FILL, Gtk.AttachOptions.FILL, 1, 1); col += 1

        # ----------------------------------------------------------------

        self.dtab = Gtk.Table(); self.dtab.set_homogeneous(False)
        self.dtab.set_col_spacings(4); self.dtab.set_row_spacings(4)

        check_fill = ("Notify", "Sound ", "Popup ", "Beep  ",  "Email ")
        self.alarr = []
        for aa in range(3):
            row += 1; col = 0
            cb = Gtk.CheckButton()
            hs = spinner(0, 23); ms = spinner(0, 59); rs = spinner(0, 59)

            self.dtab.attach(pggui.Label("  "), col, col+1, row, row + 1,
                            Gtk.AttachOptions.FILL, Gtk.AttachOptions.FILL, 1, 1); col += 1

            self.dtab.attach_defaults(pggui.Label(" Alarm _%d Enabled: " % (aa+1), cb, "Enable / Disable"), col, col+1, row, row + 1); col += 1
            self.dtab.attach_defaults(cb, col, col+1, row, row + 1); col += 1

            self.dtab.attach_defaults(pggui.Label(" _Hour: "), col, col+1,  row, row + 1)  ; col += 1
            self.dtab.attach_defaults(hs, col, col+1,  row, row + 1)            ; col += 1

            self.dtab.attach_defaults(pggui.Label(" Minute: "), col, col+1,  row, row + 1)     ; col += 1
            self.dtab.attach_defaults(ms,  col, col+1,  row, row + 1)              ; col += 1

            self.dtab.attach(pggui.Label("  "), col, col+1, row, row + 1,
                            Gtk.AttachOptions.FILL, Gtk.AttachOptions.FILL, 1, 1); col += 1

            row += 1  ; col = 0

            self.dtab.attach_defaults(pggui.Label("  "), col, col+1, row, row + 1); col += 1

            hbox = Gtk.HBox(); cccarr = []
            for aa in check_fill:
                ccc = Gtk.CheckButton(aa)
                cccarr.append(ccc)
                hbox.pack_start(ccc, 0, 0, 0)

            self.dtab.attach_defaults(hbox,  col+3, col+6,  row, row + 1)              ; col += 6
            self.alarr.append([cb, hs, ms, rs, cccarr])

            row += 1  ; col = 0
            self.dtab.attach_defaults(pggui.Label("  "), col, col+1, row, row + 1); col += 1

        # ----------------------------------------------------------------

        hbox = Gtk.HBox(); lab = pggui.Label(ttt.ctime(), font = "Sans 16")
        lab.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse("#222222"))

        hbox.pack_start(pggui.Label(" "), 0, 0, 4)
        hbox.pack_start(lab, 1, 1, 4)
        hbox.pack_start(pggui.Label(" "), 0, 0, 4)

        arrt = ((" _Subject: ", "aa"), (" _Description: ", "hello"), (" _Notes: ", "notes"))
        self.table = pggui.TextTable(arrt, textwidth=85)
        self.table.texts[0].set_text(arr[idx])

        self.edit = pgsimp.SimpleEdit()
        self.edit.set_size_request(100, 100)

        vbox.pack_start(hbox, 0, 0, 2)

        hbox3 = Gtk.HBox()
        hbox3.pack_start(pggui.Label(" "), 0, 0, 0)
        hbox3.pack_start(self.table, 0, 0, 4)
        hbox3.pack_start(pggui.Label(" "), 0, 0, 0)

        hbox4 = Gtk.HBox()
        hbox4.pack_start(pggui.Label(" "), 0, 0, 0)
        hbox4.pack_start(self.edit, 1, 1, 4)
        hbox4.pack_start(pggui.Label(" "), 0, 0, 0)

        vbox.pack_start(self.ptab, 0, 0, 4)
        vbox.pack_start(self.dtab, 0, 0, 4)
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
        print("OK")
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

class CalPopup(Gtk.Window):

    def __init__(self, strx):
        Gtk.Window.__init__(self)
        self.set_accept_focus(False); self.set_decorated(False)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.connect("button-press-event", self.area_button)

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#efefef"))

        vbox = Gtk.VBox(); hbox = Gtk.HBox()
        lab = pggui.Label(strx)
        lab.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse("#222222"))
        hbox.pack_start(lab, 0, 0, 4)

        vbox.pack_start(hbox, 0, 0, 4)
        self.add(vbox)

    def area_button(self, butt, arg):
        print("Button press in tooltip")
        pass

class   CalStruct():
    def __init__(self, nnn = None, ttt = None, pad = None):
        self.nnn = nnn
        self.ttt = ttt
        self.pad = pad

    def __str__(self):
        return "%d %s %d" % (self.nnn, str(self.ttt), self.pad)

class CalCanvas(Gtk.DrawingArea):

    def __init__(self, xdate = None, statbox = None):
        Gtk.DrawingArea.__init__(self)
        self.statbox = statbox
        self.mouevent = None
        self.xtext = []
        self.darr = []
        self.old_hx = 0; self.old_hy = 0
        self.dlg = None

        if not xdate:
            self.set_date(datetime.datetime.today())
        else:
            self.set_date(date)

        tmp = datetime.datetime.today()
        self.zdate = datetime.datetime(tmp.year, tmp.month, tmp.day)

        self.fired = 0;  self.popped = 0
        self.set_can_focus(True)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.connect("draw", self.draw_event)
        self.connect("motion-notify-event", self.area_motion)
        self.connect("button-press-event", self.area_button)
        self.connect("button-release-event", self.area_button)
        self.coll = []
        self.cnt = 0
        self.drag = None
        self.resize = None
        self.dragcoord = (0,0)
        self.size2 = (0,0)
        self.noop_down = False
        self.hand = Gdk.Cursor(Gdk.CursorType.HAND1)
        self.arrow = Gdk.Cursor(Gdk.CursorType.ARROW)
        self.sizing =  Gdk.Cursor(Gdk.CursorType.SIZING)
        self.cross =  Gdk.Cursor(Gdk.CursorType.TCROSS)
        self.hair =  Gdk.Cursor(Gdk.CursorType.CROSSHAIR)
        self.fd = Pango.FontDescription()
        self.pangolayout = self.create_pango_layout("a")

    # Internal function to set up current month

    def __calc_curr(self):

        # Pre-calculate stuff (will be updated on paint)
        self.rect =   self.rect = self.get_allocation()
        self.head =  self.rect.height // 10
        newheight = self.rect.height - self.head
        pitchx = (self.rect.width) // 7;
        pitchy = newheight // 6;
        newheight = self.rect.height - self.head


        #print("show date:", self.xdate, daystr[self.xdate.weekday()])
        ydate =  datetime.datetime(self.xdate.year, self.xdate.month, 1)
        self.smonday = ydate.weekday()

        #print ("ydate", ydate, "Month starts: ", daystr[self.smonday])
        self.mlen = monthrange(self.xdate.year, self.xdate.month)[1]
        #print ("mlen", self.mlen)

        mmm  =  self.xdate.month-1; yyy  = self.xdate.year
        if mmm == 0:
            mmm = 12;  yyy -= 1
        self.mlen2 = monthrange(yyy, mmm)[1]
        #print ("mlen", self.mlen, "mlen2", self.mlen2)

        # Simulate new data
        self.xtext = []
        for aa in range(7):
            self.xtext.append( [] )
            last = self.xtext[len(self.xtext)-1]
            for bb in range(6):
                last.append( [] )
                # Pre fill random strings
                for cc in range(random.randint(2,12)):
                    last2 = last[len(last)-1]
                    xstr = "%d - %d : %d " % (aa, bb, cc)
                    xstr += pgutils.randstr(random.randint(5,140))
                    last2.append(xstr)

        self.darr = []
        for aa in range(7):
            self.darr.append( [] )
            lastd = self.darr[len(self.darr)-1]
            for bb in range(6):
                # Manipulate count as month parameters
                nnn = aa  + (bb * 7) - self.smonday; ttt = None; pad = 0;
                if nnn <  0:
                    pad = 1
                    nnn = self.mlen2 + nnn
                    m2 = self.xdate.month - 1; y2 = self.xdate.year
                    if m2 < 1: y2 -= 1; m2 = 12
                    ttt = datetime.datetime(y2, m2, nnn+1)
                elif nnn >= self.mlen:
                    pad = 2
                    nnn %= self.mlen
                    m2 = self.xdate.month + 1; y2 = self.xdate.year
                    if m2 > 12: y2 += 1; m2 = 1
                    ttt = datetime.datetime(y2, m2, nnn+1)
                else:
                    pad = 0
                    ttt = datetime.datetime(self.xdate.year, self.xdate.month, nnn+1)

                xx = aa * pitchx;  yy = bb * pitchy + self.head
                #sss = CalStruct(nnn, ttt, pad)
                lastd.append((nnn, ttt, pad, xx, yy))

        #print(self.xtext)
        #for aa in range(7):
        #    for bb in range(6):
        #        print("struct", aa, bb, str(self.darr[aa][bb]))
        #    print("--")


    def set_date(self, dt):

        #print("set_date", dt)

        self.freeze = True
        self.xdate = dt
        self.__calc_curr()
        self.freeze = False

        self.queue_draw()

    # Return where the hit is
    def hit_test(self, px, py):
        newheight = self.rect.height - self.head
        pitchx = (self.rect.width) // 7;
        pitchy = newheight // 6;
        py2 = int(py) - self.head
        return  int(px) // pitchx, py2 // pitchy

    def dest_me(self):
        print("Destroying ...")
        #self.get_root_window().set_cursor(self.arrow)

    def show_status(self, strx):
        if self.statusbar:
            self.statusbar.set_text(strx)

    def keytime(self):
        #print( "keytime raw", time.time(), self.fired)
        if self.dlg:
            return

        if self.fired ==  1:
            if not self.popped:
                mx, my = self.get_pointer()
                #print("mx, my ", mx, my)

                # Is mouse in cal?
                if mx > 0 and my > self.head and mx < self.rect.width and my < self.rect.height:
                    self.popped = True
                    hx, hy = self.hit_test(mx, my)
                    strx = "%d %d \n" % (hx, hy)
                    arr = self.xtext[hx][hy]
                    for sss in arr:
                        if len(sss) > 36:
                            sss = sss[:34] + " ... "
                        strx += sss + "\n"

                    self.tt = CalPopup(strx)

                    # Calculate self absolute (screen) position
                    posx, posy = self.mainwin.mywin.get_position()
                    #print("posx, posy", posx, posy)

                    self.tt.move(posx + mx, posy + my + self.head)
                    #self.tt.move(posx + mx - 12, posy + my + self.head - 12)
                    self.tt.show_all()
        self.fired -= 1

    def area_motion(self, area, event):
        #print ("motion event", event.state, event.x, event.y)
        self.mouevent = event

        '''if event.state & Gdk.ModifierType.SHIFT_MASK:
                    print( "Shift ButPress x =", event.x, "y =", event.y)
                if event.state & Gdk.ModifierType.CONTROL_MASK:
                    print( "Ctrl ButPress x =", event.x, "y =", event.y)
                if event.state & Gdk.ModifierType.MOD1_MASK :
                    print( "Alt ButPress x =", event.x, "y =", event.y)
                '''

        if self.popped:
            try:
                self.tt.destroy()
            except:
                pass
            self.popped = False
        else:
            self.fired += 1
            GLib.timeout_add(600, self.keytime)

        hx, hy = self.hit_test(int(event.x), int(event.y))
        #print("hx", hx, self.old_hx, "hy", hy,self.old_hy)
        #print("Hit", hx, hy, self.xtext[hx + 7 * hy])

        if (self.old_hx != hx or self.old_hy != hy):
            #print("Delta", hx, hy)
            self.queue_draw()

        self.old_hx = hx; self.old_hy = hy

    def area_button(self, area, event):
        self.mouevent = event
        #self.mouse = Rectangle(event.x, event.y, 4, 4)
        #print( "Button", event.button, "state", event.state, " x =", event.x, "y =", event.y)

        mods = event.state & Gtk.accelerator_get_default_mod_mask()

        if(mods & Gdk.ModifierType.MOD1_MASK):
            print("Modifier ALT",  event.state)

        if event.state & Gdk.ModifierType.CONTROL_MASK:
            print( "Ctrl ButPress x =", event.x, "y =", event.y)

        if  event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            print("DBL click", event.button)

        if  event.type == Gdk.EventType.BUTTON_RELEASE:
            self.drag = None
            self.resize = None
            self.noop_down = False
            #self.get_root_window().set_cursor(self.arrow)

        elif  event.type == Gdk.EventType.BUTTON_PRESS:

            if event.button == 1:
                hx, hy = self.hit_test(event.x, event.y)
                if self.popped:
                    try:    self.tt.destroy()
                    except: pass
                    self.popped = False
                (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
                if not pad:
                    self.dlg = CalEntry(hx, hy, self, self.done_dlg)

            if event.button == 3:
                if self.popped:
                    try:    self.tt.destroy()
                    except: pass
                hx, hy = self.hit_test(event.x, event.y)
                (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
                sdd = ttt.strftime("%a %d-%b-%y")
                self.menu = pggui.Menu(("Selection: %s" % sdd, "New Calendar Entry",
                                            "Edit Day"),
                                self.menucb, event)

    def menucb(self, txt, cnt):
        #print ("aa bb", aa, bb)
        if cnt == 1:
            xx, yy = self.get_pointer()
            hx, hy = self.hit_test(xx, yy)
            if self.popped:
                try:    self.tt.destroy()
                except: pass
                self.popped = False
            (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
            if not pad:
                self.dlg = CalEntry(hx, hy, self, self.done_dlg)

    def done_dlg(self, res, dlg):
        print("Done_dlg", res)
        '''
        if res == "OK":
            for bb in dlg.table.texts:
                print("got data", bb.get_text())

            print("Free form:", dlg.edit.get_text())

            for cc in dlg.alarr:
                print("cc", cc[0].get_active(), cc[1].get_value(), \
                cc[2].get_value(),cc[3].get_value(), cc[4].get_active())
         '''

    def fill_day(self, aa, bb, ttt, xxx, yyy, www, hhh):

        (nnn, ttt, pad, xx, yy) = self.darr[aa][bb]

        self.cr.rectangle(xxx, yyy, www, hhh)
        self.cr.clip()

        hhh2 = self.rect.height / 60
        hhh2 = min(hhh2, 12)

        #if not pad:
        #    xx2, yy2 = self.get_pointer()
        #    self.cr.set_source_rgba(255/255, 255/255, 255/255)
        #    self.cr.rectangle(xxx, yy2, www, hhh2)
        #    self.cr.fill()

        self.cr.set_source_rgba(25/255, 55/255, 25/255)
        self.fd.set_family("Arial")

        self.fd.set_size(hhh2 * Pango.SCALE);
        self.pangolayout.set_font_description(self.fd)
        prog = yyy
        for sss in self.xtext[aa][bb]:
            self.pangolayout.set_text(sss, len(sss))
            txx, tyy = self.pangolayout.get_pixel_size()
            self.cr.move_to(xxx, prog)
            PangoCairo.show_layout(self.cr, self.pangolayout)
            prog += tyy
        self.cr.new_path()
        self.cr.reset_clip()

    def draw_event(self, doc, cr):

        if self.freeze:
            return

        border = 4
        #print ("Painting .. ", self.cnt)
        self.cnt += 1

        #ctx = self.get_style_context()
        #fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
        #bg_color = ctx.get_background_color(Gtk.StateFlags.NORMAL)

        self.layout = PangoCairo.create_layout(cr)
        self.rect = self.get_allocation()
        self.cr = cr

        # Paint white, ignore system BG
        cr.set_source_rgba(255/255, 255/255, 255/255)
        #cr.rectangle( border, border, self.rect.width - border * 2, self.rect.height - border * 2);
        cr.rectangle( 0, 0, self.rect.width, self.rect.height);
        cr.fill()

        self.head =  self.rect.height // 10
        newheight = self.rect.height - self.head
        pitchx = (self.rect.width) // 7;
        pitchy = newheight // 6;

        # Month, year
        cr.set_source_rgba(25/255, 55/255, 25/255)
        self.fd.set_family("Arial")
        self.fd.set_size(self.rect.height / 30 * Pango.SCALE);
        self.pangolayout.set_font_description(self.fd)

        mmm = self.xdate.month - 1
        hhh = monstr[mmm] + ", " + str(self.xdate.year)
        self.pangolayout.set_text(hhh, len(hhh))
        txx, tyy = self.pangolayout.get_pixel_size()
        cr.move_to(self.rect.width/2 - txx/2, border)
        PangoCairo.show_layout(cr, self.pangolayout)

        # Weekdays
        cr.set_source_rgba(125/255, 125/255, 155/255)
        self.fd.set_size(self.rect.height / 35 * Pango.SCALE);
        self.pangolayout.set_font_description(self.fd)
        for aa in range(7):
            xx = aa * pitchx
            self.pangolayout.set_text(daystr[aa], len(daystr[aa]))
            txx, tyy = self.pangolayout.get_pixel_size()
            cr.move_to(xx + border + (pitchx/2 - txx/2), self.head - tyy - border)
            PangoCairo.show_layout(cr, self.pangolayout)

        # Horiz grid
        cr.set_source_rgba(125/255, 125/255, 125/255)
        cr.set_line_width(1)

        for aa in range(8):
            xx = aa * pitchx + self.rect.x
            cr.move_to(xx, self.head)
            cr.line_to(xx, self.rect.height)
        cr.stroke()

        # Vert grid
        for aa in range(6):
            yy = aa * pitchy
            cr.move_to(self.rect.x, yy + self.head)
            cr.line_to(self.rect.width, yy + self.head)
        cr.stroke()

        cr.set_source_rgba(88/255, 88/255, 100/255)

        for aa in range(7):
            for bb in range(6):
                # Init
                #ttt = datetime.datetime.today(); nnn = 0; pad = 0
                (nnn, ttt, pad, xx, yy) = self.darr[aa][bb]
                xx = aa * pitchx;  yy = bb * pitchy + self.head

                # Save it back to built array
                self.darr[aa][bb] = ((nnn, ttt, pad, xx, yy))

                nnn += 1
                if not pad:
                    xx2, yy2 = self.get_pointer()
                    mx, my  = self.hit_test(xx, yy); hx, hy  = self.hit_test(xx2, yy2)
                    if hx == mx and hy == my:
                        #print("Mouse over day:", xxx, yyy)
                        if self.zdate == ttt:
                            self.cr.set_source_rgba(200/255, 230/255, 200/255)
                        else:
                            self.cr.set_source_rgba(210/255, 210/255, 210/255)
                    elif self.zdate == ttt:
                        #print("This Month", ttt)
                        cr.set_source_rgba(230/255, 255/255, 220/255)
                    else:
                        self.cr.set_source_rgba(255/255, 255/255, 255/255)
                else:
                    cr.set_source_rgba(230/255, 230/255, 255/255)

                cr.rectangle(xx + border/2, yy + border/2,
                                    pitchx - border, pitchy - border)
                cr.fill()

                # Paint upper left
                cr.move_to(xx + border, yy)
                sss = str(nnn) # + "  " + ttt.strftime("%m-%d-%y")
                cr.set_source_rgba(100/255, 100/255, 255/255)
                self.fd.set_family("Arial")
                self.fd.set_size(12 * Pango.SCALE);
                self.pangolayout.set_font_description(self.fd)
                self.pangolayout.set_text(sss, len(sss))
                txx, tyy = self.pangolayout.get_pixel_size()
                PangoCairo.show_layout(cr, self.pangolayout)

                self.fill_day(aa, bb, ttt, xx + border, yy + border + tyy,
                                        pitchx - 2*border, pitchy - 2*border - tyy)

if __name__ == "__main__":

    print("use pyalagui.py")

# EOF
















