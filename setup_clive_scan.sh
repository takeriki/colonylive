#!/bin/bash


# auto mount
# -------------------
mkdir -p ~/img
mkdir -p ~/img_scan

sudo sh -c "cat << EOF >> /etc/fstab
biofserv1.naist.jp:/local/pcfiles/mori/Project/GeneticInteraction/img  /home/morilab/img    nfs4    defaults,auto 0 0
biofserv1.naist.jp:/local/pcfiles/mori/Project/GeneticInteraction/img_scan  /home/morilab/img_scan    nfs4    defaults,auto 0 0
EOF"


# auto start in Gnome 
# ------------------------
echo "creating config file..."

cat << EOF > /home/morilab/startup.sh
#!/bin/bash
vuescan &
sleep 20
gnome-terminal -e "/home/morilab/colonylive/clive_scan.py"
EOF
chmod +x /home/morilab/startup.sh

mkdir -p ~/.config/autostart
cat << EOF > ~/.config/autostart/gnome-terminal.desktop
[Desktop Entry]
Type=Application
Terminal=false
Exec=/home/morilab/startup.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[en_US]=gnome-terminal
Name=gnome-terminal
Comment[en_US]=
Comment=
EOF



# install Vuescan
# ------------------------
cd ~/
wget http://www.hamrick.com/files/vuex6495.tgz
tar xvf vuex6495.tgz
sudo ln -s /home/morilab/Vuescan/vuescan /usr/local/bin/vuescan


mkdir -p ~/.vuescan
cat << EOF > ~/.vuescan/colonylive-gtx970.ini
[VueScan]
[Input-File-Transparency]
Media=1
BitsPerPixel=2
Quality=4
ScanFromPreview=1
[Prefs-File-Transparency]
PrintedUnits=0
[Crop-GT-8700-Flatbed]
XSize=13571
YSize=18725
CropSize=1
AutoOffset=0
PreviewArea=4
[Color-GT-8700-Flatbed]
WhitePointRed=754
WhitePointGreen=754
WhitePointBlue=758
[Input-GT-8700-Flatbed]
PreviewResolution=7
BitsPerPixel=1
MediaSize=1
[Output-File-Transparency]
PrintedSize=11
[Input-File-Transparency8x10]
Quality=4
ScanResolution=6
BitsPerPixel=4
PreviewResolution=8
LockExposure=1
[Crop-File-Transparency8x10]
CropSize=1
AutoOffset=0
YSize=2368
ShowMultiOutline=0
[Color-File-Transparency8x10]
WhitePointRed=754
WhitePointGreen=755
WhitePointBlue=753
[Input-GT-X970-Transparency]
Media=1
Quality=4
BitsPerPixel=2
ScanFromPreview=1
[Output-GT-X970-Transparency]
PrintedSize=11
[Prefs-GT-X970-Transparency]
PrintedUnits=0
[Input-GT-X970-Transparency8x10]
Quality=4
ScanResolution=6
BitsPerPixel=4
PreviewResolution=8
LockExposure=1
[Crop-GT-X970-Transparency8x10]
CropSize=1
AutoOffset=0
ShowMultiOutline=0
YSize=2368
[Color-GT-X970-Transparency8x10]
WhitePointRed=754
WhitePointGreen=756
WhitePointBlue=753
[Output]
DefaultFolder=/home/riki/Desktop/scan_data
AutoFileName=0
TIFFFile=1
JPEGFile=0
TIFFFileName=/home/morilab/Desktop/scan_data/11819.tif
TIFFCompression=1
[Prefs]
ExternalViewer=0
ExternalEditor=0
WindowMaximized=1
GuidedMode=0
Options=1
WarnOnOverwrite=0
EnablePopupTips=0
EnableSampleImages=0
StartupTip=0
WindowXSize=1022
WindowYSize=688
EnableSpinButtons=0
WindowXOffset=353
WindowYOffset=257
[Crop-GT-X970-Flatbed]
XSize=3585
YSize=54414
XOffset=448
YOffset=576
PreviewXSize=39685
PreviewYSize=56125
[Color-GT-X970-Flatbed]
WhitePointRed=44
WhitePointGreen=43
WhitePointBlue=42
[Output-GT-X970-Transparency8x10]
PrintedSize=0
TIFFFile=1
JPEGFile=0
[Output-File-Transparency8x10]
PrintedSize=0
[Input-GT-X970]
Mode=2
[Output-GT-X970-\(null\)]
TIFFFile=1
JPEGFile=0
EOF

echo "DONE"


# install required programs
# ------------------------
sudo apt-get update
sudo apt-get -y install vim mysql-client zip
sudo apt-get -y install openssh-server ntpdate xautomation wmctrl 
sudo apt-get -y install python-numpy python-mysqldb python-opencv


echo "Done"
echo "Please reboot"
