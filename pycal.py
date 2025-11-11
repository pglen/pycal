#!/usr/bin/env python3

import os, time, sys, datetime, random, warnings

from calendar import monthrange

import pycalent, pycallog, pycalsql, calfile, pyala

from pyvguicom import pggui, pgutils

white_col = (255/255, 255/255, 255/255)
grey_col  = (25/255, 55/255, 25/255)
lgrey_col = (125/255, 125/255, 125/255)
blue_col  = (230/255, 230/255, 255/255)
dblue_col = (88/255, 88/255, 100/255)
lgree_col = (150/255, 255/255, 150/255)

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

dayidx = "MO", "TU", "WE", "TH", "FR", "SA", "SU"
daystr = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
monstr = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
            "Oct", "Nov", "Dec")

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

class CalCanvas(Gtk.DrawingArea):

    def __init__(self, config, xdate = None, statbox = None):
        Gtk.DrawingArea.__init__(self)
        self.statbox = statbox
        self.config = config
        self.mouevent = self.dlg = None
        self.xtext = self.darr = self.monarr = self.coll = []
        self.old_hx = 0; self.old_hy = 0; self.fired = 0;
        self.popped = self.cnt = 0
        self.shx, self.shy = (-1, -1)
        self.drag = self.resize = None
        self.dragcoord = (0,0)
        self.size2 = (0,0)
        self.noop_down = False
        self.sql = None
        self.moonarr = []
        self.usarr = []
        self.donearr = []
        self.moon = True
        self.holy = True
        self.defc = True
        self.scrollday = 0
        self.ign = 0

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
        self.connect("key-press-event", self.keypress)

        self.fd = Pango.FontDescription()
        self.pangolayout = self.create_pango_layout("a")
        self._cursors()

        global handler_tick
        GLib.timeout_add(1000, self.handler_tick) #, self)

    def keypress(self, win, event):

        ret = False
        #print ("key", event.string, "val", event.keyval, "state", event.state)
        #print("hw", event.hardware_keycode)

        #if  event.state & Gdk.ModifierType.SHIFT_MASK:
        #    print("SHIFT")
        #if  event.state & Gdk.ModifierType.CONTROL_MASK:
        #    print("CONTROL")
        #if  event.state & Gdk.ModifierType.MOD1_MASK:
        #    print("ALT")

        if event.keyval == Gdk.KEY_Up:
            #print("Up")
            ret = True
        if event.keyval == Gdk.KEY_Down:
            #print("Down")
            ret = True
        if event.keyval == Gdk.KEY_Left:
            #print("Left")
            ret = True
        if event.keyval == Gdk.KEY_Right:
            #print("Right")
            ret = True

        return ret

    def invalidate(self):
        #print("Invalidate calendar")
        self.set_date(self.xdate)

    # --------------------------------------------------------------------
    def set_dbfile(self, dbfile, config):
        self.dbfile = dbfile
        try:
            self.sql = pycalsql.CalSQLite(self.dbfile, config)
        except:
            print("Cannot make/open calendar database.")
        self.monarr = self.get_month_data()

    #def add_calfile(self, calfilename):
    #    ''' Add additional calendar file '''
    #    arr = calfile.eval_file(calfilename)
    #    self.monarr += self.get_cal_data(arr)

    def set_moonfile(self, moonfile):
        self.moonarr = calfile.eval_file(moonfile)
        self.monarr += self.get_cal_data(self.moonarr)

    def set_usafile(self, usafile):
        self.usarr = calfile.eval_file(usafile, 0)
        #for aa in self.usarr:
        #    print(aa)
        self.monarr += self.get_cal_data(self.usarr)

    def set_holfile(self, holfile):
        self.holarr = calfile.eval_file(holfile)
        self.monarr += self.get_cal_data(self.holarr )

    def _cursors(self):
        disp =  self.get_display()
        self.hand = Gdk.Cursor.new_for_display(disp, Gdk.CursorType.HAND1)
        self.arrow = Gdk.Cursor.new_for_display(disp, Gdk.CursorType.ARROW)
        self.sizing =  Gdk.Cursor.new_for_display(disp, Gdk.CursorType.SIZING)
        self.cross =  Gdk.Cursor.new_for_display(disp, Gdk.CursorType.TCROSS)
        self.hair =  Gdk.Cursor.new_for_display(disp, Gdk.CursorType.CROSSHAIR)

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

    # --------------------------------------------------------------------
    def get_month_data(self):

        arr = []
        # Get padded (OK) days
        for aa in range(7):
            lastd = self.darr[aa]
            for bb in lastd:
                if bb[2]:
                    continue
                ddd = bb[1]
                key = "%02d-%02d-%02d %%" % (ddd.day, ddd.month, ddd.year)
                if not self.sql:
                    continue
                # Get it from the DB
                arr2 = self.sql.get(key)
                if not arr2:
                    continue
                #print("sql.get key", key, "got sql", arr2)
                for aa in arr2:
                    ttt = aa[1].split(" ")
                    (dd, mm, yy) = ttt[0].split("-")
                    (HH, MM) = ttt[1].split(":")
                    dur = ttt[2]
                    arr3, arr4, arr5 = self.sql.getdata(key)
                    #print("sql get data arr3", arr3, "arr4", arr4, "arr5", arr5)

                    defa = ( False, 0, 0, [False, False, False, False, False])
                    #arr3x = eval(arr3); print("arr3 evaled", type(arr3x), arr3x)

                    if arr3:
                        arr3 = eval(arr3)
                    else:
                        arr3 = defa[:]
                    if arr4:
                        arr4 = eval(arr4)
                    else:
                        arr4 = defa[:]
                    if arr5:
                        arr5 = eval(arr5)
                    else:
                        arr5 = defa[:]

                    def unpackx(*arrx):
                        res = arrx
                        return res
                    carr = [aa[2],
                                [int(dd), int(mm),
                                int(yy), int(HH), int(MM), int(dur)],
                                [*aa[3:]], [ arr3, arr4, arr5 ] ]
                    #print("reading carr", carr)
                    arr.append(carr)
        return arr

    # --------------------------------------------------------------------
    def get_cal_data(self, arrx):

        #print("get_cal_data() arrx", arrx)
        arr = []

        # Blank the alarm fields
        arr3 = [ False, 0, 0, [False, False, False, False, False]]
        arr4 = [ False, 0, 0, [False, False, False, False, False]]
        arr5 = [ False, 0, 0, [False, False, False, False, False]]

        # Process rules for the month
        for aa in arrx:
            if aa[6]:
                rr =  flatten(aa[6])
                if "FREQ=YEARLY" in rr:
                    rule = get_rule_str(str(self.xdate.month), rr)
                    if rule:
                        zdate = None
                        #print("byday args:", rr, "'" + rule + "'")
                        roffs = int(rule[:-2])
                        dd = 0; cnt = 0
                        for cc in dayidx:
                            if cc == rule[-2:]:
                                dd = cnt
                                break
                            cnt += 1
                        #print("day", roffs, "num", rule[-2:], "dd", dd)
                        mr = monthrange(self.xdate.year, self.xdate.month)[1]
                        if roffs >= 0:
                            for bb in range(1, mr + 1):
                                zdate = datetime.datetime(self.xdate.year, self.xdate.month, bb)
                                #print("zdate", zdate, zdate.weekday())
                                if zdate.weekday() == dd:
                                    #print ("encountered", zdate, zdate.weekday())
                                    roffs -= 1
                                    if roffs == 0:
                                        #print ("Set", zdate, zdate.weekday(), aa[0])
                                        break
                        else:
                            for bb in range(mr, 0, -1):
                                zdate = datetime.datetime(self.xdate.year, self.xdate.month, bb)
                                #print("zdate", zdate, zdate.weekday())
                                if zdate.weekday() == dd:
                                    #print ("encountered", zdate, zdate.weekday())
                                    roffs += 1
                                    if roffs == 0:
                                        #print ("Set", zdate, zdate.weekday(), aa[0])
                                        break

                        if zdate:
                            carr = ["", [ zdate.day, zdate.month, zdate.year,
                                                zdate.hour, zdate.minute, 0 ],
                                   [flatten(aa[0]), "", "", flatten(aa[5]) ],
                                   [ arr3, arr4, arr5 ]  ]
                            arr.append(carr)

            try:
                if self.xdate.year == aa[1].year and \
                        self.xdate.month == aa[1].month:

                    #print("day arr", aa)
                    #print(aa[1].year, aa[1].month, aa[1].day, "\nsum:",
                    #                flatten(aa[0]), "\ndesc:", flatten(aa[5]) )

                    carr = ["", [ aa[1].day, aa[1].month, aa[1].year,
                                            aa[1].hour, aa[1].minute, 0 ],
                               [flatten(aa[0]), "", "", flatten(aa[5]) ],
                               [ arr3, arr4, arr5 ]  ]
                    arr.append(carr)

            except:
                print("Cannot parse:", sys.exc_info())
                print( "aa", aa)
        return arr

    def set_date(self, dt):

        #print("set_date", dt)
        pycallog.logwin.append_logwin("Set new date on cal: %s\n" % dt.ctime())

        self.donearr = []
        self.freeze = True
        self.xdate = dt
        self.__calc_curr()
        self.freeze = False

        self.monarr = self.get_month_data()

        if self.moon:
            self.monarr += self.get_cal_data(self.moonarr)

        if self.holy:
            self.monarr += self.get_cal_data(self.usarr)

        self.queue_draw()

    # Return where the hit is
    def hit_test(self, px, py):
        newheight = self.rect.height - self.head
        pitchx = (self.rect.width) // 7;
        pitchy = newheight // 6;
        py2 = int(py) - self.head
        #print("px", px, "pitchy", pitchy)
        aa = 0; bb = 0
        try: aa = int(px) // pitchx;
        except: pass
        try: bb =  py2 // pitchy;
        except: pass
        return aa, bb

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
                        #print(sys.exc_info())
                        #pgutils.put_exception("key_time")
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
                #pgutils.put_exception("motion popped")
                #print(sys.exc_info())
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
            self.scrollday = 0
            self.queue_draw()

        self.old_hx = hx; self.old_hy = hy

    # --------------------------------------------------------------------

    def area_button(self, area, event):
        self.mouevent = event
        #self.mouse = Rectangle(event.x, event.y, 4, 4)
        #print( "Button", event.button, "state", event.state, " x =", event.x, "y =", event.y)

        mods = event.state & Gtk.accelerator_get_default_mod_mask()

        if(mods & Gdk.ModifierType.MOD1_MASK):
            #print("Modifier ALT",  event.state)
            pass
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            #print( "Ctrl ButPress x =", event.x, "y =", event.y)
            pass
        elif  event.type == Gdk.EventType.BUTTON_PRESS:
            #print("Single click", event.button)
            if event.button == 1:
                hit = pggui.Rectangle(event.x, event.y, 2, 2)

                if self.tri_2 != []:
                    #print("Got tri2", self.tri_2)
                    rrr = pggui.Rectangle(self.tri_2)
                    if rrr.intersect(hit)[0]:
                        #print("Click in tri 2")
                        self.scrollday += 1
                        self.invalidate()
                        self.ign += 1
                        return

                if self.tri_1 != []:
                    #print("Got tri1", self.tri_1)
                    rrr = pggui.Rectangle(self.tri_1)
                    if rrr.intersect(hit)[0]:
                        #print("Click in tri 1")
                        if  self.scrollday > 0:
                            self.scrollday -= 1
                        self.invalidate()
                        self.ign += 1
                        return

                self.ign = 0
                self.shx, self.shy = self.hit_test(event.x, event.y)

            if event.button == 3:
                if self.popped:
                    try:    self.tt.destroy()
                    except: pass
                hx, hy = self.hit_test(event.x, event.y)
                #print("hx, hY", hx, hy)
                (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
                sdd = ttt.strftime("%a %d-%b-%Y")
                warnings.simplefilter("ignore")
                self.menu = pggui.Menu(("Selection: %s" % sdd, "New Calendar Entry",
                                            "Edit entry", "Delete Entry"),
                                                self.menucb, event)
                warnings.simplefilter("default")

            self.queue_draw()

        elif  event.type == Gdk.EventType.BUTTON_RELEASE:
            self.drag = None
            self.resize = None
            self.noop_down = False
            #self.get_root_window().set_cursor(self.arrow)

        elif  event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:

            if self.ign:
                self.ign -= 1
                return

            #print("DBL click", event.x, event.y)
            if event.button == 1:
                if self.popped:
                    try:    self.tt.destroy()
                    except: pass
                    self.popped = False

                hx, hy = self.hit_test(event.x, event.y)
                (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
                if not pad:
                    self.dlg = pycalent.CalEntry( \
                                event.x, event.y, self, self.done_caldlg)

    def menucb(self, txt, cnt):
        #print (" txt cnt", txt, txt)
        xxx = self.menu.event.x;  yyy = self.menu.event.y
        if cnt == 1:
            #print("New entry")
            if self.popped:
                try:    self.tt.destroy()
                except: pass
                self.popped = False
            hx, hy = self.hit_test(xxx, yyy)
            (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
            if not pad:
                self.dlg = pycalent.CalEntry(xxx, yyy, self, self.done_caldlg, True)
        if cnt == 2:
            if self.popped:
                try:    self.tt.destroy()
                except: pass
                self.popped = False

            hx, hy = self.hit_test(xxx, yyy)
            (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
            #, int(xxx), int(yyy),)
            if self.config.debug > 3:
                print("Editing entry:",  nnn, "-", ttt, "-", pad, xx, yy)
            if not pad:
                self.dlg = pycalent.CalEntry(xxx, yyy, self, self.done_caldlg)

        if cnt == 3:
            if self.popped:
                try:    self.tt.destroy()
                except: pass
                self.popped = False

            hx, hy = self.hit_test(xxx, yyy)
            (nnn, ttt, pad, xx, yy) = self.darr[hx][hy]
            #if not pad:
            #    self.dlg = pycalent.CalEntry(xxx, yyy, self, self.done_caldlg)

            # This was the font height on draw ...
            hhh2 = self.rect.height / 60; hhh2 = min(hhh2, 12) + 6
            xdarr = self.get_daydat(ttt)
            xdarrs = sorted(xdarr, key=lambda val: val[1][3] * 60 + val[1][4] )
            idx = int(((yyy - (hhh2 + 4)) - yy) // hhh2) + self.scrollday
            #print(idx, "xdarrs", xdarrs)

            #print("len", len(xdarrs), "idx", idx)
            msg = "\n"

            if idx >= len(xdarrs):
                pggui.message(      "\nNot pointing to valid Item or"
                                    "\nItem not in personal calendar."
                                    "\nPlease select a deletable item.")
                return
            else:
                xdat = xdarrs[idx]
                if self.config.debug > 3:
                    print("Deleting entry", xdat)

                sdd = ttt.strftime("%a %d-%b-%Y")
                sdd +=  " %02d:%02d" %  (xdat[1][3], xdat[1][4])
                msg += "%s\n\n%s\n%s" % (sdd, xdat[2][0], xdat[2][1])

            warnings.simplefilter("ignore")
            ret = pggui.yes_no(msg, title = " Confirm Delete Item ")
            warnings.simplefilter("default")

            if ret == Gtk.ResponseType.YES:
                #print("deleting", xdat[0])
                ret = self.sql.rmone(xdat[0])
                #if not ret:
                #    pggui.message(      "\nCannot delete %s" % xdat[2][0])
                self.invalidate()

        if cnt == 4:
            print("Editing day")

    # --------------------------------------------------------------------
    # Got data

    def done_caldlg(self, res, cald):
        if res != "OK":
            return

        # See if append or ovewrite
        done = False
        if self.monarr:
            for aa in range(len(self.monarr)):
                flag = True
                curr = self.monarr[aa]
                for bb in range(len(curr[1])-1):
                    #print("curr", curr[1][bb], cald.xnowarr[bb])
                    if curr[1][bb] !=  cald.xnowarr[bb]:
                        flag = False
                        break
                if flag:
                    done = True
                    #self.monarr[aa] = arrx
                    print("done_caldlg: insert")
        if not done:
            #self.monarr.append(arrx)
            print("done_caldlg: append")
        #printit(cald)

        if self.config.debug > 2:
            print("cald", cald)

        # Save to SQLite database
        key = self.make_key(cald.xnowarr)

        if self.config.debug > 1:
            print("put:", key, "-",  cald.xuuid, "vals =", *cald.txtarr)
        self.sql.put(key,  cald.xuuid, *cald.txtarr)

        arrz = []
        for aa in cald.xalarr:
            arrz.append(str(aa))

        if self.config.debug > 1:
            print("put data:", key, "val =", *arrz)
        self.sql.putdata(cald.xuuid, *arrz)

        # Save to SQLite alarms database
        #print("put ala", arrx[3])
        #self.sql.putala(key, *arrz)

    # --------------------------------------------------------------------

    def make_key(self, sss):
        key = ""
        for bb in range(3):
            key += "%02d-" % (int(sss[bb]))
        key = str.strip(key, "-")
        key += " "
        for bb in range(2):
            key += "%02d:" % (int(sss[bb+3]))
        key = str.strip(key, ":")
        key += " %02d" % (int(sss[5]))
        return key

    def get_daydat(self, ddd):
        arr = []
        #print ("get_daydat for", ddd)
        # Get it for arr
        for aa in self.monarr:
            last = aa[1]
            if int(last[0]) == ddd.day and \
                int(last[1]) == ddd.month and \
                    int(last[2]) == ddd.year:
                #print("Date match", last)
                arr.append(aa)
            else:
                pass
                #print("no match", last[0], last[1], last[2])
                #print("with", ddd.day, ddd.month, ddd.year)

        return arr

    def decode_text(self, txt):
        strx = ""
        txt2 = txt.encode("ascii", "ignore")
        for aa in txt2:
            if ord(aa) < 128:
                strx += aa
        return strx
        #return strx.decode("cp437")

    def fill_day(self, aa, bb, ttt, xxx, yyy, www, hhh):

        (nnn, ttt, pad, xx, yy) = self.darr[aa][bb]

        if pad:
            return

        self.cr.rectangle(xxx, yyy, www, hhh)
        self.cr.clip()

        hhh2 = self.rect.height / 60
        hhh2 = min(hhh2, 12)

        self.cr.set_source_rgba(*grey_col)
        self.fd.set_family("Arial")

        self.fd.set_size(hhh2 * Pango.SCALE);
        self.pangolayout.set_font_description(self.fd)
        prog = yyy

        arrd = self.get_daydat(ttt)
        arrsd = sorted(arrd, key=lambda val: val[1][3] * 60 + val[1][4] )
        if self.shx == aa and self.shy == bb:
            tmpscroll = self.scrollday
        else:
            tmpscroll = 0

        if len(arrsd):
            try:
                for sss in arrsd[tmpscroll:]:
                    #print("sss", sss[3][3], sss[3][4])
                    txt = "%02d:%02d " % (int(sss[1][3]), int(sss[1][4]))
                    if sss[2][0]:
                        txt += str(sss[2][0])
                    else:
                        txt += "Empty Subject Line " # + sss[0]
                    #print("printing", txt, "len:", len(txt), "ulen", len(txt.encode("UTF8")) )
                    if sys.version_info[0] < 3:
                        txt2 = self.decode_text(txt)
                        print("ver 2", txt2)
                        self.pangolayout.set_text(txt2, len(txt2))
                    else:
                        self.pangolayout.set_text(txt, len(txt.encode("UTF8")) )

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
        self.cr2 = pggui.CairoHelper(cr)

        # Paint white, ignore system BG
        cr.set_source_rgba(*white_col)
        #cr.rectangle( border, border, self.rect.width - border * 2, self.rect.height - border * 2);
        cr.rectangle( 0, 0, self.rect.width, self.rect.height);
        cr.fill()

        self.head =  self.rect.height // 10
        newheight = self.rect.height - self.head
        pitchx = (self.rect.width) // 7;
        pitchy = newheight // 6;

        # Month, year
        cr.set_source_rgba(*grey_col)
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
        cr.set_source_rgba(*lgrey_col)
        self.fd.set_size(self.rect.height / 35 * Pango.SCALE);
        self.pangolayout.set_font_description(self.fd)
        for aa in range(7):
            xx = aa * pitchx
            self.pangolayout.set_text(daystr[aa], len(daystr[aa]))
            txx, tyy = self.pangolayout.get_pixel_size()
            cr.move_to(xx + border + (pitchx/2 - txx/2), self.head - tyy - border)
            PangoCairo.show_layout(cr, self.pangolayout)

        # Horiz grid
        cr.set_source_rgba(*lgrey_col)
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

        self.tri_2 = [] ; self.tri_1 = []
        cr.set_source_rgba(*dblue_col)

        for aa in range(7):
            for bb in range(6):
                # Init
                #ttt = datetime.datetime.today(); nnn = 0; pad = 0
                (nnn, ttt, pad, xx, yy) = self.darr[aa][bb]
                xx = aa * pitchx;  yy = bb * pitchy + self.head

                warnings.simplefilter("ignore")
                xx2, yy2 = self.get_pointer()
                warnings.simplefilter("default")
                mx, my  = self.hit_test(xx, yy); hx, hy  = self.hit_test(xx2, yy2)

                # Save it back to built array
                self.darr[aa][bb] = ((nnn, ttt, pad, xx, yy))

                nnn += 1
                rrr, ggg, bbb = (255., 255., 255.)

                if not pad:
                    if hx == mx and hy == my:
                        #print("Mouse over day:", mx, my)
                        if self.zdate == ttt:
                            rrr, ggg, bbb = (200/255, 230/255, 200/255)
                        elif self.shx == aa and self.shy == bb:
                            # Selected
                            rrr, ggg, bbb = (200/255, 220/255, 220/255)
                        else:
                            rrr, ggg, bbb = (240/255, 240/255, 240/255)

                    elif self.zdate == ttt:
                        #print("Today", ttt)
                        rrr, ggg, bbb = lgree_col
                    elif self.shx == aa and self.shy == bb:
                        rrr, ggg, bbb = (215/255, 235/255, 235/255)
                    else:
                        # Default
                        rrr, ggg, bbb = white_col
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

                if not pad:
                    if self.shx == aa and self.shy == bb:
                        # Draw nav arrows
                        self.cr.set_source_rgba(238/255, 255/255, 238/255)
                        xxx =  xx + border/2 + 11 * pitchx/12
                        yyy =  yy + border/2 + 5*pitchy/8
                        www =  pitchx - border - 11*pitchx/12
                        hhh =  pitchy - border - 5*pitchy/8
                        #cr.rectangle(xxx, yyy, www, hhh)
                        #cr.fill()

                        # Draw triangles
                        cr.set_line_width(1)
                        self.cr.set_source_rgba(100/255, 255/255, 100/255)
                        self.tri_1 = [xxx, yyy, www, hhh/3]
                        self.cr2.tri(self.tri_1)
                        cr.fill()
                        self.cr.set_source_rgba(100/255, 200/255, 100/255)
                        self.cr2.tri(self.tri_1)
                        cr.stroke()

                        # Draw triangles2
                        self.cr.set_source_rgba(100/255, 255/255, 100/255)
                        self.tri_2 = [xxx, yyy + 2*hhh/3, www, hhh/3]
                        self.cr2.tri2(self.tri_2)
                        cr.fill()
                        self.cr.set_source_rgba(100/255, 200/255, 100/255)
                        self.cr2.tri2(self.tri_2)
                        cr.stroke()

                        # Draw corners
                        cr.set_source_rgba(10/255, 10/255, 125/255)
                        cr.move_to(xx+2, yy+hh-2)
                        cr.line_to(xx+2, yy+hh-hh/4)
                        cr.move_to(xx+2, yy+hh - 2)
                        cr.line_to(xx+ww/4, yy +hh- 2)

                        cr.move_to(xx+ww-2, yy + 2)
                        cr.line_to(xx+ww-2, yy + hh/4)
                        cr.move_to(xx+ww-2, yy + 2)
                        cr.line_to(xx+ww-ww/4, yy + 2)

                        cr.stroke()

    # --------------------------------------------------------------------
    # Trigger alarms, if not done already
    def pop_alarm(self, aa):
        done = False
        for dd in self.donearr:
            if dd == aa[0]:
                done = True

        if not done:
            self.donearr.append(aa[0])
            dddd = str(aa[3][0][1]) + ":" + str(aa[3][0][2])
            self.mainwin.logwin.append_logwin("Alarm at: %s %s %s\r" %
                                    (dddd, aa[2][0], datetime.datetime.today().ctime()) )

            #print("Alarm triggered", dddd)
            pyala.play_sound()
            pyala.notify_sys(aa[2][0], aa[2][1], dddd)
            pggui.message("\n" + aa[2][0] + "\n" + aa[2][1], title =  "Alarm at " + dddd)

            sys.stdout.write('\a')
            sys.stdout.flush()

    def eval_alarm(self):

        flag = False
        tmp = datetime.datetime.today()
        if self.config.debug > 3:
            print("eval_alarm", tmp.day, "-", tmp.month, "-", tmp.year,
                                    tmp.hour, tmp.minute, tmp.second)
        for aa in self.monarr:
            #print("Data:", aa[1])
            # Is it today?
            if aa[1][0] == tmp.day and aa[1][1] == tmp.month  \
                    and aa[1][2] == tmp.year:
                #if self.config.debug > 1:
                #    print("Today", aa[1], aa[2])

                # Enabled?
                if aa[3][0][0]:
                    if self.config.debug > 3:
                        print("Enabled", aa[1], aa[2])
                    # Is it now?
                    if aa[1][3] == tmp.hour:
                        if aa[1][4] == tmp.minute:
                            self.pop_alarm(aa)

                    # Is it in the future?
                    if  aa[1][3] > tmp.hour or \
                          aa[1][3] == tmp.hour and aa[1][4] > tmp.minute:
                            print("future", aa[1][3], aa[1][4])
                            #print("future", aa)
                            #self.set_text(str(aa))
                            self.mainwin.mywin.set_title("Python Calendar -- next up: " \
                                +  aa[2][0] + " at "  +  \
                                    str(aa[1][3]) + ":" + str(aa[1][4]))

    def handler_tick(self):

        if self.config.debug > 4:
            print("handler_tick")
        self.eval_alarm()
        return True

        #try:
        #    GLib.timeout_add(1000, handler_tick, main_class)
        #except:
        #    print("Exception in setting timer handler", sys.exc_info())


if __name__ == "__main__":
    print("This is a module file, use pycalgui.py")

# EOF

