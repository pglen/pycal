#!/usr/bin/env python3

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform
import ctypes, datetime, sqlite3, warnings, math, pickle

#from six.moves import range

import gi; gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Pango
from gi.repository import cairo

gi.require_version('PangoCairo', '1.0')
from gi.repository import PangoCairo

class CalCanvas(Gtk.DrawingArea):

    def __init__(self, statbox = None):
        Gtk.DrawingArea.__init__(self)
        self.statbox = statbox
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
        self.mouse = Rectangle(event.x, event.y, 4, 4)
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
            hit = Rectangle(event.x, event.y, 2, 2)
            hitx = None

    def draw_event(self, doc, cr):

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
        border = 4
        cr.set_source_rgba(255/255, 255/255, 255/255)
        cr.rectangle( border, border, self.rect.width - border * 2, self.rect.height - border * 2);
        cr.fill()

        head =  self.rect.height // 10
        newheight = self.rect.height - head

        # Horiz
        pitchx = (self.rect.width) // 7;
        pitchy = newheight // 7;
        cr.set_source_rgba(125/255, 125/255, 125/255)
        cr.set_line_width(1)

        for aa in range(7):
            xx = aa * pitchx
            cr.move_to(xx, head)
            cr.line_to(xx, self.rect.height)
        cr.stroke()
        for aa in range(7):
            yy = aa * pitchy
            cr.move_to(0, yy + head)
            cr.line_to(self.rect.width, yy + head)
        cr.stroke()

        cr.set_source_rgba(88/255, 88/255, 100/255)
        self.fd.set_family("Arial")
        self.fd.set_size(10 * Pango.SCALE);
        self.pangolayout.set_font_description(self.fd)

        for aa in range(7):
            for bb in range(7):
                xx = aa * pitchx;  yy = bb * pitchy + head
                cr.move_to(xx + border, yy)
                sss = str(aa  + (bb*7) + 1)
                self.pangolayout.set_text(sss, len(sss))
                txx, tyy = self.pangolayout.get_pixel_size()
                PangoCairo.show_layout(cr, self.pangolayout)





