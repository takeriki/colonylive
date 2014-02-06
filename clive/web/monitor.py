#!/usr/bin/python

import sys
import datetime
import numpy as np

from clive.core.conf import Configure
from clive.db.handler import ScannerHandler, ExpHandler, PersonHandler
from scheduler import ScheduleManager

scanner_handler = ScannerHandler()
exp_handler = ExpHandler()
person_handler = PersonHandler()
schedule_manager = ScheduleManager()

cfg = Configure()
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))
HOUR_GAP = 3
DAYS_SCHEDULE = 14


class ScanOrder():
    def __init__(self, action):
        self.action = action
        self.dt_fs2exps = {}
        if action == "start":
            self.in_process = 0
        elif action == "abort":
            self.in_process = 1

    def update(self, person_id):
        # get planned exps
        dt_now = datetime.datetime.now()
        dt_gap = datetime.timedelta(hours=HOUR_GAP)
        exps = exp_handler.get_reserved_exps()
        
        if self.action == "start":
            exps_pick = [i for i in exps if 
                i.person_id == person_id 
                and i.step_done == 0
                and i.dt_start > (dt_now - dt_gap)
                and i.dt_start < (dt_now + dt_gap)
                and i.in_process==self.in_process]
        if self.action == "abort":
            exps_pick = [i for i in exps if 
                i.person_id==person_id 
                and i.step_done == 0
                and i.in_process==self.in_process]
        self._make_orders(exps_pick)
        
    def _make_orders(self, exps):
        dt_sfs = set([])
        self.dt_sf2exps = {}
        self.dt_sf2ind = {}
        self.ind2dt_sf = {}
        ind = 1
        for exp in exps:
            dt_sf = self._calc_dt_sf(exp.dt_start, exp.h_scan)
            if dt_sf not in dt_sfs:
                dt_sfs.add(dt_sf)
                self.dt_sf2exps[dt_sf] = []
                self.dt_sf2ind[dt_sf] = ind
                self.ind2dt_sf[ind] = dt_sf
                ind += 1
            self.dt_sf2exps[dt_sf] += [exp]
    
    def _calc_dt_sf(self, dt_start, h_scan):
        dt_hours = datetime.timedelta(hours=h_scan)
        dt_finish = dt_start + dt_hours
        dt_sf = (dt_start, dt_finish)
        return dt_sf
    
    def make_button(self, person_id):
        self.update(person_id)
        html = "<FORM action=/monitor method=POST>\n"
        html += "<table class='sample'>\n"
        for dt_sf, exps in self.dt_sf2exps.items():
            ind = self.dt_sf2ind[dt_sf]
            h_plan = int(dt_sf[0].strftime('%H'))
            html += "<tr><td>Planned time: %d h (%d plates)</td>\n" % (h_plan, len(exps))
            html += "<td><input type='submit' name='%s-%s' value='%s'></td></tr>\n" % (self.action, ind, self.action)
        html += "</table>\n"
        html += "</form>\n"
        return html

    def _make_sid2exps(self, exps):
        dt_now = datetime.datetime.now()
        h_scan = exps[0].h_scan
        dt_end = dt_now + datetime.timedelta(hours=h_scan)
        
        ds = []
        sids = set([])
        sid2exps = {}
        for exp in exps:
            sid, pid = map(int,exp.pos_scan.split("-"))
            ds += [(sid, pid, exp)]
        ds.sort(key=lambda x:(x[0],x[1]))
        for sid, pid, exp in ds:
            if sid not in sids:
                sids.add(sid)
                sid2exps[sid] = []
            sid2exps[sid] += [exp] 
        return sid2exps

    def submit(self, ind):
        dt_sf = self.ind2dt_sf[ind]
        exps = self.dt_sf2exps[dt_sf]
        dt_now = datetime.datetime.now()
        dt_start = dt_now
        h_scan = exps[0].h_scan
        dt_measure = datetime.timedelta(hours=h_scan)
        dt_finish = dt_start + dt_measure
        person_id = exps[0].person_id
        person_name = person_handler.get_name(person_id)
        
        sid2exps = self._make_sid2exps(exps)
        for sid, exps in sid2exps.items():
            scanner = scanner_handler.load(sid)
            # scanner
            if self.action == "start":
                tmp = [i.id for i in exps]
                exp_ids = "|".join(map(str,tmp))
                scanner.person_name = person_name
                scanner.dt_start = dt_start
                scanner.dt_finish = dt_finish
                scanner.exp_ids = exp_ids
                scanner_handler.update()
                in_process = 1
            if self.action == "abort":
                scanner_handler.clean(scanner)
                in_process = 0

            # exp
            for exp in exps:
                exp.dt_start = dt_start
                exp.in_process = in_process
            exp_handler.update()


class ScanStatus():
    def __init__(self):
        self.scanners = [''] * len(SCANNER_IDS)

    def update(self):
        for i, sid in enumerate(SCANNER_IDS):
            self.scanners[i] = scanner_handler.load(sid)
   
    def make_table(self):
        self.update()
        html = "<table class='sample'>\n"
        for scanner in self.scanners:
            
            if scanner.dt_finish == None:
                color = 'blue'
                status = 'Ready to use'
            else:
                name = scanner.person_name
                dt_finish = scanner.dt_finish
                color = 'red'
                status = 'Running: [%s] until %s' % (
                    name,
                    dt_finish.strftime('%m/%d %H:%M')
                    )

            res = "<span style='color:%s'>%s</span>" % (color, status)
            html += "<tr><td>Scanner %s</td><td>%s</td></tr>\n" % (scanner.id, res)
        html += '</table>\n'
        return html


def main(person_id):
    scan_status = ScanStatus()
    print scan_status.make_table()
    
    scan_start = ScanOrder('start')
    print scan_start.make_button(person_id)
    
    scan_abort = ScanOrder('abort')
    print scan_abort.make_button(person_id)


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 2:
        quit("usage: %s [person_id]" % argvs[0])
    person_id = int(argvs[1])
    main(person_id)
