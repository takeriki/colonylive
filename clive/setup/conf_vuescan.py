"""
make configuration file of VueScan

"""

from os.path import expanduser

def make_conf():
    home = expanduser("~")
    fpath = home + '/.vuescan/vuescan.ini'
    
    f = open(fpath,'wb')
    f.write(conf)
    f.close()

conf = """[VueScan]
[Input-GT-X970]
Mode=2
[Input-GT-X970-Transparency8x10]
PreviewResolution=8
ScanResolution=6
LockExposure=1
[Output-GT-X970-Transparency8x10]
TIFFFile=1
JPEGFile=0
[Crop-GT-X970-Transparency8x10]
CropSize=1
AutoOffset=0
ShowMultiOutline=0
[Prefs]
StartupTip=0
WindowMaximized=1
WindowXOffset=0
WindowYOffset=27
WindowXSize=1728
WindowYSize=1080
GuidedMode=0
ExternalViewer=0
ExternalEditor=0
Options=1
[Output]
AutoFileName=0"""


if __name__ == "__main__":
    make_conf()

