#!/usr/bin/env python3

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform, random
import ctypes, datetime, sqlite3, warnings, math, pickle
from calendar import monthrange

sys.path.append('../common')
import pggui, pgutils

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

class CalEntry(Gtk.Window):

    def __init__(self, strx, callb = None):
        Gtk.Window.__init__(self)
        self.callb = callb
        self.set_accept_focus(True);
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.connect("button-press-event", self.area_button)
        #self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#efefef"))

        vbox = Gtk.VBox(); hbox = Gtk.HBox()
        lab = Gtk.Label(strx)

        lab.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse("#222222"))
        hbox.pack_start(lab, 0, 0, 4)

        '''self.tr1 = pggui.TextRow("Subject:       ", "None", vbox)
        self.tr2 = pggui.TextRow("Dessription: ", "No Description", vbox)
        self.tr3 = pggui.TextRow("Notes:          ", "", vbox)
        '''
        arr = (("Sub:", "aa"), ("Desc", "hello"), ("Notes:", "notes"))
        self.table = pggui.TextTable(arr)

        hbox2 = Gtk.HBox()
        bbb1 = Gtk.Button(" Cancel  "); bbb1.connect("clicked", self.cancel)
        bbb2 = Gtk.Button("    OK     "); bbb2.connect("clicked", self.ok)

        hbox2.pack_start(Gtk.Label(" "), 1, 1, 0)
        hbox2.pack_start(bbb1, 0, 0, 2);   hbox2.pack_start(bbb2, 0, 0, 2)
        vbox.pack_start(hbox, 0, 0, 2)

        hbox3 = Gtk.HBox()
        hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)
        hbox3.pack_start(self.table, 0, 0, 4)
        hbox3.pack_start(Gtk.Label(" "), 0, 0, 0)

        vbox.pack_start(hbox3, 0, 0, 4)
        vbox.pack_start(hbox2, 0, 0, 4)

        self.add(vbox)
        self.show_all()
        self.set_modal(True)
        self.set_keep_above(True)

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

class Popup(Gtk.Window):

    def __init__(self, strx):
        Gtk.Window.__init__(self)
        self.set_accept_focus(False); self.set_decorated(False)
        self.set_events(Gdk.EventMask.ALL_EVENTS_MASK)
        self.connect("button-press-event", self.area_button)

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#efefef"))

        vbox = Gtk.VBox(); hbox = Gtk.HBox()
        lab = Gtk.Label(strx)
        lab.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse("#222222"))
        hbox.pack_start(lab, 0, 0, 4)

        vbox.pack_start(hbox, 0, 0, 4)
        self.add(vbox)

    def area_button(self, butt, arg):
        print("Button press in tooltip")
        pass



class CalCanvas(Gtk.DrawingArea):

    def __init__(self, xdate = None, statbox = None):
        Gtk.DrawingArea.__init__(self)
        self.statbox = statbox
        self.mouevent = None
        self.xtext = []
        self.old_hx = 0; self.old_hy = 0
        self.dlg = None

        for aa in range(6*7):
            self.xtext.append([])

        if not xdate:
            self.set_date(datetime.datetime.today())
        else:
            self.set_date(date)

        tmp = datetime.datetime.today()
        self.zdate = datetime.datetime(tmp.year, tmp.month, tmp.day)

        self.fired = 0
        self.popped = 0
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

    def __calc_curr(self):

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

    def set_date(self, dt):
        print("set_date", dt)

        # Simulate new data
        self.xtext = []
        for aa in range(7):
            self.xtext.append( [] )
            for bb in range(6):
                last = self.xtext[len(self.xtext)-1]
                last.append( [] )
                for cc in range(5):
                    last2 = last[len(last)-1]
                    xstr = "%d - %d : %d " % (aa, bb, cc)
                    xstr += pgutils.randstr(random.randint(5,140))
                    last2.append(xstr)

        #print(self.xtext)

        self.xdate = dt
        self.__calc_curr()
        self.queue_draw()

    # Return where the hit is
    def hit_test(self, px, py):
        newheight = self.rect.height - self.head
        pitchx = (self.rect.width) // 7;
        pitchy = newheight // 6;
        py2 = py - self.head
        return  px // pitchx, py2 // pitchy

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

                    self.tt = Popup(strx)

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
            self.get_root_window().set_cursor(self.arrow)

        if  event.type == Gdk.EventType.BUTTON_PRESS:
            self.get_root_window().set_cursor(self.cross)
            pass

        hx, hy = self.hit_test(int(event.x), int(event.y))
        arr = self.xtext[hx][hy]

        #for sss in arr:
        #    print(sss)

        if self.popped:
            try:
             self.tt.destroy()
            except:
             pass
        self.popped = False
        self.dlg = CalEntry(arr[0], self.done_dlg)

    def done_dlg(self, res, dlg):
        print("Done_dlg", res)
        for bb in dlg.table.texts:
            print("got data", bb.get_text())

    def fill_day(self, aa, bb, ttt, xxx, yyy, www, hhh):

        self.cr.rectangle(xxx, yyy, www, hhh)
        self.cr.clip()

        self.cr.set_source_rgba(25/255, 55/255, 25/255)
        self.fd.set_family("Arial")

        hhh = self.rect.height / 60
        hhh = min(hhh, 12)
        self.fd.set_size(hhh * Pango.SCALE);
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

        border = 4
        #print ("Painting .. ", self.cnt)
        self.cnt += 1
        ctx = self.get_style_context()
        fg_color = ctx.get_color(Gtk.StateFlags.NORMAL)
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

        ttt = datetime.datetime.today()

        for aa in range(7):
            for bb in range(6):
                pad = 0
                xx = aa * pitchx;  yy = bb * pitchy + self.head
                # Manipulate count as month parameters

                nnn = aa  + (bb*7) - self.smonday
                if nnn <  0:
                    pad = True
                    nnn = self.mlen2 + nnn
                    m2 = self.xdate.month - 1; y2 = self.xdate.year
                    if m2 < 1: y2 -= 1; m2 = 12
                    ttt = datetime.datetime(y2, m2, nnn+1)
                elif nnn >= self.mlen:
                    pad = True
                    nnn %= self.mlen
                    m2 = self.xdate.month + 1; y2 = self.xdate.year
                    if m2 > 12: y2 += 1; m2 = 1
                    ttt = datetime.datetime(y2, m2, nnn+1)
                else:
                    ttt = datetime.datetime(self.xdate.year, self.xdate.month, nnn+1)

                nnn += 1

                if not pad:
                    xx2, yy2 = self.get_pointer()
                    mx, my  = self.hit_test(xx, yy); hx, hy  = self.hit_test(xx2, yy2)
                    if hx == mx and hy == my:
                        #print("Mouse over day:", xxx, yyy)
                        self.cr.set_source_rgba(210/255, 210/255, 210/255)
                    elif self.zdate == ttt:
                        #print("Today", ttt)
                        cr.set_source_rgba(230/255, 255/255, 230/255)
                    else:
                        self.cr.set_source_rgba(255/255, 255/255, 255/255)
                else:
                    cr.set_source_rgba(240/255, 240/255, 255/255)

                cr.rectangle(xx + border/2, yy + border/2,
                                    pitchx - border, pitchy - border)
                cr.fill()

                cr.move_to(xx + border, yy)
                sss = str(nnn)  + "  " + ttt.strftime("%m-%d-%y")
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





