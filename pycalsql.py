#!/usr/bin/env python3

from __future__ import print_function

# ------------------------------------------------------------------------
# Test client for the pyserv project. Encrypt test.

import  os, sys, getopt, signal, select, socket, time, struct
import  random, stat, os.path, datetime, threading, sqlite3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

gi.require_version('Notify', '0.7')
from gi.repository import Notify

import pyala, pycal, pycallog

sys.path.append('../common')

import pggui, pgutils

# -------------------------------------------------------------------

class CalSQLite():

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
             (pri INTEGER PRIMARY KEY, keyx text, uid text, val text, val2 text, val3 text, val4 text)")
            self.c.execute("create index if not exists kcalendar on calendar (keyx)")
            self.c.execute("create index if not exists pcalendar on calendar (pri)")

            self.c.execute("create table if not exists caldata \
             (pri INTEGER PRIMARY KEY, keyx text, val text, val2 text, val3 text)")
            self.c.execute("create index if not exists kcaldata on caldata (keyx)")
            self.c.execute("create index if not exists pcaldata on caldata (pri)")

            self.c.execute("create table if not exists calala \
             (pri INTEGER PRIMARY KEY, keyx text, val text, val2 text, val3 text)")
            self.c.execute("create index if not exists kcalala on calala (keyx)")
            self.c.execute("create index if not exists pcalala on calala (pri)")

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

        #print("Getting data by keyx=", kkk)

        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from calendar where keyx like ?", (kkk,))
            else:
                self.c.execute("select * from calendar where keyx like ?", (kkk,))
            rr = self.c.fetchall()
        except:
            print("Cannot get sql data", sys.exc_info())
            rr = None
            self.errstr = "Cannot get sql data" + str(sys.exc_info())

        finally:
            #c.close
            pass
        if rr:
            return (rr)
        else:
            return None

    def   getdata(self, kkk):
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from caldata where keyx like ?", (kkk,))
            else:
                self.c.execute("select * from caldata indexed by kcaldata where keyx like ?", (kkk,))
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

    def   put(self, keyx, uid, val, val2, val3, val4):

        #got_clock = time.clock()
        #print("put", keyx, uid, val, val2, val3, val4)

        ret = True
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from calendar where keyx == ?", (keyx,))
            else:
                self.c.execute("select * from calendar indexed by kcalendar where keyx == ?", (keyx,))
            rr = self.c.fetchall()
            if rr == []:
                #print "inserting"
                self.c.execute("insert into calendar (keyx, uid, val, val2, val3, val4) \
                    values (?, ?, ?, ?, ?, ?)", (keyx, uid, val, val2, val3, val4))
            else:
                #print "updating"
                if os.name == "nt":
                    self.c.execute("update calendar \
                                set uid = ? val = ? val2 = ?, val3 = ?, val4 = ? where keyx = ?", \
                                      (uid, val, val2, val3, val4, keyx))
                else:
                    self.c.execute("update calendar indexed by kcalendar \
                                set uid = ?, val = ?, val2 = ?, val3 = ?, val4 = ? where keyx = ?",\
                                     (uid, val, val2, val3, val4, keyx))
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

    def   putdata(self, keyx, val, val2, val3):

        #got_clock = time.clock()

        ret = True
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from caldata where keyx == ?", (keyx,))
            else:
                self.c.execute("select * from caldata indexed by kcaldata where keyx == ?", (keyx,))
            rr = self.c.fetchall()
            if rr == []:
                #print "inserting"
                self.c.execute("insert into caldata (keyx, val, val2, val3) \
                    values (?, ?, ?, ?)", (keyx, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.c.execute("update caldata \
                                set val = ? val2 = ?, val3 = ? where keyx = ?", \
                                      (val, val2, val3, keyx))
                else:
                    self.c.execute("update caldata indexed by kcaldata \
                                set val = ?, val2 = ?, val3 = ? where keyx = ?",\
                                     (val, val2, val3, keyx))
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

    def   putala(self, keyx, val, val2, val3):

        #got_clock = time.clock()

        ret = True
        try:
            #c = self.conn.cursor()
            if os.name == "nt":
                self.c.execute("select * from calala where keyx == ?", (keyx,))
            else:
                self.c.execute("select * from calala indexed by kcalala where keyx == ?", (keyx,))
            rr = self.c.fetchall()
            if rr == []:
                #print "inserting"
                self.c.execute("insert into caldata (keyx, val, val2, val3) \
                    values (?, ?, ?, ?)", (keyx, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.c.execute("update caldata \
                                set val = ? val2 = ?, val3 = ? where keyx = ?", \
                                      (val, val2, val3, keyx))
                else:
                    self.c.execute("update caldata indexed by kcaldata \
                                set val = ?, val2 = ?, val3 = ? where keyx = ?",\
                                     (val, val2, val3, keyx))
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


# EOF
