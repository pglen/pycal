#!/usr/bin/env python3

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings, math, pickle

from calendar import monthrange

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

class CalCanvas(Gtk.DrawingArea):

    def __init__(self, xdate = None, statbox = None):
        Gtk.DrawingArea.__init__(self)
        self.statbox = statbox

        if not xdate:
            self.set_date(datetime.datetime.today())
        else:
            self.set_date(date)

        tmp = datetime.datetime.today()
        self.zdate = datetime.datetime(tmp.year, tmp.month, tmp.day)

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

    def _calc_curr(self):

        print("show date:", self.xdate, daystr[self.xdate.weekday()])
        ydate =  datetime.datetime(self.xdate.year, self.xdate.month, 1)
        self.smonday = ydate.weekday()
        print ("ydate", ydate, "Month starts: ", daystr[self.smonday])

        self.mlen = monthrange(self.xdate.year, self.xdate.month)[1]
        print ("mlen", self.mlen)

        mmm  =  self.xdate.month-1; yyy  = self.xdate.year
        if mmm == 0:
            mmm = 12;  yyy -= 1
        self.mlen2 = monthrange(yyy,mmm)[1]
        print ("mlen2", self.mlen2)

    def set_date(self, dt):
        print("set_date", dt)
        self.xdate = dt
        self._calc_curr()
        self.queue_draw()

    def show_status(self, strx):
        if self.statusbar:
            self.statusbar.set_text(strx)

    def area_motion(self, area, event):
        #print ("motion event", event.state, event.x, event.y)
        pass

        '''if event.state & Gdk.ModifierType.SHIFT_MASK:
                    print( "Shift ButPress x =", event.x, "y =", event.y)
                if event.state & Gdk.ModifierType.CONTROL_MASK:
                    print( "Ctrl ButPress x =", event.x, "y =", event.y)
                if event.state & Gdk.ModifierType.MOD1_MASK :
                    print( "Alt ButPress x =", event.x, "y =", event.y)
                '''

    def area_button(self, area, event):
        #self.mouse = Rectangle(event.x, event.y, 4, 4)
        print( "Button", event.button, "state", event.state, " x =", event.x, "y =", event.y)

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

    def fill_day(self, nnn, xxx, yyy, www, hhh):

        self.cr.set_source_rgba(255/255, 255/255, 255/255)
        self.cr.rectangle(xxx, yyy, www, hhh)
        self.cr.clip()

        self.cr.set_source_rgba(25/255, 55/255, 25/255)
        self.fd.set_family("Arial")
        self.fd.set_size(self.rect.height / 60 * Pango.SCALE);
        self.pangolayout.set_font_description(self.fd)
        prog = yyy

        for aa in range(4):
            sss = "12345678 ABCD efghij"
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
        #self.crh = CairoHelper(cr)

        # Paint white, ignore system BG
        cr.set_source_rgba(255/255, 255/255, 255/255)
        cr.rectangle( border, border, self.rect.width - border * 2, self.rect.height - border * 2);
        cr.fill()

        self.rect.x += border
        self.rect.y += border

        head =  self.rect.height // 10
        newheight = self.rect.height - head
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
            cr.move_to(xx + border + (pitchx/2 - txx/2), head - tyy - border)
            PangoCairo.show_layout(cr, self.pangolayout)

        # Horiz
        cr.set_source_rgba(125/255, 125/255, 125/255)
        cr.set_line_width(1)

        for aa in range(7):
            xx = aa * pitchx
            cr.move_to(xx, head)
            cr.line_to(xx, self.rect.height)
        cr.stroke()
        # Vert
        for aa in range(6):
            yy = aa * pitchy
            cr.move_to(0, yy + head)
            cr.line_to(self.rect.width, yy + head)
        cr.stroke()

        cr.set_source_rgba(88/255, 88/255, 100/255)

        for aa in range(7):
            for bb in range(6):
                pad = 0
                xx = aa * pitchx;  yy = bb * pitchy + head
                #cr.move_to(xx + border, yy)

                # Manipulate count as month parameters
                nnn = aa  + (bb*7) - self.smonday
                if nnn <  0:
                    pad = 1
                    nnn %= self.mlen2
                if nnn >= self.mlen:
                    pad = 2
                    nnn %= self.mlen

                nnn += 1

                if not pad:
                    ttt = datetime.datetime(self.xdate.year, self.xdate.month, nnn)
                    if self.zdate == ttt:
                        print("Today", ttt)
                        cr.set_source_rgba(240/255, 240/255, 240/255)
                        cr.rectangle(xx + border/2, yy + border/2,
                                        pitchx - border, pitchy - border)
                        cr.fill()
                        cr.set_source_rgba(0/255, 50/255, 255/255)
                    else:
                        cr.set_source_rgba(88/255, 88/255, 100/255)
                else:
                    cr.set_source_rgba(255/255, 88/255, 100/255)

                cr.move_to(xx + border, yy)
                sss = str(nnn)
                self.fd.set_family("Arial")
                self.fd.set_size(11 * Pango.SCALE);
                #self.fd.set_size(self.rect.height / 50 * Pango.SCALE);
                self.pangolayout.set_font_description(self.fd)
                self.pangolayout.set_text(sss, len(sss))
                txx, tyy = self.pangolayout.get_pixel_size()
                PangoCairo.show_layout(cr, self.pangolayout)

                self.fill_day(nnn, xx + border, yy + border + tyy,
                                        pitchx - 2*border, pitchy - 2*border - tyy)


if __name__ == "__main__":

    print("use pyalagui.py")






