"""
setup for GUI automation of VueScan

"""

import commands
import os
import time

from clive.core.conf import Configure
cfg = Configure()

def gui_setup():
    print "start to GUI position setting for VueScan."
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
    
    # window setting
    os.system("wmctrl -a terminal")
    os.system("wmctrl -r terminal -b remove,maximized_vert,maximized_horz")
    os.system("wmctrl -r terminal -e 1,400,100,600,500")

    msg = "move pointer to 'Input' tab, then hit enter"
    cfg[('vuescan','pos_input_tab')] = _get_mouse_pos(msg)
    
    msg = "move pointer to 'Source' list, then hit enter"
    cfg[('vuescan','pos_source')] = _get_mouse_pos(msg)

    msg = "move pointer to 'Mode' list, then hit enter"
    cfg[('vuescan','pos_mode')] = _get_mouse_pos(msg)
    
    start_scan()
    msg = "move pointer to 'Abort' button, then hit enter"
    cfg[('vuescan','pos_abort')] = _get_mouse_pos(msg)
    stop_scan()
    
    cfg.update()
    print "Complete!"


def start_scan():
    os.system("wmctrl -a VueScan")
    time.sleep(1)
    os.system("xte 'keydown Control_L'")
    os.system("xte 'key n'")
    os.system("xte 'keyup Control_L'")
    time.sleep(1)
    os.system("wmctrl -a terminal")


def stop_scan():
    time.sleep(1)
    os.system("wmctrl -a VueScan")
    time.sleep(1)
    os.system("xte 'mousemove %s'" % cfg[('vuescan','pos_abort')])
    os.system("xte 'mouseclick 1'")
    time.sleep(1)
    os.system("wmctrl -a terminal")


def check_vuescan():
    output = commands.getoutput("wmctrl -l")
    for line in output.split('\n'):
        if line.find('VueScan') != -1:
            return 1
    return 0


def _get_mouse_pos(msg):
    os.system('clear')
    raw_input(msg)
    output = commands.getoutput("xmousepos")
    x,y,u,v = map(int,output.split())
    out = "%s %s" % (x, y)
    return out


if __name__ == "__main__":
    gui_setup()

