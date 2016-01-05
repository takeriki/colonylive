"""
setup for GUI automation of VueScan

"""

import commands
import os
import time


def gui_setup():
    print "start to GUI position setting for VueScan."
    
    # window setting
    os.system("wmctrl -a terminal")
    os.system("wmctrl -r terminal -b remove,maximized_vert,maximized_horz")
    os.system("wmctrl -r terminal -e 1,400,100,600,500")

    msg = "move pointer to 'Input' tab, then hit enter"
    inputtab = _get_mouse_pos(msg)
    
    msg = "move pointer to 'Source' list, then hit enter"
    source = _get_mouse_pos(msg)

    msg = "move pointer to 'Mode' list, then hit enter"
    mode = _get_mouse_pos(msg)
    
    start_scan()
    msg = "move pointer to 'Abort' button, then hit enter"
    abort = _get_mouse_pos(msg)
    stop_scan(abort)
    print "Complete!"
    return [inputtab, source, mode, abort]


def start_scan():
    os.system("wmctrl -a VueScan")
    time.sleep(1)
    os.system("xte 'keydown Control_L'")
    os.system("xte 'key n'")
    os.system("xte 'keyup Control_L'")
    time.sleep(1)
    os.system("wmctrl -a terminal")


def stop_scan(abort):
    time.sleep(1)
    os.system("wmctrl -a VueScan")
    time.sleep(1)
    os.system("xte 'mousemove %s'" % abort)
    os.system("xte 'mouseclick 1'")
    time.sleep(1)
    os.system("wmctrl -a terminal")


def _get_mouse_pos(msg):
    os.system('clear')
    raw_input(msg)
    output = commands.getoutput("xmousepos")
    x,y,u,v = map(int,output.split())
    out = "%s %s" % (x, y)
    return out


if __name__ == "__main__":
    gui_setup()

