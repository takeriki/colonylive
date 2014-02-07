"""
Periodic scanning

"""

TEST_MODE = 1

import os
import time
import datetime

from clive.core.version import get_version
from clive.core.conf import Configure
from clive.io.imgio import ExpTmpImgIO, ScanImgIO

from clive.db.handler import ScannerHandler, ImgscanHandler, ImgHandler
from clive.db.manager import ExpManager
from gui_scan import gui_scan
from imgcrip import clip_scanimg

scanner_handler = ScannerHandler()
img_scan_handler = ImgscanHandler()
img_handler = ImgHandler()

cfg = Configure()
MIN_CYCLE = int(cfg[('scan','min_cycle')])
SCANNER_IDS = map(int,cfg[('scan','scanner_ids')].split(","))
VERSION = get_version()


# Loop
def keep_scan():
    if TEST_MODE:
        while True:
            print '[test-mode]'
            time.sleep(2)
            #time.sleep(10)
            run()
    while True:
        dt_now = datetime.datetime.now()
        min_wait = MIN_CYCLE - (dt_now.minute % MIN_CYCLE)
        sec_past = dt_now.second
        time.sleep(min_wait*60 - sec_past)
        run()


# Main program
def run():
    dt_now = datetime.datetime.now()
    dt_next = dt_now + datetime.timedelta(minutes=MIN_CYCLE)

    os.system('clear')
    print " cycle_scan.py     VERSION = " + VERSION
    print "---------------------------------------"
    print "DATE     : " + dt_now.strftime('%a, %d %b %Y')
    print "SCANNED  : " + dt_now.strftime('%H:%M')
    print "Next SCAN: " + dt_next.strftime('%H:%M')
    print 

    for sid in SCANNER_IDS:
        scanner = scanner_handler.load(sid)
        print "scanner%2d: " % int(scanner.id),

        # scan?
        if scanner.dt_finish == None:
            print "None"
            continue

        exp_ids = map(int, scanner.exp_ids.split("|"))

        # stop?
        if scanner.dt_finish < dt_now:
            print "Complete!!"
            tmpimgs = [ExpTmpImgIO(i) for i in exp_ids]
            for tmpimg in tmpimgs:
                tmpimg.push_folder()
            img_handler.create(
                exp_id, scanner.id, scanner.min_grows)
            expman = ExpManager(exp_id)
            expman.set_in_process(0)
            expman.set_step_done(1)
            scanner_handler.clean(scanner)
            continue
        
        # Perform scan
        print "%s; " % scanner.person_name,
        print "until %s " % scanner.dt_finish.strftime('%a, %d %b %Y'),
        img_scan = img_scan_handler.create(scanner.id, scanner.exp_ids)
        scanimg = ScanImgIO(img_scan.id)
        fail = gui_scan(scanner.id, scanimg.path)
        #fail = 0
        if fail:
            print "[Faild]"
            continue
        print "[Success]"
        
        # Registration
        if scanner.min_grows in [None, '']:
            min_grows = []
        else:
            min_grows = [i for i in scanner.min_grows.split("|")]
        min_grow = _get_min_grow(scanner, img_scan)
        min_grows += [min_grow]
        scanner.min_grows = "|".join(map(str, min_grows))
        scanner_handler.update()
    
        # Split image
        tmpimgs = [ExpTmpImgIO(i) for i in exp_ids]
        n_scan = len(min_grows) - 1
        path_outs = [i.get_path(n_scan) for i in tmpimgs]
        clip_scanimg(scanimg.path, path_outs)
    
    print
    print "DONE"


def _get_min_grow(scanner, img_scan):
    dt_scan = img_scan.dt_scan
    dif = dt_scan - scanner.dt_start
    min_grow = (dif.days * 86400 + dif.seconds) / 60
    return min_grow


def store_images(scanner):
    exp_ids = map(int, scanner.exp_ids.split("|"))
    for exp_id in exp_ids:
        store_tmp_images(exp_id)
        img_handler.create(
            exp_id, scanner.id, scanner.min_grows)
        expman = ExpManager(exp_id)
        expman.set_in_process(0)
        expman.set_step_done(1)


if __name__ == "__main__":
    keep_scan()

