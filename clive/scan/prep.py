"""
GUI preparation for GUI scan

"""

import commands
import os
import time


def prep_gui():
    if check_vuescan():
        print "Running VueScan: OK"
    else:
        try:
            os.system("vuescan &")
            time.sleep(5)
            # window setting
            os.system("wmctrl -r VueScan -b add,maximized_vert,maximized_horz")
        except:
            print "Cannot run VueScan"
            quit()
    
    os.system("wmctrl -a terminal")
    os.system("wmctrl -r terminal -b remove,maximized_vert,maximized_horz")
    os.system("wmctrl -r terminal -e 1,000,000,400,600")
    

def check_vuescan():
    output = commands.getoutput("wmctrl -l")
    for line in output.split('\n'):
        if line.find('VueScan') != -1:
            return 1
    return 0


if __name__ == "__main__":
    prep_gui()

