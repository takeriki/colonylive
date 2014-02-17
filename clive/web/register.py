#!/usr/bin/python
#

import os
import csv
import sys
import datetime
import time
import numpy as np

import send_mail

from clive.core.conf import Configure
from clive.db.handler import ExpHandler, PersonHandler
from scheduler import ScheduleManager

exp_handler = ExpHandler()
person_handler = PersonHandler()
schedule_manager = ScheduleManager()

cfg = Configure()
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))


def make_reservation(values):
    # decode input
    try:
        person_id, project, dt_start, plate_ids, medium, h_scan, conditions\
            = decode_order(values)
    except:
        return error_msg(['Wrong input.'])

    # reserve scanner
    n_plates = len(plate_ids)
    scanposs = schedule_manager.reserve(
        SCANNER_IDS, dt_start, h_scan, n_plates)
    if len(scanposs) == 0:
        return error_msg(['No space.'])
   
    # record experiment info
    exps = []
    for plate_id, condition, scanpos in zip(plate_ids, conditions, scanposs):
        exp = exp_handler.create(person_id, project, plate_id, medium, dt_start, condition, h_scan, scanpos)
        exps += [exp]

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


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) != 9:
        quit("usage: %s [person_id] [project] [dt_start] [plate_ids] [medium] [h_scan] [conditions_key] [conditions_value]" % argvs[0])
    values = argvs[1:]
    print make_reservation(values)

