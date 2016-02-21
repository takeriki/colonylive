#!/usr/bin/env python2
# -*- coding:utf-8 -*-


import datetime
import numpy as np

def get_html_scanstatus(scanners):
    html = "<table class='sample'>\n"
    for scanner in scanners:
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


def get_html_button(person_id, batchs):
    html = "<FORM action=/monitor method=POST>\n"
    html += "<table class='sample'>\n"
    
    for batch in batchs:
        action = "Start"
        print batch.id
        print batch.status
        if batch.status == "monitoring":
            action = "Cancel"
        html += "<tr><td>"
        html += "Batch %s -- " % batch.id
        html += "%s -- " % batch.project
        now = datetime.datetime.now()
        dt_fin = calc_dt_finish(now, batch.h_scan)
        dt_str = dt_fin.strftime("%m/%d %H:%M")
        html += "%d plates -- " % batch.num_plates
        html += "until %s </td>\n" % dt_str
        html += "<td><input type='submit' "
        html += "name='%s-%s' " % (action, batch.id)
        html += "value='%s'></td>\n" % action
        if action == "Cancel":
            html += "<td><input type='submit' "
            html += "name='Abort-%s' " % (batch.id)
            html += "value='Abort'></td>\n"
        html += "</tr>\n"
    html += "</table>\n"
    html += "</form>\n"
    return html


def calc_dt_finish(dt_start, h_scan):
    dt_hours = datetime.timedelta(hours=h_scan)
    dt_finish = dt_start + dt_hours
    return dt_finish


def get_html_booktable(batchs):
    if len(batchs) == 0:
        return ""
    html =  "<FORM action=/reg_manage method=POST>\n"
    html += "<table class='sample'>\n"
    html += "<tr>\n"
    html += "<th>ID</th>\n"
    html += "<th>Person</th>\n"
    html += "<th>Project</th>\n"
    html += "<th>Date</th>\n"
    html += "<th>Plates</th>\n"
    html += "<th>Remove</th>\n"
    html += "</tr>\n"

    for batch in batchs:
        dt_start = batch.dt_start 
        dt_finish = calc_dt_finish(batch.dt_start, batch.h_scan)
        dt_str =  dt_start.strftime("%m/%d %H") + "h - "
        dt_str += dt_finish.strftime("%m/%d %H") + "h"
        html += "<tr>\n"
        html += "<td>%d</td>\n" % batch.id
        html += "<td>%s</td>\n" % batch.person_name
        html += "<td>%s</td>\n" % batch.project 
        html += "<td>%s</td>\n" % dt_str
        html += "<td>%d plates</td>\n" % batch.num_plates
        html += "<td><button type='submit' "
        html += "name='batchid_rm' "
        html += "value='%s'>Remove</td></tr>\n" % batch.id
        html += "</form>\n"
    html += "</table>\n"
    html += "<br>\n"
    return html


def make_calender(batchs, sid2ary):
    sids = sid2ary.keys()
    day_shown = len(sid2ary[sids[0]])/24

    txt = ""
    fmt ="{0:8}"
    for i in range(24):
        fmt += " {%d:^3}" % (i+1)
    fmt +="\n"
    
    arys = sid2ary.values()
    ary = np.array(arys).reshape(len(sids),day_shown,24)
    for ind_day in range(day_shown):
        tmp = ["Day %d" % ind_day] + [i for i in range(1,25)]
        txt += fmt.format(*tmp)
        for ind_sid in range(len(sids)):
            sid = sids[ind_sid]
            tmp = ["%s)" % sid] + [str(int(i)) if i > 0 else '-' 
                for i in ary[ind_sid, ind_day, :]]
            txt += fmt.format(*tmp)
        txt += "\n"
    return txt


if __name__ == "__main__":
    print
