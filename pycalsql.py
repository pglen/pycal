#!/usr/bin/env python3

import os, sys, sqlite3

import pyala, pycal, pycallog
from pyvguicom import pgutils

class CalSQLite():

    ''' SQL routines for calendar '''

    def __init__(self, file, config):

        self.config = config
        self.errstr = ""

        if self.config.debug > 0:
            print("sql file:", file)
        try:
            self.curr = sqlite3.connect(file)
        except:
            print("Cannot open/create db:", file, sys.exc_info())
            return
        try:
            self.cur = self.curr.cursor()
            # Create table
            self.cur.execute("create table if not exists calendar \
             (pri INTEGER PRIMARY KEY, keyx text, uid text, val text, \
                                val2 text, val3 text, val4 text, val5 text)")
            self.cur.execute("create index if not exists kcalendar on calendar (keyx)")
            self.cur.execute("create index if not exists pcalendar on calendar (pri)")

            self.cur.execute("create table if not exists caldata \
             (pri INTEGER PRIMARY KEY, keyx text, val text, val2 text, \
                            val3 text, val4 text, val5 text)")
            self.cur.execute("create index if not exists kcaldata on caldata (keyx)")
            self.cur.execute("create index if not exists pcaldata on caldata (pri)")

            self.cur.execute("PRAGMA synchronous=OFF")
            # Save (commit) the changes
            self.curr.commit()
        except:
            print("Cannot insert sql data", sys.exc_info())
            self.errstr = "Cannot insert sql data" + str(sys.exc_info())

    # --------------------------------------------------------------------
    # Return None if no data

    def   get(self, kkk):

        if self.config.debug > 5:
            print("Getting by keyx =", "'" + kkk + "'")
        try:
            self.cur.execute("select * from calendar where keyx like ?", (kkk,))
        except:
            #print("Cannot get sql for ", kkk, sys.exc_info())
            #pgutils.print_exception("cannot get")
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        try:
            rr = self.cur.fetchall()
        except:
             rr = None
        if not rr:
            return None
        if self.config.debug > 2:
            print("key:", kkk)
            for aa in rr:
                print(" ", aa)
        return (rr)

    def   getdata(self, kkk, all = False):

        if self.config.debug > 5:
            print("Getting data by keyx =", "'" + kkk + "'")
        try:
            self.cur.execute("select * from caldata where keyx like ?", (kkk,))
        #except sqlite3.OperationalError:
        #    pass
        except:
            print("Cannot get sql data for", kkk, sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        try:
            rr = self.cur.fetchone()
        except:
            rr = None
        if not rr:
            return ([], [], [])
        if self.config.debug > 2:
            print("Data key:", kkk)
            for aa in rr:
                print(" ", aa)
        if all:
            return (rr)
        return (rr[2], rr[3], rr[4], rr[5], rr[6])

    # --------------------------------------------------------------------
    # Return False if cannot put data

    def   put(self, keyx, uid, val, val2, val3, val4, val5):

        #got_clock = time.clock()
        if self.config.debug > 1:
            print("putting:", keyx, uid, val, val2, val3, val4, val5)

        #print("types", type(keyx), type(uid), type(val), type(val2), \
        #                    type(val3), type(val4))
        ret = True
        try:
            self.cur.execute("select * from calendar indexed by \
                                 kcalendar where uid == ?", (uid,))
            rr = self.cur.fetchall()
            if rr == []:
                #print ("inserting", rr)
                self.cur.execute("insert into calendar (keyx, uid, val, val2, \
                            val3, val4, val5) values (?, ?, ?, ?, ?, ?, ?)", \
                            (keyx, uid, val, val2, val3, val4, val5))
            else:
                #print ("updating", rr)
                self.cur.execute("update calendar indexed by kcalendar \
                                set val = ?, val2 = ?, val3 = ?, \
                                    val4 = ?, val5 = ? where uid = ?",\
                                        (val, val2, val3, val4, val5, uid))
            self.curr.commit()
        except:
            print("Cannot put sql ", sys.exc_info())
            pgutils.print_exception("put")
            self.errstr = "Cannot put sql " + str(sys.exc_info())
            ret = False

        #self.take += time.clock() - got_clock

        return ret

    # --------------------------------------------------------------------
    # Return False if cannot put data

    def   putdata(self, keyx, val, val2, val3, val4, val5):

        #got_clock = time.clock()
        if self.config.debug > 1:
            print("putting data:", keyx, val, val2, val3, val4, val5)

        #print("types", type(keyx), type(val), type(val2), type(val3))

        ret = True
        try:
            self.cur.execute("select * from caldata indexed by kcaldata \
                                where keyx == ?", (keyx,))
            rr = self.cur.fetchall()
            if rr == []:
                #print "inserting"
                self.cur.execute("insert into caldata \
                  (keyx, val, val2, val3, val4, val5) \
                    values (?, ?, ?, ?, ?, ?)", (keyx, val, val2, val3, val4, val5))
            else:
                #print "updating"
                self.cur.execute("update caldata indexed by kcaldata \
                      set val = ?, val2 = ?, val3 = ?, val4 = ?, val5 = ? where keyx = ?",\
                            (val, val2, val3, val4, val5, keyx))
            self.curr.commit()
        except:
            print("Cannot put sql data", sys.exc_info())
            self.errstr = "Cannot put sql data" + str(sys.exc_info())
            ret = False

        #self.take += time.clock() - got_clock

        return ret

    # --------------------------------------------------------------------
    # Get All

    def   getall(self, strx = "", limit = 1000):

        if self.config.debug > 1:
            print("getall '" +  strx + "'")
        try:
            self.cur.execute("select * from calendar where val like ? or val2 like ? or val3 like ? limit  ?",
                                            (strx, strx, strx, limit))
            rr = self.cur.fetchall()
        except:
            rr = []
            print("Cannot get all sql data", sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())

        return rr

    def   rmone(self, uid):
        if self.config.debug > 1:
            print("removing one:", uid)
        try:
            self.cur.execute("delete from calendar where uid == ?", (uid,) )
            self.curr.commit()
            rr = self.cur.fetchone()
        except:
            print("Cannot delete sql data", sys.exc_info())
            self.errstr = "Cannot delete sql data" + str(sys.exc_info())
        if rr:
            return rr[1]
        else:
            return None

    # --------------------------------------------------------------------
    # Return None if no data

    def   rmall(self):
        if self.config.debug > 1:
            print("removing all")

        try:
            self.cur.execute("delete from calendar")
            self.curr.commit()
            rr = self.cur.fetchone()
        except:
            print("Cannot delete sql data", sys.exc_info())
            self.errstr = "Cannot delete sql data" + str(sys.exc_info())
        if rr:
            return rr[1]
        else:
            return None

    def   rmalldata(self):
        if self.config.debug > 1:
            print("removing all data")
        try:
            self.cur.execute("delete from caldata")
            self.curr.commit()
            rr = self.cur.fetchone()
        except:
            print("Cannot delete sql data", sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        if rr:
            return rr[1]
        else:
            return None

if __name__ == "__main__":
    print("This is a module file, use pycalgui.py")

# EOF
