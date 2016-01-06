"""
setup for GUI automation of VueScan

"""

import commands
import os
import time

from clive.setup.auto_vuescan import gui_setup
from clive.core.conf import Configure
from clive.scan.prep import prep_gui
cfg = Configure()

prep_gui()
inputtab, source, mode, abort = gui_setup()

cfg[('vuescan','coordinate_inputtab')] = inputtab
cfg[('vuescan','coordinate_source')] = source
cfg[('vuescan','coordinate_mode')] = mode
cfg[('vuescan','coordinate_abort')] = abort
cfg.update()

