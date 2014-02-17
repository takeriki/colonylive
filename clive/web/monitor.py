#!/usr/bin/python

import sys
import datetime
import numpy as np

from clive.core.conf import Configure
from clive.db.handler import ScannerHandler

scanner_handler = ScannerHandler()

cfg = Configure()
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))


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


def get_status():
    scan_status = ScanStatus()
    return scan_status.make_table()

if __name__ == "__main__":
    argvs = sys.argv
    html = get_status()
    print html
