"""
Package version

"""

import pkg_resources

def get_version():
    return pkg_resources.require("colonylive")[0].version


if __name__ == "__main__":
    print get_version()
