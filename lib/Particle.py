#import CircleImage
import math
import numpy as np
import cv2
import circle_fit as cf
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from lib.singleCircleAnalysis import interp_along_radius

class Particle:
    def __init__(self, picture, x_midpoint, y_midpoint, radius):
        self.flag = 0  # 0: not validated 1: valid 2: not valid
        self.x_midpoint = x_midpoint
        self.y_midpoint = y_midpoint
        self.radius = radius
        self.crop_fac = 1.5
        self.origin = [max(0, int(self.x_midpoint-self.radius*self.crop_fac)),
                       max(0, int(self.y_midpoint-self.radius*self.crop_fac))]
        self.picture = picture[self.origin[1]:int(self.y_midpoint+self.radius*self.crop_fac),
                       self.origin[0]:int(self.x_midpoint+self.radius*self.crop_fac)]

    def find_intensity_max_arround_circles(self):
        #since evaluating in polar coordinates is terrible, lets just rotate the picture by the angle we want, and crop the interesting part of the picture from there
        masksizewidth = 5
        length = self.radius
        searchsize = 0.1*self.radius
        phi = 0
        lines_to_evaluate = []
        cv2.line(self.picture, (0, self.y_midpoint), (self.picture.shape[0], self.y_midpoint), color=0, thickness=2)
        for phi in range(0, 180, 30):
            #first create the rotation matrix for the angle to evaluate:
            phi = phi*2*math.pi/360
            rot = cv2.getRotationMatrix2D((self.picture.shape[0]/2, self.picture.shape[1]/2), phi, 1.0)
            #trans = np.concatenate([rot, np.array([[1],[1]]).dot(np.array([0]))], axis=1)
            print(rot)
            rotatetPicture = cv2.warpAffine(self.picture, rot, self.picture.shape)
            """
            x_min = self.x_midpoint+length-searchsize
            x_max = self.x_midpoint+length+searchsize
            y_min = self.y_midpoint-masksizewidth
            y_max = self.y_midpoint-masksizewidth
            """
            intensity_line = rotatetPicture[int(rotatetPicture.shape[0]/2-3):int(rotatetPicture.shape[0]/2+3),0:self.picture.shape[-1]]
            intensity_line = np.mean(intensity_line, axis=0)
            lines_to_evaluate.append([phi, intensity_line])
        #fining maximums in these lines:
        x_max = []
        y_max = []
        for line in lines_to_evaluate:
            #line[1] equals the points to evaluate, line[0] equals phi
            line_ev = line[1][0:int(len(line[1])/2)]
            x_max.append(-(-np.argmax(line_ev) + len(line_ev))*math.cos(line[0])+self.picture.shape[0]/2)
            y_max.append(-(-np.argmax(line_ev) + len(line_ev))*math.sin(line[0])+self.picture.shape[1]/2)

            line_ev=line[1][int(len(line[1])/2):-1]
            x_max.append(np.argmax(line_ev)*math.cos(line[0])+self.picture.shape[0]/2)
            y_max.append(np.argmax(line_ev)*math.sin(line[0])+self.picture.shape[1]/2)

        x=[]
        y=[]
        z=[]
        for line in lines_to_evaluate:
            x.append([(i-len(line[1])/2)*math.cos(line[0])+self.picture.shape[0]/2 for i in range(len(line[1]))])
            y.append([(i-len(line[1])/2)*math.sin(line[0])+self.picture.shape[1]/2 for i in range(len(line[1]))])
            z.append(line [1])

        x=np.asarray(x).flatten()
        y=np.asarray(y).flatten()
        z=np.asarray(z).flatten()

        fig, (axs1, axs2) = plt.subplots(1,2, sharex=True, sharey=True)
        axs1.scatter(x,y,c=z)
        #axs1.scatter(range(len(lines_to_evaluate[0][1])),12*np.ones(22,1), lines_to_evaluate[0][1])
        axs2.imshow(self.picture)
        axs2.scatter(x_max, y_max, c='b')
        # fit circle through pts:

        xc, yc, r, _ = cf.least_squares_circle(np.array([x_max, y_max]).transpose())
        c = plt.Circle((xc, yc), r, fill=False, color='red')
        axs2.add_artist(c)
        axs2.scatter(self.picture.shape[0]/2, self.picture.shape[1]/2, c='g', marker='o', s=200)
        axs2.scatter(xc, yc, c='r', marker='+', s=200)
        print(xc,yc)
        plt.show()

    def find_intensity_max_arround_circles2(self):
        kernel = np.ones((3, 3), np.uint8)
        #self.picture = cv2.erode(self.picture, kernel, iterations=1)
        #self.picture = cv2.dilate(self.picture, kernel, iterations=1)
        xcentre = np.shape(self.picture)[0]/2
        ycentre = np.shape(self.picture)[1]/2
        nphi = 9
        phi_ls = np.linspace(0, 2*math.pi*(1-1/nphi), nphi)
        # do it once to get length of line:
        _, _, tmp = interp_along_radius(self.picture, 0)

        fig, (axs1, axs2, axs3) = plt.subplots(1, 3, figsize=(10, 5))
        axs2.imshow(self.picture)
        # plot center of image:
        axs2.scatter(self.picture.shape[0]/2, self.picture.shape[1]/2, c='r', marker='+', s=1000)

        intensity_lines = np.zeros(shape=(len(tmp), len(phi_ls)))
        pts_of_max_int = np.zeros(shape=(nphi, 2))
        for (i, p) in enumerate(phi_ls):
            x, y, tmp = interp_along_radius(self.picture, p)
            #  put line into array:
            intensity_lines[:, i] = tmp
            pts_of_max_int[i, 0] = np.mean(x[np.where(tmp == np.amax(tmp))[0]])
            pts_of_max_int[i, 1] = np.mean(y[np.where(tmp == np.amax(tmp))[0]])
            axs2.plot(y, x, 'k--')

        xmax = pts_of_max_int[:, 0]
        ymax = pts_of_max_int[:, 1]
        axs2.scatter(ymax, xmax, c='r')
        # fit circle through pts:
        xc, yc, r, _ = cf.least_squares_circle(np.array([ymax, xmax]).transpose())
        # circle from hough:
        c = plt.Circle((xcentre, ycentre), self.radius, fill=False, color='red', linestyle='--', linewidth=3)
        axs2.add_artist(c)
        # circle newly found:
        c = plt.Circle((xc, yc), r, fill=False, color='black', linewidth=3)
        axs2.add_artist(c)
        axs2.scatter(xc, yc, c='g', marker='+', s=20000)

        ny, nx = np.shape(intensity_lines)
        XX, YY = np.meshgrid(np.arange(nx), np.arange(ny))
        axs1.contourf(XX, YY, intensity_lines)
        axs1.scatter(np.arange(nx), np.sqrt(np.square(xmax-xcentre)+np.square(ymax-ycentre)), c='r')
        axs1.set_xlim([0, nx-1])
        every = 2
        axs1.set_xticks(np.arange(nphi)[::every])
        axs1.set_xticklabels(["%4.1f" % (p*180/math.pi) for p in phi_ls[::every]], rotation=0)
        axs1.set_xlabel('angle [°]')
        axs1.set_ylim([0, np.shape(XX)[0]-1])
        axs1.set_ylabel('Radius [px]')
        axs2.set_xlabel('x [px]')
        axs2.set_ylabel('y [px]')
        print(nx)
        lx = np.shape(self.picture)[0]
        ly = np.shape(self.picture)[1]
        dx = min(abs(lx-xc), lx)-1
        dy = min(abs(ly-yc), ly)-1
        print(int(xc-dx), int(xc+dx))
        print(int(yc-dy), int(yc+dy))
        #self.picture = self.picture[xc-dx:xc+dx, yc-dy:yc+dy]
        axs3.imshow(self.picture[int(xc-dx):int(xc+dx), int(yc-dy):int(yc+dy)])
        plt.show()