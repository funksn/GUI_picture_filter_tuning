from pco_tools import pco_reader as pco
import numpy as np
import cv2
import csv
import pickle
from lib.Particle import Particle
import sys
import os
from scipy import ndimage
from scipy.signal import medfilt as mfilt
import json

class CircleImage:

    def __init__(self, image_path, settings, keepRaw = True, normalize=True):
        """
        :param image_path: filepath of the image
        :param keepRaw: if Truem the raw image is kept in the Variable raw_img
        """
        self.image_path=image_path
        if ".b16" in image_path:
            im = pco.load(image_path)
        else:
            im = cv2.imread(image_path, 0)
        if keepRaw:
            self.raw_img_norm = (im - im.min()) / (im.max() - im.min()) * 255
            #self.raw_img_norm = np.uint8(im / np.max(im) * 256)
            self.raw_img = im
        self.settings = settings
        #adjust datatype of image for gray values
        #and normalize the range from 0 to 256
        if normalize:
            #self.img = np.uint8(im / np.max(im)) * 256
            self.img = (im - im.min()) / (im.max() - im.min()) * 255
            print(np.max(im))
            print(np.max(self.img))
        else:
            self.img = im
        self.Particles = None
        self.circles = None

    def cropPicture(self, x1, y1, x2, y2):
        if not min(x1,y1,x2,y2)<0:
            self.img=self.img[x1:y1, x2:y2]

    def getContours(self):
        pass#self.img=cv2.

    def adaptive_threshold_gauss(self,a=11, b=2):
        try:
            a = self.settings['thres_gauss_a']
            b = self.settings['thress_gauss_b']
            max = 1#np.asarray(self.img).max
            self.img = cv2.adaptiveThreshold(self.img, max, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, a, b)
        except KeyError:
            print('no settings for adp_thres_gauß')
        return self.img

    def adaptive_threshold_mean(self, a=11, b=2):
        try:
            a = self.settings['thres_mean_a']
            b = self.settings['thres_mean_b']
            max = 1# np.asarray(self.img).max
            self.img = cv2.adaptiveThreshold(self.img, max, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, np.max(self.img.shape), a)#, b)
        except KeyError:
            print('no settings for adp_thres_gauß')
        return self.img

    def canny(self, lower_th_canny=17, upper_th_canny=100, filter='bilateral', filterSettings = None):
        try:
            lower_th_canny = self.settings['lower_th_canny']
            upper_th_canny = self.settings['upper_th_canny']
        except KeyError:
            pass
        if filterSettings is None:
            try:
                a = self.settings['CA_filtersize']
                b = self.settings['CA_sigmaColor']
                c = self.settings['CA_sigmaSpace']
                filterSettings = {'filtersize': a, 'sigmaColor': b, 'sigmaSpace': c}
            except KeyError:
                filterSettings = {'filtersize': 9, 'sigmaColor': 10, 'sigmaSpace': 10}
        #combined with gaussian blurr
        # from https://www.pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
        if self.img.dtype is not 'uint8':
            self.img = np.uint8(self.img / np.max(self.img) * 256)
        if filter == 'gauss':
            blurred = cv2.GaussianBlur(self.img, (3, 3), 0)
        if filter == 'bilateral':
            blurred = cv2.bilateralFilter(self.img, d=filterSettings['filtersize'], sigmaColor=
                                            filterSettings['sigmaColor'], sigmaSpace=filterSettings['sigmaSpace'])
        if filter is None:
            blurred = self.img
        else:
            v = np.median(blurred)
        self.img = cv2.Canny(blurred, lower_th_canny, upper_th_canny)
        return self.img

    def bilateral(self, filterSettings=None):
        if self.img.dtype is not 'uint8':
            self.img = np.uint8(self.img / np.max(self.img) * 256)
        if filterSettings == None:
            filterSettings = {'filtersize': 9, 'sigmaColor': 10, 'sigmaSpace': 10}
        blurred = cv2.bilateralFilter(self.img, d=filterSettings['filtersize'], sigmaColor=
                                        filterSettings['sigmaColor'], sigmaSpace=filterSettings['sigmaSpace'])
        self.img = blurred
        return blurred

    def gauss(self):
        if self.img.dtype is not 'uint8':
            self.img = np.uint8(self.img / np.max(self.img) * 256)
        blurred = cv2.GaussianBlur(self.img, (3, 3), 0)
        self.img = blurred
        return blurred

    def calc_bg(self, img=None):
        if img is None:
            img = self.img
        self.bg = np.mean(img)
        return self.bg

    def subtract_bg(self, img=None):
        if img is None:
            self.img = self.img - self.calc_bg()
            self.img[self.img<0]=0
        else:
            img = img - self.calc_bg(img)
            img[img<0]=0
            self.img=img
        return self.img

    def subtract_local_bg(self, d=10):
        ny, nx = np.shape(self.img)
        dx = np.arange(0, nx, d)
        dy = np.arange(0, nx, d)
        ndx = len(dx)
        ndy = len(dy)
        for i in range(ndy-1):
            for j in range(ndx-1):
                limg = self.img[dy[i]:dy[i+1], dx[j]:dx[j+1]]
                lmean = np.mean(limg)
                self.img[dy[i]:dy[i+1], dx[j]:dx[j+1]][limg<lmean] = 0#self.img[dy[i]:dy[i+1], dx[j]:dx[j+1]]-lmean
        return self.img

    def snr(self):
        mu = np.mean(self.img)
        self.snr = self.img/mu
        return self.snr

    def median(self, k):
        self.img = cv2.medianBlur(self.img, k)
        return self.img

    def dilate(self, kernel=np.ones((3, 3), np.uint8)):
        self.img = cv2.dilate(self.img, kernel, iterations=1)
        return self.img

    def erode(self, kernel=np.ones((3, 3), np.uint8)):
        self.img = cv2.erode(self.img, kernel, iterations=1)
        return self.img

    def detect_circles(self,settings=None, image=None):
        self.circles = []
        if settings is None:
            settings=self.settings
        if image is None:
            image = self.img

        hough_circles = cv2.HoughCircles(np.uint8(image), method=cv2.HOUGH_GRADIENT, dp=settings['dp'], minDist=settings['minDist'], param1=settings['par1'], param2=settings['par2'], minRadius=settings['minRad'], maxRadius=settings['maxRad'])
        self.circles = hough_circles
        #for hc in hough_circles[0]:
        #    self.circles.append(hc)

    def get_enclosing_circle(self, edge=None):
        #only works for if edge detection works well for circles and if there is just one circle in the edgepoints
        if edge is None:
            edge=self.img
        pointlists = np.nonzero(edge)
        circlepoints = np.stack([pointlists[1], pointlists[0]], axis=1) #transfer all edgepoint into a list of 2d points
        detected = cv2.minEnclosingCircle(circlepoints)#find the enclosing circle for these edgepoints
        self.circles = detected
        #drawOn = self.raw_img_norm
        #self.circles = [[self.circles[0][0], self.circles[0][1], self.circles[1]]]
        #return drawOn

    def detect_and_draw_circles(self, image=None, drawOn=None):
        if image is None:
            image = self.img
        self.detect_circles(image=image)
        if drawOn is None:
            drawOn=np.uint8(self.img / np.max(self.img) * 256)
        #drawOn = cv2.cvtColor(drawOn, cv2.COLOR_GRAY2BGR)
        circles = self.circles
        for i in circles[0,:]:
            cv2.circle(drawOn, (i[0], i[1]), i[2], (0, 255, 0), 2)
            cv2.rectangle(drawOn, (int(i[0]-1), int(i[1]-1)), (int(i[0]+1), int(i[1]+1)), (0, 0, 255))
        return drawOn

    def detect_circles_and_create_particles(self, settings):
        if self.circles is None:
            self.detect_circles(settings)
            if self.circles is None:
                raise Exception('couldnt find particles in picture, try to change parameters for circledetection')
        self.Particles = []
        for circle in self.circles[0,:]:
            #part = Particle(self.subtract_bg(self.raw_img), circle[0], circle[1], circle[2])
            #part = Particle(self.subtract_local_bg(d=10), circle[0], circle[1], circle[2])
            part = Particle(self.img, circle[0], circle[1], circle[2])
            self.Particles.append(part)


    def save_detected_circles(self,savepath=None, fileFormat='csv'):
        if savepath is None:
            savepath = self.image_path.replace('.tiff', 'detected_c.csv')
        if self.circles is not None:
            if not os.path.isfile(self.image_path.replace('.tiff','detected_c.csv')):
                with open(savepath, 'x', newline='') as myfile:
                    print('created file')
            if fileFormat == 'csv':
                with open(savepath,'w', newline='') as myfile:
                    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                    wr.writerow(self.circles)
            if fileFormat == 'pickle':
                print('saveing to pickle')
                with open(savepath, 'wb') as f:
                    pickle.dump(self.circles, f)
            if fileFormat == 'numpy':
                np.save(savepath, self.circles)
        else:
            print('there are no circles detected yet, may run detct_circles() first')

    def print_circle_stats(self):
        print(" > Hough found %d particles " % np.shape(self.circles)[1])
        print(" > Average diameter is %3.2f" % (2*np.mean(np.asarray([r[2] for r in self.circles[0]]))))

    def fft(self):
        f = np.fft.fft2(self.img)
        self.fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(self.fshift))
        self.magnitude_spectrum = magnitude_spectrum
        return magnitude_spectrum

    def ifft(self, val):
        rows, cols = self.img.shape
        crow, ccol = rows // 2, cols // 2
        if val>0:
            self.fshift[crow - val:crow + val, ccol - val:ccol + val] = 0
        else:
            val = abs(val)
            self.fshift[val:-val, val:-val] = 0
        f_ishift = np.fft.ifftshift(self.fshift)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        self.img = img_back
        return img_back

    def high_pass(self, ksize=None):
        try:
            ksize = self.settings['highpass ksize']
        except KeyError:
            self.settings['highpass ksize'] = 7
        if ksize % 2 == 0:
            sys.exit('Kernel size must be odd')
        kernel = -1/(ksize*ksize)*np.ones((ksize,ksize))
        kernel[(ksize-1)//2, (ksize-1)//2] = (ksize*ksize-1)/(ksize*ksize)
        highpass_3x3 = ndimage.convolve(self.img, kernel)
        self.img = highpass_3x3
        return self.img

    def medfilt(self, ksize=3):
        try:
            ksize = self.settings['median ksize']
        except KeyError:
            pass
        print(ksize)
        self.img = mfilt(self.img, kernel_size=ksize)
        return self.img

    def laplace(self, ksize=3):
        """
        try:
            ksize = self.settings['laplace ksize']
        except KeyError:
            pass
        self.img = cv2.Laplacian(self.img, 256, ksize=ksize)
        """
        self.img = ndimage.laplace(self.img)
        return self.img

    def sobel(self, dx=3, dy=3):
        '''
        try:
            dx = self.settings['xdim']
            dy=self.settings['ydim']
        except KeyError:
            pass

        self.img = cv2.Sobel(self.img, 256, dx=dx, dy=dy)
        '''
        self.img = ndimage.sobel(self.img)
        return self.img

    def open(self, ksize=3):
        kernel = np.ones((ksize, ksize),np.uint8)
        self.img = cv2.morphologyEx(self.img, cv2.MORPH_OPEN, kernel)
        return self.img