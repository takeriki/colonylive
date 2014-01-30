#!/usr/bin/python

import sys
import datetime
import numpy as np

from clive.core.conf import Configure
from clive.db.handler import ScannerHandler, ExpHandler, PersonHandler

scanner_handler = ScannerHandler()
exp_handler = ExpHandler()
person_handler = PersonHandler()

cfg = Configure()
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))
POSS_SCAN = map(int,cfg[('scan','pos_scan')].split(","))
DAYS_SCHEDULE = 14


def get_total_hour(td): 
    return (td.seconds + td.days * 24 * 3600)/3600


class ScanSchedule():
    def __init__(self, scanner_id):
        self.scanner_id = scanner_id
        self.ary = np.zeros(24*DAYS_SCHEDULE)

    def update(self, dt_sf, ind):
        sind, find = self._calc_inds(dt_sf)
        self.ary[sind:find] = ind
        
    def get_available_poss(self, dt_sf):
        sind, find = self._calc_inds(dt_sf)
        res = [1 for i in self.ary[sind:find] if i > 0]
        if sum(res) > 0:
            return []
        scanposs = []
        for pos in POSS_SCAN:
            scanpos = "%d-%d" % (self.scanner_id, pos)
            scanposs += [scanpos]
        return scanposs

    def _calc_inds(self, dt_sf):
        dt_start, dt_finish = dt_sf
        dt_now = datetime.datetime.now()
        dt_today = datetime.datetime(
            dt_now.year, dt_now.month, dt_now.day)
        sind = get_total_hour(dt_start - dt_today) 
        find = get_total_hour(dt_finish - dt_today) 
        if sind < 0: sind = 0
        if find < 0: find = 0
        return sind, find

    def check(self):
        scanposs_available = []

        for sid in SCANNER_IDS:
            scanner = Scanner(sid, self.exps[0])
            scanner.update()
            scanposs_available += scanner.reserve()

        if len(scanposs_available) < len(self.exps):
            msgs = ["Scanner is occupied."]
            quit_with_msgs(msgs)

        for i, exp in enumerate(self.exps):
            exp.scanpos = scanposs_available[i]


class ScheduleManager():
    sid2schedule = {}

    def __init__(self):
        for sid in SCANNER_IDS:
            schedule = ScanSchedule(sid)
            self.sid2schedule[sid] = schedule
        self.reload()

    def reload(self):
        for sid in SCANNER_IDS:
            schedule = ScanSchedule(sid)
            self.sid2schedule[sid] = schedule
        exps = exp_handler.get_reserved_exps()
        self._analyze(exps)
    
    def _analyze(self, exps):
        self.dt_sfs = set([])
        self.dt_sf2exps = {}
        self.ind2dt_sf = {}
        self.dt_sf2ind = {}
        ind = 1
        for exp in exps:
            sid, pos = map(int,exp.pos_scan.split("-"))
            if sid not in SCANNER_IDS:
                continue
            
            dt_sf = self._calc_dt_sf(exp.dt_start, exp.h_scan)
            if dt_sf not in self.dt_sfs:
                self.dt_sfs.add(dt_sf)
                self.dt_sf2exps[dt_sf] = []
                self.ind2dt_sf[ind] = dt_sf
                self.dt_sf2ind[dt_sf] = ind
                ind += 1

            self.dt_sf2exps[dt_sf] += [exp]
            if pos == 1:
                self.sid2schedule[sid].update(dt_sf, self.dt_sf2ind[dt_sf])

    def make_table(self):
        if len(self.ind2dt_sf.items()) == 0:
            return ""
        txt = "<table class='sample'>\n"
        txt += "<tr>\n"
        txt += "<th>ID</th>\n"
        txt += "<th>Person</th>\n"
        txt += "<th>Project</th>\n"
        txt += "<th>Date</th>\n"
        txt += "<th>Plates</th>\n"
        txt += "</tr>\n"

        for ind, dt_sf in self.ind2dt_sf.items():
            exps = self.dt_sf2exps[dt_sf]
            dt_str =  dt_sf[0].strftime("%m/%d %H") + "h - "
            dt_str += dt_sf[1].strftime("%m/%d %H") + "h"
            pname = person_handler.get_name(exps[0].person_id)
            txt += "<tr>\n"
            txt += "<td>%d</td>\n" % ind
            txt += "<td>%s</td>\n" % pname
            txt += "<td>%s</td>\n" % exps[0].project 
            txt += "<td>%s</td>\n" % dt_str
            txt += "<td>%d plates</td>\n" % len(exps)
        txt += "</table>\n"
        txt += "<br>\n"
        return txt

    def make_calender(self):
        txt = ""
        
        fmt ="{0:8}"
        for i in range(24):
            fmt += " {%d:^3}" % (i+1)
        fmt +="\n"
        
        n_scanner = len(SCANNER_IDS)
        arys = [self.sid2schedule[sid].ary for sid in SCANNER_IDS]
        ary = np.array(arys).reshape(n_scanner,DAYS_SCHEDULE,24)
        for ind_day in range(DAYS_SCHEDULE):
            tmp = ["Day %d" % ind_day] + [i for i in range(1,25)]
            txt += fmt.format(*tmp)
            for ind_sid in range(n_scanner):
                sid = SCANNER_IDS[ind_sid]
                tmp = ["%s)" % sid] + [str(int(i)) if i > 0 else '-' 
                    for i in ary[ind_sid, ind_day, :]]
                txt += fmt.format(*tmp)
            txt += "\n"
        return txt

    
    def cancel(self, ind):
        dt_sf = self.ind2dt_sf[ind]
        exps = self.dt_sf2exps[dt_sf]
        for exp in exps:
            exp_handler.remove(exp)            
        self.reload()

     
    def reserve(self, scanner_ids_use, dt_start, h_scan, n_plates):
        dt_sf = self._calc_dt_sf(dt_start, h_scan)
        scanposs = []
        tmp = []
        for sid in scanner_ids_use:
            schedule = self.sid2schedule[sid]
            tmp += schedule.get_available_poss(dt_sf)
            if n_plates <= len(tmp):
                scanposs = tmp[:n_plates]
                break
        return scanposs


    def _calc_dt_sf(self, dt_start, h_scan):
        dt_hours = datetime.timedelta(hours=h_scan)
        dt_finish = dt_start + dt_hours
        dt_sf = (dt_start, dt_finish)
        return dt_sf


def main(ptype):
    schedule_manager = ScheduleManager()
    if ptype == "table":
        print schedule_manager.make_table()
    if ptype == "calender":
        print schedule_manager.make_calender()


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 2:
        quit("usage: %s ['table' or 'calender']" % argvs[0])
    ptype = argvs[1]
    main(ptype)
