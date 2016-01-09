#!/usr/bin/python
#

import csv
import sys
import datetime
import numpy as np

#import send_mail

from schema import Exp


def make_reservation(batch, sid2ary, pairs):
    # reserve scanner
    scanposs = reserve(sid2ary, batch)
    if len(scanposs) == 0:
        return "No space."

    # record experiment info
    tmp = []
    for ((conditions, plate_id), scanpos) in zip(pairs, scanposs):
        exp = Exp()
        exp.set_maxid()
        exp.batch_id = batch.id
        exp.person_id = batch.person_id
        exp.project = batch.project
        exp.medium = batch.medium
        exp.dt_start = batch.dt_start
        exp.h_scan = batch.h_scan
        exp.plate_id = plate_id
        exp.conditions = conditions
        exp.pos_scan = scanpos
        exp.insert() 
        tmp += [(scanpos, exp.id)]

    pos2exp_id = "|".join(["%s:%s" % (i[0],i[1]) for i in tmp])
    batch.pos2exp_id = pos2exp_id
    batch.insert()
    
    """
    # make csv table, then report 
    dt_now = datetime.datetime.now()
    fname = "/tmp/exp-%s.csv" % (dt_now.strftime('%Y%m%d'))
    write_csv_table(fname, exps)
    time.sleep(1)
    report_by_email(person_id, fname)
    cmd = "rm %s" % fname
    os.system(cmd) 
    """ 
    return 0


def get_total_hour(td): 
    return (td.seconds + td.days * 24 * 3600)/3600


def calc_inds(dt_sf):
    dt_start, dt_finish = dt_sf
    dt_now = datetime.datetime.now()
    dt_today = datetime.datetime(
        dt_now.year, dt_now.month, dt_now.day)
    sind = get_total_hour(dt_start - dt_today) 
    find = get_total_hour(dt_finish - dt_today)
    if sind < 0: sind = 0
    if find < 0: find = 0
    return sind, find

def calc_dt_sf(dt_start, h_scan):
    dt_hours = datetime.timedelta(hours=int(h_scan))
    dt_finish = dt_start + dt_hours
    dt_sf = (dt_start, dt_finish)
    return dt_sf

def get_available_poss(dt_sf, sid, ary):
    sind, find = calc_inds(dt_sf)
    res = [1 for i in ary[sind:find] if i > 0]
    if sum(res) > 0:
        return []
    scanposs = []
    for pos in [1,2,3,4]:
        scanpos = "%d-%d" % (sid, pos)
        scanposs += [scanpos]
    return scanposs


def reserve(sid2ary, batch):
    dt_sf = calc_dt_sf(batch.dt_start, batch.h_scan)
    scanposs = []
    tmp = []
    for sid in sid2ary.keys():
        ary = sid2ary[sid]
        tmp += get_available_poss(dt_sf, sid, ary)
        if batch.num_plates <= len(tmp):
            scanposs = tmp[:batch.num_plates]
            break
    return scanposs


def make_sid2ary(batchs, SCANNER_IDS, day_schedule):
    sid2ary = {}   
    for sid in SCANNER_IDS:
        sid2ary[sid] = np.zeros(24*day_schedule)
    
    for batch in batchs:
        dt_sf = calc_dt_sf(batch.dt_start, batch.h_scan)
        sind, find = calc_inds(dt_sf)
        sids = map(int, [i.split(":")[0].split("-")[0] for i in batch.pos2exp_id.split("|")])
        sids = sorted(list(set(sids)))
        for sid in sids:
            sid2ary[sid][sind:find] = batch.id
    return sid2ary


def write_csv_table(fname, exps):
    w = csv.writer(open(fname, 'wb'))
    w.writerow(['ExpID','Project','PlateID','Conditions','Datetime','ScannerID','Position'])
    
    exp = exps[0]
    dt_start = exp.dt_start
    dt_hours = datetime.timedelta(hours=exp.h_scan)
    dt_finish = exp.dt_start + dt_hours
    dt_sf = (dt_start, dt_finish)
    dt_str =  dt_start.strftime("%Y/%m/%d %H") + "h - "
    dt_str += dt_finish.strftime("%Y/%m/%d %H") + "h"
    for exp in exps:
        sid, pos = exp.pos_scan.split("-")
        out= [exp.id, exp.project, exp.plate_id, exp.conditions, dt_str, sid, pos]
        w.writerow(out)


def report_by_email(person_id, fname):
    name = person_handler.get_name(person_id)
    email = person_handler.get_email(person_id)
    body = "To %s,\n\n" % name
    body += "Here is your registration information (attaced excel file).\n"
    body += "Please keep this file. You need Exp ID for further analysis.\n"
    send_mail.send_mail('Colony-live', email,'Registration information',body,fname)


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 9:
        quit("usage: %s [person_id] [project] [dt_start] [plate_ids] [medium] [h_scan] [conditions_key] [conditions_value]" % argvs[0])
    values = argvs[1:]
    print make_reservation(values)

