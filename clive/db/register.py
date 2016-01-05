#!/usr/bin/python
#

import os
import csv
import sys
import datetime
import time
import numpy as np

#import send_mail

from database import Database
from schema import Batch


def make_reservation(values, sid2ary, batchs):
    # decode input
    person_id, project, dt_start, plate_ids, medium, h_scan, conditions\
        = decode_order(values)
    try:
        person_id, project, dt_start, plate_ids, medium, h_scan, conditions\
            = decode_order(values)
    except:
        return error_msg(['Wrong input.'])

    # reserve scanner
    n_plates = len(plate_ids)
    #scanposs = schedule_manager.reserve(
    scanposs = reserve(
        sid2ary, batchs, dt_start, h_scan, n_plates)
    if len(scanposs) == 0:
        return error_msg(['No space.'])

   
    # record experiment info
    db = Database()
    batchid = int(db.get_maxid("batch")) + 1
    itemvalues = [
                ("id", batchid),
                ("project", project),
                ("person_id", person_id),
                ("num_plates", n_plates),
                ("dt_start", dt_start),
                ("h_scan", h_scan)]
    db.insert("batch", itemvalues)

    tmp = []
    for plate_id, condition, scanpos in zip(plate_ids, conditions, scanposs):
        expid = int(db.get_maxid("exp")) + 1
        itemvalues = [
                ("id", expid),
                ("batch_id", batchid),
                ("person_id", person_id),
                ("project", project),
                ("plate_id", plate_id),
                ("medium", medium),
                ("dt_start", dt_start),
                ("conditions", condition),
                ("h_scan", h_scan),
                ("pos_scan", scanpos)]
        db.insert("exp", itemvalues)
        tmp += [(scanpos, expid)]

    pos2exp_id = "|".join(["%s:%s" % (i[0],i[1]) for i in tmp])
    batch = Batch(batchid)
    batch.pos2exp_id = pos2exp_id
    batch.update()
    return "<h2>Success!!</h2>\n"

    # make csv table, then report 
    dt_now = datetime.datetime.now()
    fname = "/tmp/exp-%s.csv" % (dt_now.strftime('%Y%m%d'))
    write_csv_table(fname, exps)
    time.sleep(1)
    report_by_email(person_id, fname)
    cmd = "rm %s" % fname
    os.system(cmd) 
    
    return "<h2>Success!!</h2>\n"

def error_msg(msgs):
    html = "<span style='color:#FF0000'>\n"
    html += "<h2>Error</h2>\n"
    for msg in msgs:
        html += msg + "\n"
    html += "</span>\n"
    return html


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


def decode_order(values):
    person_id = int(values[0])
    project = values[1]
    dt_plan = datetime.datetime.strptime(values[2], '%Y-%m-%d-%H')
    dt_h = datetime.timedelta(hours=1)
    if dt_plan < datetime.datetime.now()-dt_h:
        quit_with_msgs(["Datetime shold be in the future"])
        quit_with_msgs(["Datetime shold be in the future"])
    plate_ids = [int(i) for i in values[3].split(",") if i != ""]
    medium = values[4]
    h_scan = int(values[5])
    keys = [i for i in values[6].split("|") if i != ""]
    tmps = values[7].split("|")
    valss = []
    for tmp in tmps:
        valss += [[i for i in tmp.split(",") if i != ""]]
    num_c = len(keys)
    num_p = len(plate_ids)
    conditions = []
    for p in range(num_p):
        vfmts = []
        for c in range(num_c):
            key = keys[c]
            value = valss[c][p]
            vfmt = "%s=%s" % (key, value)
            vfmts += [vfmt]
        conditions += ["|".join(vfmts)]
    return person_id, project, dt_plan, plate_ids, medium, h_scan, conditions



def report_by_email(person_id, fname):
    name = person_handler.get_name(person_id)
    email = person_handler.get_email(person_id)
    body = "To %s,\n\n" % name
    body += "Here is your registration information (attaced excel file).\n"
    body += "Please keep this file. You need Exp ID for further analysis.\n"
    send_mail.send_mail('Colony-live', email,'Registration information',body,fname)


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
    dt_hours = datetime.timedelta(hours=h_scan)
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


def reserve(sid2ary, batchs, dt_start, h_scan, n_plates):
    dt_sf = calc_dt_sf(dt_start, h_scan)
    scanposs = []
    tmp = []
    for sid in sid2ary.keys():
        ary = sid2ary[sid]
        tmp += get_available_poss(dt_sf, sid, ary)
        if n_plates <= len(tmp):
            scanposs = tmp[:n_plates]
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


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 9:
        quit("usage: %s [person_id] [project] [dt_start] [plate_ids] [medium] [h_scan] [conditions_key] [conditions_value]" % argvs[0])
    values = argvs[1:]
    print make_reservation(values)

