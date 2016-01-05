"""
Image object

"""

import cv
import numpy as np
import matplotlib.pylab as plt

# color value for drawing image
RED = cv.CV_RGB(255,0,0)
BLUE = cv.CV_RGB(0,0,255)
YELLOW = cv.CV_RGB(255,255,0)

class Image():
    def __init__(self):
        self.iplimg = None
        self.size = None
    
    def load_file(self, fname):
        self.iplimg = cv.LoadImage(fname)
        self.size = cv.GetSize(self.iplimg)
    
    def load_array(self, ary):
        iplimg = get_iplimg_from_array(ary)
        self.iplimg = iplimg
        self.size = cv.GetSize(iplimg)

    def get_array(self):
        mat = cv.GetMat(self.iplimg)
        ary = np.array(mat)
        return ary

    def save_to_file(self, fname='test'):
        cv.SaveImage('%s.png'%(fname), self.iplimg)
    
    def draw_edges(self, edges):
        RED = (0,0,255)
        for edge in edges:
            self.iplimg[edge[1],edge[0]] = RED

    def draw_lines(self, lines):
        for line in lines:
            cv.Line(self.iplimg, line[0], line[1], BLUE, 1)

    def unsharp_mask(self, k=5, kernel=21, outLevel=2):
        gray = cv.CloneImage(self.iplimg)
        smooth = cv.CreateImage(self.size, cv.IPL_DEPTH_8U,1)
        sub = cv.CreateImage(self.size, cv.IPL_DEPTH_8U,1)
        out = cv.CreateImage(self.size, cv.IPL_DEPTH_8U,1)
        tmp = cv.CloneImage(self.iplimg) 
        cv.Smooth(tmp,smooth,cv.CV_GAUSSIAN, kernel)
        cv.Sub(self.iplimg, smooth, sub)
        m = cv.GetMat(sub)
        a = np.asarray(m)
        a = a * k
        mat = cv.fromarray(a) 
        cv.Add(self.iplimg, mat, tmp)
        self.iplimg = tmp

    def convert_to_gray(self):
        img_gray = self.copy()
        tmp = cv.CreateImage(self.size, cv.IPL_DEPTH_8U, 1)
        cv.CvtColor(self.iplimg, tmp, cv.CV_BGR2GRAY)
        img_gray.iplimg = tmp
        return img_gray
    
    def convert_to_binary(self, threshold):
        img_binary = self.copy()
        tmp = cv.CreateImage(self.size, cv.IPL_DEPTH_8U,1)
        cv.Threshold(self.iplimg, tmp,
            threshold, 255, cv.CV_THRESH_BINARY)
        img_binary.iplimg = tmp
        return img_binary

    def copy(self):
        img = Image()
        img.iplimg = self.iplimg
        img.size = self.size
        return img


def get_iplimg_from_array(a):
    dtype2depth = {
        'uint8':   cv.IPL_DEPTH_8U,
        'int8':    cv.IPL_DEPTH_8S,
        'uint16':  cv.IPL_DEPTH_16U,
        'int16':   cv.IPL_DEPTH_16S,
        'int32':   cv.IPL_DEPTH_32S,
        'float32': cv.IPL_DEPTH_32F,
        'float64': cv.IPL_DEPTH_64F,
    }
    try:
        nChannels = a.shape[2]
    except:
        nChannels = 1
    cv_im = cv.CreateImageHeader((a.shape[1],a.shape[0]),
        dtype2depth[str(a.dtype)], nChannels)
    cv.SetData(cv_im, a.tostring(),
        a.dtype.itemsize*nChannels*a.shape[1])
    mat = cv.GetMat(cv_im)
    iplimg = cv.GetImage(mat)
    return iplimg


if __name__ == "__main__":
    img_color = Image()
    img_color.load_file('../45.tif')

    img_gray = img_color.convert_to_gray()
