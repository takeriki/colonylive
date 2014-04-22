"""
automatic GUI operation for VueScan

"""

import commands
import os
import time
import sys
import subprocess as sp

from clive.core.conf import Configure
from prep import back_to_terminal
cfg = Configure()

POS_INPUT_TAB = cfg[('vuescan','pos_input_tab')]
POS_SOURCE = cfg[('vuescan','pos_source')]
POS_MODE = cfg[('vuescan','pos_mode')]
POS_ABORT = cfg[('vuescan','pos_abort')]
SEC_WAIT_LIMIT = int(cfg[('vuescan','sec_scan_wait')])


def gui_scan(scanner, fname):
    fname = fname.replace(".tif","")
    initialize()
    start_scan(scanner)
    no_window = wait_scanned_window()
    if no_window:
        treat_timeout(scanner, fname)    
        turn_off_head_light()
        return 1
    save_scanned_pict(fname)
    turn_off_head_light()
    back_to_terminal()
    return 0


def wait_scanned_window():
    i = 0
    while True:
        # print i
        if SEC_WAIT_LIMIT < i:
            print 'timeout'
            return 1 
        output = commands.getoutput("wmctrl -l")
        for line in output.split('\n'):
            if line.find("Choose the TIFF file name") > -1:
                return 0
        i += 1
        time.sleep(1)


def initialize():
    os.system("export DISPLAY=':0.0'")
    # Focus to Vuescan window
    os.system("wmctrl -a VueScan")
    time.sleep(1)

    os.system("xte 'keydown Alt_L'")
    os.system("xte 'key f'")
    os.system("xte 'keyup Alt_L'")
    time.sleep(1)
    os.system("xte 'key l'")
    time.sleep(2)
    os.system("xte 'key Return'")
    time.sleep(5)
    

def start_scan(scanner):
    # Move to input setting
    os.system("xte 'mousemove %s'" % POS_INPUT_TAB)
    os.system("xte 'mouseclick 1'")
    
    # select scanner
    os.system("xte 'mousemove %s'" % POS_SOURCE)
    os.system("xte 'mouseclick 1'")
    time.sleep(2)

    i = 1 
    while i < scanner:
        os.system("xte 'key Down'")
        time.sleep(0.5)
        i += 1
    os.system("xte 'key Return'")
    time.sleep(8)

    # scan  
    os.system("xte 'keydown Control_L'")
    os.system("xte 'key n'")
    os.system("xte 'keyup Control_L'")
    return 


def save_scanned_pict(fname):
    # Save image file
    os.system("xte 'keydown Control_L'")
    os.system("xte 'key a'")
    os.system("xte 'keyup Control_L'")
    time.sleep(0.3)
    os.system("xte 'key Delete'")
    time.sleep(0.3)

    os.system("xte 'str %s'" % fname)
    os.system("xte 'key Return'")
    time.sleep(8)
    return


def turn_off_head_light():
    os.system("xte 'mousemove %s'" % POS_MODE)
    os.system("xte 'mouseclick 1'")
    time.sleep(2)
    os.system("xte 'key Up'")
    time.sleep(0.5)
    os.system("xte 'key Up'")
    os.system("xte 'key Return'")
    time.sleep(4)

    os.system("xte 'keydown Control_L'")
    os.system("xte 'key i'")
    os.system("xte 'keyup Control_L'")
    time.sleep(3)
    os.system("xte 'mousemove %s'" % POS_ABORT)
    time.sleep(1)
    os.system("xte 'mouseclick 1'")
    time.sleep(5)
    return


def treat_timeout(scanner, fname):
    os.system("xte 'mousemove %s'" % POS_ABORT)
    os.system("xte 'mouseclick 1'")
    error_msg = "timeout, scanner=%s, out=%s" % (scanner, fname)
    f = open('error.log', 'a')
    f.write(error_msg + '\n')
    f.close()
    return


if __name__ == "__main__":
    gui_scan(1,'test.tif')

