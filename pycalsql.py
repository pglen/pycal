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
             (pri INTEGER PRIMARY KEY, keyx text, uid text, val text, val2 text, val3 text, val4 text)")
            self.cur.execute("create index if not exists kcalendar on calendar (keyx)")
            self.cur.execute("create index if not exists pcalendar on calendar (pri)")

            self.cur.execute("create table if not exists caldata \
             (pri INTEGER PRIMARY KEY, keyx text, val text, val2 text, val3 text)")
            self.cur.execute("create index if not exists kcaldata on caldata (keyx)")
            self.cur.execute("create index if not exists pcaldata on caldata (pri)")

            self.cur.execute("create table if not exists calala \
             (pri INTEGER PRIMARY KEY, keyx text, val text, val2 text, val3 text)")
            self.cur.execute("create index if not exists kcalala on calala (keyx)")
            self.cur.execute("create index if not exists pcalala on calala (pri)")

            self.cur.execute("PRAGMA synchronous=OFF")
            # Save (commit) the changes
            self.curr.commit()
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

        if self.config.debug > 2:
            print("Getting by keyx =", "'" + kkk + "'")
        try:
            #c = self.curr.cursor()
            self.cur.execute("select * from calendar where keyx like ?", (kkk,))
        except:
            #print("Cannot get sql for ", kkk, sys.exc_info())
            #pgutils.print_exception("cannot get")
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        try:
            rr = self.cur.fetchall()
        except:
             rr = None

        finally:
            #c.close
            pass
        if rr:
            return (rr)
        else:
            return None

    def   getdata(self, kkk, all = False):

        if self.config.debug > 2:
            print("Getting data by keyx =", "'" + kkk + "'")
        try:
            #c = self.curr.cursor()
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

        finally:
            #c.close
            pass

        if rr:
            if all:
                return (rr)
            return (rr[2], rr[3], rr[4])
        else:
            return ([], [], [])

    # --------------------------------------------------------------------
    # Return False if cannot put data

    def   put(self, keyx, uid, val, val2, val3, val4):

        #got_clock = time.clock()
        if self.config.debug > 1:
            print("putting:", keyx, uid, val, val2, val3, val4)

        #print("types", type(keyx), type(uid), type(val), type(val2), type(val3), type(val4))

        ret = True
        try:
            #c = self.curr.cursor()
            if os.name == "nt":
                self.cur.execute("select * from calendar where keyx == ?", (keyx,))
            else:
                self.cur.execute("select * from calendar indexed by kcalendar where keyx == ?", (keyx,))
            rr = self.cur.fetchall()
            if rr == []:
                #print ("inserting")
                self.cur.execute("insert into calendar (keyx, uid, val, val2, val3, val4) \
                    values (?, ?, ?, ?, ?, ?)", (keyx, uid, val, val2, val3, val4))
            else:
                #print ("updating")
                if os.name == "nt":
                    self.cur.execute("update calendar \
                                set uid = ? val = ? val2 = ?, val3 = ?, val4 = ? where keyx = ?", \
                                      (uid, val, val2, val3, val4, keyx))
                else:
                    self.cur.execute("update calendar indexed by kcalendar \
                                set uid = ?, val = ?, val2 = ?, val3 = ?, val4 = ? where keyx = ?",\
                                     (uid, val, val2, val3, val4, keyx))
            self.curr.commit()
        except:
            print("Cannot put sql ", sys.exc_info())
            pgutils.print_exception("put")
            self.errstr = "Cannot put sql " + str(sys.exc_info())
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
        if self.config.debug > 1:
            print("putting data:", keyx, val, val2, val3)

        #print("types", type(keyx), type(val), type(val2), type(val3))

        ret = True
        try:
            #c = self.curr.cursor()
            if os.name == "nt":
                self.cur.execute("select * from caldata where keyx == ?", (keyx,))
            else:
                self.cur.execute("select * from caldata indexed by kcaldata where keyx == ?", (keyx,))
            rr = self.cur.fetchall()
            if rr == []:
                #print "inserting"
                self.cur.execute("insert into caldata (keyx, val, val2, val3) \
                    values (?, ?, ?, ?)", (keyx, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.cur.execute("update caldata \
                                set val = ? val2 = ?, val3 = ? where keyx = ?", \
                                      (val, val2, val3, keyx))
                else:
                    self.cur.execute("update caldata indexed by kcaldata \
                                set val = ?, val2 = ?, val3 = ? where keyx = ?",\
                                     (val, val2, val3, keyx))
            self.curr.commit()
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

    def   putala(self, keyx, val, val2, val3):

        #got_clock = time.clock()
        if self.config.debug > 1:
            print("putala", keyx, val, val2, val3)

        ret = True
        try:
            #c = self.curr.cursor()
            if os.name == "nt":
                self.cur.execute("select * from calala where keyx == ?", (keyx,))
            else:
                self.cur.execute("select * from calala indexed by kcalala where keyx == ?", (keyx,))
            rr = self.cur.fetchall()
            if rr == []:
                #print "inserting"
                self.cur.execute("insert into caldata (keyx, val, val2, val3) \
                    values (?, ?, ?, ?)", (keyx, val, val2, val3))
            else:
                #print "updating"
                if os.name == "nt":
                    self.cur.execute("update caldata \
                                set val = ? val2 = ?, val3 = ? where keyx = ?", \
                                      (val, val2, val3, keyx))
                else:
                    self.cur.execute("update caldata indexed by kcaldata \
                                set val = ?, val2 = ?, val3 = ? where keyx = ?",\
                                     (val, val2, val3, keyx))
            self.curr.commit()
        except:
            print("Cannot put sql ala", sys.exc_info())
            self.errstr = "Cannot put sql ala" + str(sys.exc_info())
            ret = False
        finally:
            #c.close
            pass

        #self.take += time.clock() - got_clock

        return ret

    def   getala(self, keyx):

        #got_clock = time.clock()

        if self.config.debug > 1:
            print("Get ala by keyx =", "'" + kkk + "'")

        ret = []
        try:
            #c = self.curr.cursor()
            if os.name == "nt":
                self.cur.execute("select * from calala where keyx like ?", (keyx,))
            else:
                self.cur.execute("select * from calala indexed by kcalala where keyx like ?", (keyx,))
            ret = self.cur.fetchall()
        except:
            print("Cannot get sql ala", sys.exc_info())
            self.errstr = "Cannot get sql ala" + str(sys.exc_info())
        finally:
            #c.close
            pass

        #self.get += time.clock() - got_clock

        return ret

    # --------------------------------------------------------------------
    # Get All

    def   getall(self, strx = "", limit = 1000):

        if self.config.debug > 1:
            print("getall '" +  strx + "'")
        try:
            #c = self.curr.cursor()
            self.cur.execute("select * from calendar where val like ? or val2 like ? or val3 like ? limit  ?",
                                            (strx, strx, strx, limit))
            rr = self.cur.fetchall()
        except:
            rr = []
            print("Cannot get all sql data", sys.exc_info())
            self.errstr = "Cannot get sql data" + str(sys.exc_info())
        finally:
            #c.close
            pass

        return rr

    def   rmone(self, kkk):
        if self.config.debug > 1:
            print("removing one:", kkk)
        try:
            #c = self.curr.cursor()
            self.cur.execute("delete from calendar where keyx like ?", (kkk,) )
            rr = self.cur.fetchone()
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

    # --------------------------------------------------------------------
    # Return None if no data

    def   rmall(self):
        if self.config.debug > 1:
            print("removing all")

        try:
            #c = self.curr.cursor()
            self.cur.execute("delete from calendar")
            rr = self.cur.fetchone()
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
        if self.config.debug > 1:
            print("removing all data")
        try:
            #c = self.curr.cursor()
            self.cur.execute("delete from caldata")
            rr = self.cur.fetchone()
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
