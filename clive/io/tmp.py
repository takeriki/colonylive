"""
temporary directory, for image, web session...
"""

import os
import getpass


uname = getpass.getuser()
DIR_TMP = "/tmp/clive-%s" % (uname)

if not os.path.exists(DIR_TMP):
    os.system("mkdir %s") % DIR_TMP

