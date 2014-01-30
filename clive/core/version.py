"""
Package version

"""

import pkg_resources

def get_version():
    return pkg_resources.require("clive")[0].version
