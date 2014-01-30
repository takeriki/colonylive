#!/usr/bin/python2

import wx
import math
import csv
import numpy as np

nrow = 32 
ncol = 48


def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result


class DrawPanel(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent)
        self.moveflag = False
        self.ind = 0
        self.rad = 0
        self.xyi = (0,0)
        self.xyspan = (0,0)
        self.xary = np.zeros((ncol,nrow))
        self.yary = np.zeros((ncol,nrow))
        self.rectpos = [(100,100),(100,200),(200,100)]
    
        image = wx.Image('scanimg.jpg')
        self.bmp = image.ConvertToBitmap()
        size = self.bmp.GetSize()
        self.xyratio = (size[0]/1200., size[1]/800.)
        self.bmp = scale_bitmap(self.bmp, 1200,800)
    
        pan = wx.Panel(self,-1)
        box = wx.BoxSizer()
        box.Add(pan,0)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        self.SetFocus()
        wx.FutureCall(200, self.SetFocus)

    def on_size(self, event):
        width, height = self.GetClientSize()
        self._buffer = wx.EmptyBitmap(width, height)
        self.update_drawing()

    def update_drawing(self):
        self.Refresh(False)

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        dc.SetPen(wx.Pen('black', 2))
        dc.DrawBitmap(self.bmp, 0, 0, True)
        
        for i in range(ncol):
            for j in range(nrow):
                dc.DrawCircle(self.xary[i,j],self.yary[i,j],1)
         
        #for xy in self.rectpos:
        #    dc.DrawCircle(xy[0], xy[1], 5)
       

    def on_motion(self, event):
        x, y = event.GetPosition()
        if not self.moveflag:
            return

        self.rectpos[self.ind] = (x,y)
        
        (xylu, xyld, xyru) = self.rectpos
        xi, yi = xylu
        xspan = xyru[0] - xylu[0] 
        yspan = xyld[1] - xylu[1]
        
        if self.ind == 1:
            w = xyld[0]-xylu[0]
            if w == 0:
                rad = 0
            else:
                rad = -np.arctan(w/float(yspan))
            xp = xi + xspan
            yp = yi + np.tan(rad)*xspan
            self.rectpos[2] = (xp,yp)
        else:
            h = xyru[1]-xylu[1]
            if h == 0:
                rad = 0
            else:
                rad = np.arctan(h/float(xspan))
            xp = xi + np.tan(-rad)*yspan
            yp = yi + yspan
            self.rectpos[1] = (xp,yp)
        self.xyi = (xi, yi)
        self.xyspan = (xspan, yspan)
        self.rad = rad
        self.make_grid_pos()


    def make_grid_pos(self):
        tx = self.xyspan[0] / np.cos(self.rad)
        ty = self.xyspan[1] / np.cos(self.rad)
        dx = tx / float(ncol-1)
        dy = ty / float(nrow-1)
        for i in range(ncol):
            self.xary[i,:] = i * dx
        for j in range(nrow):
            self.yary[:,j] = j * dy
        
        xary_r = self.xary * np.cos(self.rad) - self.yary * np.sin(self.rad) + self.xyi[0]
        yary_r = self.xary * np.sin(self.rad) + self.yary * np.cos(self.rad) + self.xyi[1]
        self.xary = xary_r
        self.yary = yary_r


    def on_left_down(self, event):
        self.moveflag = not(self.moveflag)
        
        x, y = event.GetPosition()
        ds = []
        for xy in self.rectpos:
            d = abs(x-xy[0])+abs(y-xy[1])
            ds += [d]
        self.ind = ds.index(min(ds))

    
    def on_key_down(self, event):
        key = event.GetKeyCode()
        
        # output to csv file
        if key == wx.WXK_RETURN:
            print 'key:Return'
            self.output() 
            quit()
    
    
    def output(self):
        w = csv.writer(open('gridpos.csv','wb'))
        w.writerow(['col','row','X (pixel)','Y (pixel)'])
        for i in range(ncol):
            for j in range(nrow):
                x = int(self.xary[i,j] * self.xyratio[0])
                y = int(self.yary[i,j] * self.xyratio[1])
                out = [i+1,j+1,x,y]
                w.writerow(out)
                print out
        

class DynamicFrame(wx.Frame):
    def __init__(self, *args, **kw):
        wx.Frame.__init__(self, *args, **kw)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_TIMER, self.on_timer)

        self.panel = DrawPanel(self)
        self.timer = wx.Timer(self)
        self.timer.Start(20)

    def on_close(self, event):
        self.timer.Stop()
        self.Destroy()

    def on_timer(self, event):
        self.panel.update_drawing()


     
app = wx.App(False)
frame = DynamicFrame(None, -1, "grid_setting.py", size=wx.Size(1200,800))
frame.Show(True)
app.MainLoop()
