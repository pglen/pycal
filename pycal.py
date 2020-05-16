#!/usr/bin/env python3

from __future__ import absolute_import, print_function

import signal, os, time, sys, subprocess, platform, random
import ctypes, datetime, sqlite3, warnings, math, pickle
from calendar import monthrange

import pycalent, pycallog

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

class CalCanvas(Gtk.DrawingArea):

    def __init__(self, xdate = None, statbox = None):
        Gtk.DrawingArea.__init__(self)
        self.statbox = statbox
        self.mouevent = self.dlg = None
        self.xtext = self.darr = self.xarr = self.coll = []
        self.old_hx = 0; self.old_hy = 0; self.fired = 0;
        self.popped = self.cnt = 0
        self.shx, self.shy = (-1, -1)
        self.drag = self.resize = None
        self.dragcoord = (0,0)
        self.size2 = (0,0)
        self.noop_down = False

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
        self.fd = Pango.FontDescription()
        self.pangolayout = self.create_pango_layout("a")
        self._cursors()

    # --------------------------------------------------------------------
    def set_dbfile(self, dbfile):

        self.dbfile = dbfile
        try:
            self.sql = calsql(self.dbfile)
        except:
            print("Cannot make calendar database.")


    def _cursors(self):
        self.hand = Gdk.Cursor(Gdk.CursorType.HAND1)
        self.arrow = Gdk.Cursor(Gdk.CursorType.ARROW)
        self.sizing =  Gdk.Cursor(Gdk.CursorType.SIZING)
        self.cross =  Gdk.Cursor(Gdk.CursorType.TCROSS)
        self.hair =  Gdk.Cursor(Gdk.CursorType.CROSSHAIR)

    # Internal function to set up current month

    def __calc_curr(self):

        # Pre-calculate stuff (will be updated on paint)
        self.rect = self.get_allocation()
        self.head =  self.rect.height // 10
        newheight = self.rect.height - self.head

        pitchx = (self.rect.width) // 7; pitchy = newheight // 6;
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

            '''for bb in range(6):
                last.append( [] )
                # Pre fill random strings
                for cc in range(random.randint(2,12)):
                    last2 = last[len(last)-1]
                    xstr = "%d - %d : %d " % (aa, bb, cc)
                    xstr += pgutils.randstr(random.randint(5,140))
                    last2.append(xstr)
             '''
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
                lastd.append((nnn, ttt, pad, xx, yy))

        #print(self.xtext)


    def set_date(self, dt):

        #print("set_date", dt)
        pycallog.logwin.append_logwin("Set new date on cal: %s\n" % dt.ctime())

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
                    try:
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
                    except:
                        print(sys.exc_info())
                        pass

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
                print(sys.exc_info())
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

        elif  event.type == Gdk.EventType.BUTTON_PRESS:
            #print("Single click", event.button)
            if event.button == 1:
                self.shx, self.shy = self.hit_test(event.x, event.y)

            if event.button == 3:
                if self.popped:
                    try:    self.tt.destroy()
                    except: pass
                hx, hy = self.hit_test(event.x, event.y)
                (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
                sdd = ttt.strftime("%a %d-%b-%Y")
                self.menu = pggui.Menu(("Selection: %s" % sdd, "New Calendar Entry",
                                            "Edit entry", "Edit Day"),
                                                self.menucb, event)
            self.queue_draw()

        elif  event.type == Gdk.EventType.BUTTON_RELEASE:
            self.drag = None
            self.resize = None
            self.noop_down = False
            #self.get_root_window().set_cursor(self.arrow)

        elif  event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
            #print("DBL click", event.button)
            if event.button == 1:
                hx, hy = self.hit_test(event.x, event.y)
                if self.popped:
                    try:    self.tt.destroy()
                    except: pass
                    self.popped = False
                (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
                if not pad:
                    self.dlg = pycalent.CalEntry(hx, hy, self, self.done_dlg)


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
                self.dlg = pycalent.CalEntry(hx, hy, self, self.done_dlg)

        if cnt == 2:
            print("Editing entry")
        if cnt == 3:
            print("Editing day")

    # --------------------------------------------------------------------
    # Got data

    def done_dlg(self, res, arrx):


        if res != "OK":
            return

        # See if append or ovewrite
        done = False
        if self.xarr:
            for aa in range(len(self.xarr)):
                flag = True
                curr = self.xarr[aa]
                for bb in range(len(curr[1])-1):
                    if curr[1][bb] !=  arrx[1][bb]:
                        flag = False
                if flag:
                    done = True
                    self.xarr[aa] = arrx
                    #print("done_dlg: inserted", end = "")

        if not done:
            self.xarr.append(arrx)
            #print("done_dlg: appended", end = "")

        print(arrx)

    # --------------------------------------------------------------------

    def get_daydat(self, ddd):
        arr = []
        for aa in self.xarr:
            #last = aa[len(aa)-1]
            last = aa[1]
            if last[0] == ddd.day and last[1] == ddd.month and last[2] == ddd.year:
                #print("Date match")
                arr.append(aa)
        return arr

    def fill_day(self, aa, bb, ttt, xxx, yyy, www, hhh):

        (nnn, ttt, pad, xx, yy) = self.darr[aa][bb]

        self.cr.rectangle(xxx, yyy, www, hhh)
        self.cr.clip()

        hhh2 = self.rect.height / 60
        hhh2 = min(hhh2, 12)

        self.cr.set_source_rgba(25/255, 55/255, 25/255)
        self.fd.set_family("Arial")

        self.fd.set_size(hhh2 * Pango.SCALE);
        self.pangolayout.set_font_description(self.fd)
        prog = yyy

        arrd = self.get_daydat(ttt)
        arrsd = sorted(arrd, key=lambda val: val[1][3] * 60 + val[1][4] )
        if len(arrsd):
            try:
                for sss in arrsd:
                    #print("sss", sss[3][3], sss[3][4])
                    txt = "%02d:%02d " % (sss[1][3], sss[1][4])
                    if sss[2][0]:
                        txt += str(sss[2][0])
                    else:
                        txt += "Empty Subject Line " # + sss[0]

                    self.pangolayout.set_text(txt, len(txt))
                    txx, tyy = self.pangolayout.get_pixel_size()
                    self.cr.move_to(xxx, prog)
                    prog += tyy
                    PangoCairo.show_layout(self.cr, self.pangolayout)

            except:
                #print("fill_day", sys.exc_info())
                pgutils.put_exception("Fill_day")
                pass

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
                rrr, ggg, bbb = (255., 255., 255.)

                if not pad:
                    xx2, yy2 = self.get_pointer()
                    mx, my  = self.hit_test(xx, yy); hx, hy  = self.hit_test(xx2, yy2)
                    if hx == mx and hy == my:
                        #print("Mouse over day:", xxx, yyy)
                        if self.zdate == ttt:
                            rrr, ggg, bbb = (200/255, 230/255, 200/255)
                        elif self.shx == aa and self.shy == bb:
                            # Selected
                            rrr, ggg, bbb = (200/255, 220/255, 220/255)
                        else:
                            rrr, ggg, bbb = (210/255, 210/255, 210/255)

                    elif self.zdate == ttt:
                        #print("Today", ttt)
                        rrr, ggg, bbb = (230/255, 255/255, 220/255)
                    elif self.shx == aa and self.shy == bb:
                        rrr, ggg, bbb = (215/255, 235/255, 235/255)
                    else:
                        rrr, ggg, bbb = (255/255, 255/255, 255/255)
                else:
                    #if self.shx == aa and self.shy == bb:
                    #    self.cr.set_source_rgba(255/255, 235/255, 235/255)
                    #else:
                    rrr, ggg, bbb = (230/255, 230/255, 255/255)

                self.cr.set_source_rgba(rrr, ggg, bbb)
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
                '''
                # Draw quarter ticks
                cr.set_source_rgba(10/255, 10/255, 125/255)
                tth = (pitchy - 2*border) / 4
                for aaa in range(4):
                    cr.move_to(xx +2, yy + tth * (aaa + 1))
                    cr.line_to(xx+10, yy + tth * (aaa + 1))
                '''
                ww = pitchx; hh = pitchy

                if self.shx == aa and self.shy == bb:
                    cr.set_source_rgba(10/255, 10/255, 125/255)

                    # Draw corners
                    cr.move_to(xx+2, yy+hh-2)
                    cr.line_to(xx+2, yy+hh-hh/4)
                    cr.move_to(xx+2, yy+hh - 2)
                    cr.line_to(xx+ww/4, yy +hh- 2)

                    cr.move_to(xx+ww-2, yy + 2)
                    cr.line_to(xx+ww-2, yy + hh/4)
                    cr.move_to(xx+ww-2, yy + 2)
                    cr.line_to(xx+ww-ww/4, yy + 2)

                    cr.stroke()


# -------------------------------------------------------------------

class calsql():

    def __init__(self, file):

        #self.take = 0
        self.errstr = ""

        try:
            self.conn = sqlite3.connect(file)
        except:
            print("Cannot open/create db:", file, sys.exc_info())
            return
        try:
            self.c = self.conn.cursor()
            # Create table
            self.c.execute("create table if not exists calendar \
             (pri INTEGER PRIMARY KEY, key text, val text, val2 text, val3 text)")
            self.c.execute("create index if not exists kcalendar on calendar (key)")
            self.c.execute("create index if not exists pcalendar on calendar (pri)")
            self.c.execute("create table if not exists caldata \
             (pri INTEGER PRIMARY KEY, key text, val text, val2 text, val3 text)")
            self.c.execute("create index if not exists kcaldata on caldata (key)")
            self.c.execute("create index if not exists pcaldata on caldata (pri)")

            self.c.execute("PRAGMA synchronous=OFF")
            # Save (commit) the changes
            self.conn.commit()
        except:
            print("Cannot insert sql data", sys.exc_info())
            self.errstr = "Cannot insert sql data" + str(sys.exc_info())

        finally:
            # We close the cursor, we are done with it
            #c.close()
            pass

    # --------------------------------------------------------------------
    # Return None if no data

    def   get(self, kkk):
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from calendar where key = ?", (kkk,))
            else:
                self.c.execute("select * from calendar indexed by kcalendar where key = ?", (kkk,))
            rr = self.c.fetchone()
        except:
            print("Cannot get sql data", sys.exc_info())
            rr = None
            self.errstr = "Cannot get sql data" + str(sys.exc_info())

        finally:
            #c.close
            pass
        if rr:
            return (rr[2], rr[3], rr[4])
        else:
            return None

    def   getdata(self, kkk):
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from caldata where key = ?", (kkk,))
            else:
                self.c.execute("select * from caldata indexed by kcaldata where key = ?", (kkk,))
            rr = self.c.fetchone()
        except:
            print("Cannot get sql data", sys.exc_info())
            rr = None
            self.errstr = "Cannot get sql data" + str(sys.exc_info())

        finally:
            #c.close
            pass
        if rr:
            return (rr[2], rr[3], rr[4])
        else:
            return None


    # --------------------------------------------------------------------
    # Return False if cannot put data

    def   put(self, key, val, val2, val3):

        #got_clock = time.clock()

        ret = True
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from calendar where key == ?", (key,))
            else:
                self.c.execute("select * from calendar indexed by kcalendar where key == ?", (key,))
            rr = self.c.fetchall()
            if rr == []:
                #print "inserting"
                self.c.execute("insert into calendar (key, val, val2, val3) \
                    values (?, ?, ?, ?)", (key, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.c.execute("update calendar \
                                set val = ? val2 = ?, val3 = ? where key = ?", \
                                      (val, val2, val3, key))
                else:
                    self.c.execute("update calendar indexed by kcalendar \
                                set val = ?, val2 = ?, val3 = ? where key = ?",\
                                     (val, val2, val3, key))
            self.conn.commit()
        except:
            print("Cannot put sql data", sys.exc_info())
            self.errstr = "Cannot put sql data" + str(sys.exc_info())
            ret = False
        finally:
            #c.close
            pass

        #self.take += time.clock() - got_clock

        return ret

    # --------------------------------------------------------------------
    # Return False if cannot put data

    def   putdata(self, key, val, val2, val3):

        #got_clock = time.clock()

        ret = True
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from caldata where key == ?", (key,))
            else:
                self.c.execute("select * from caldata indexed by kcaldata where key == ?", (key,))
            rr = self.c.fetchall()
            if rr == []:
                #print "inserting"
                self.c.execute("insert into caldata (key, val, val2, val3) \
                    values (?, ?, ?, ?)", (key, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.c.execute("update caldata \
                                set val = ? val2 = ?, val3 = ? where key = ?", \
                                      (val, val2, val3, key))
                else:
                    self.c.execute("update caldata indexed by kcaldata \
                                set val = ?, val2 = ?, val3 = ? where key = ?",\
                                     (val, val2, val3, key))
            self.conn.commit()
        except:
            print("Cannot put sql data", sys.exc_info())
            self.errstr = "Cannot put sql data" + str(sys.exc_info())
            ret = False
        finally:
            #c.close
            pass

        #self.take += time.clock() - got_clock

        return ret

    # --------------------------------------------------------------------
    # Get All

    def   getall(self, strx = "", limit = 1000):

        #print("getall '" +  strx + "'")

        try:
            #c = self.conn.cursor()
            self.c.execute("select * from calendar where val like ? or val2 like ? or val3 like ? limit  ?",
                                            (strx, strx, strx, limit))
            rr = self.c.fetchall()
        except:
            rr = []
            print("Cannot get all sql data", sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass

        return rr

    # --------------------------------------------------------------------
    # Return None if no data

    def   rmall(self):
        print("removing all")
        try:
            #c = self.conn.cursor()
            self.c.execute("delete from calendar")
            rr = self.c.fetchone()
        except:
            print("Cannot delete sql data", sys.exc_info())
            self.errstr = "Cannot delete sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass
        if rr:
            return rr[1]
        else:
            return None

    def   rmalldata(self):
        print("removing all")
        try:
            #c = self.conn.cursor()
            self.c.execute("delete from caldata")
            rr = self.c.fetchone()
        except:
            print("Cannot delete sql data", sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass
        if rr:
            return rr[1]
        else:
            return None

if __name__ == "__main__":
    print("This is a module file, use pycalgui.py")

# EOF






















