"""
GUI preparation for GUI scan

"""

import commands
import os
import time

terminal = "terminal"

def prep_gui():
    # disable lock
    os.system("gsettings set org.gnome.desktop.screensaver lock-enabled false")

    os.system("wmctrl -r :ACTIVE: -N '%s'" % terminal)

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
    
    os.system("wmctrl -a %s" % terminal)
    os.system("wmctrl -r %s -b remove,maximized_vert,maximized_horz" % terminal)
    os.system("wmctrl -r %s -e 1,000,000,400,800" % terminal)
    

def check_vuescan():
    output = commands.getoutput("wmctrl -l")
    for line in output.split('\n'):
        if line.find('VueScan') != -1:
            return 1
    return 0


def back_to_terminal():
    # Just in case, escape from save window
    os.system("xte 'key Escape'")
    # Focus to terminal window
    os.system("wmctrl -a %s" % terminal)
    return


if __name__ == "__main__":
    prep_gui()

