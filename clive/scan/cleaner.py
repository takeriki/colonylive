"""
Keep reducing file number in the scan image folder

"""

import os
import time
import datetime
import glob

from clive.core.conf import Configure

cfg = Configure()
DAYS_KEEP = cfg[('scan','days_scan_keep')]
FOLDER_IMG_SCAN = cfg[('folder','img_scan')]


def keep_clean():
    while True:
        _rm_img_scan()
        _wait_to_next_sunday()


def _rm_img_scan():
    current_time = time.time()
    for fname in glob.glob(FOLDER_IMG_SCAN + '/*.tif'):
        ctime = os.path.getctime(fname)
        past_days = (current_time - ctime) / (60*60*24)
        if past_days >= DAYS_KEEP:
            os.remove(fname)


def _wait_to_next_sunday():
    dt = datetime.datetime.now()
    tsec_now = dt.hour * 3600 + dt.minute * 60 + dt.second
    tsec_day = 24 * 3600
    if dt.weekday == 6:
        days = 6
    else:
        days = 6 - dt.weekday()
    sec_wait = (days)*tsec_day - tsec_now
    time.sleep(sec_wait)

if __name__ == "__main__":
    keep_clean()
