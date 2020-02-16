import lib.Particle
import lib.CircleImage as CircleImage
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import cv2
import sys
import numpy as np
from lib.singleCircleAnalysis import multistepCircleDetection
from lib.management import read_settings
import glob
import os
img_select = 1

ls_settings = glob.glob('./settings/hough_study/*set')
for setting_path in ls_settings[0:1]:
    print(setting_path)
    settings = read_settings(setting_path)

    if img_select == 1:
        a = CircleImage.CircleImage('.\\pictures\\Cam1_0001A.b16', settings)
        a.cropPicture(settings['crop_xmin'], settings['crop_xmax'], settings['crop_ymin'], settings['crop_ymax'])
    elif img_select == 2:
        a = CircleImage.CircleImage('C:\\Users\\Matthias\\Documents\\GitHub\\DefocusingPTV\\microsig-python-master\\examples\B00002.tif')
    elif img_select == 3:
        a = CircleImage.CircleImage('.\\pictures\\clutch\Cam1_0001B.tiff', settings)
        a.cropPicture(settings['crop_xmin'], settings['crop_xmax'], settings['crop_ymin'], settings['crop_ymax'])

    raw_img = a.img
    a.raw_img = raw_img

    # find circles by means of hough trafo:
    if settings['medfilt']:
        print(' > applying median filter ')
        a.img = a.medfilt()

    if settings['fft']:
        print(' > applying fft cutoff ')
        a.fft()
        a.img = a.ifft(settings['f_cutoff'])
    if settings['highpass']:
        print(' > applying highpass ')
        a.img = a.high_pass()
    if settings['erode']:
        print(' > applying erode ')
        a.erode()
    if settings['dilate']:
        print(' > applying dilate ')
        a.dilate()
    if settings['binarize']:
        print(' > applying binarize ')
        a.img[a.img<settings['binarize_th']] = 0
        a.img[a.img>=settings['binarize_th']] = 256
    if settings['canny']:
        print(' > applying canny ')
        a.canny()

    debug=True
    if debug:
        fig, ax = plt.subplots(1, 2)
        print(cv2.bitwise_not(a.raw_img))
        ax[0].imshow(cv2.bitwise_not(a.raw_img), cmap='bone', vmin=230, vmax=256)
        ax[1].imshow(cv2.bitwise_not(a.img), cmap='bone', vmin=0, vmax=256)
        plt.show()
        #sys.exit()
    #a.img = cv2.GaussianBlur(a.img, (3, 3), 0)
    #a.img = a.ifft(-100)
    #a.img[a.img < np.mean(a.img)] = 0
    a.detect_circles_and_create_particles(settings=settings)
    a.print_circle_stats()

    # plot raw and raw with circles:
    g_fig, g_ax = plt.subplots(1, 2)
    g_ax[0].imshow(raw_img, cmap='bone', vmax=100)
    g_ax[1].imshow(a.img, cmap='bone', vmax=20)

    circles = a.circles
    for (i, circ) in enumerate(circles[0, :]):
        c = plt.Circle((circ[0], circ[1]), circ[2], fill=False, color='green', linewidth=1)
        g_ax[0].add_artist(c)
        g_ax[0].text(circ[0]+0.75*circ[2], circ[1]-0.75*circ[2], "%i" % (i+1), color='green')

    print(np.shape(a.circles[0]))
    for (i, p) in enumerate(a.Particles[0:]):
        try:
            print(" > Checking Circle x/y/r:", p.x_midpoint, p.y_midpoint, p.radius)
            new_pic, new_res = multistepCircleDetection(p.picture, settings, iterations=1, showplot=False, prev_result=None)
            if new_res[2] is not np.nan:
                p.origin[0] += new_res[0]
                p.origin[1] += new_res[1]
                # plot new circles:
                c = plt.Circle((p.origin[0], p.origin[1]), new_res[2], fill=False, color='red', linewidth=1)
                g_ax[1].add_artist(c)
                c = plt.Circle((p.origin[0], p.origin[1]), new_res[2], fill=False, color='red', linewidth=1)
                g_ax[0].add_artist(c)
                g_ax[1].text(p.origin[0]+0.75*new_res[2], p.origin[1]-new_res[2], "%i" % (i+1), color='red')
                p.flag = 1
            else:
                p.flag = 2
        except:
            p.flag = 2
    plt.savefig("%s.png" % setting_path)
    plt.show()

    """
    sys.exit()

    #a.img[a.img<40]=0

    ax[0].imshow(a.img, cmap='gray', vmax=256)
    ax[1].hist(a.img.flatten(), 256, [0, 256], color='k')
    ax[1].set_yscale('log')
    #  a = CircleImage.CircleImage('.\\pictures\\Cam1_0001A.b16')
    #  a.cropPicture(0, 200, 0, 200)
    #a.detect_circles_and_create_particles()
    #a.print_circle_stats()
    plt.show()
    a.detect_circles_and_create_particles()

    for particle in a.Particles[0:5]:
        try:
            particle.find_intensity_max_arround_circles3()
        except:
            pass
    from lib.singleCircleAnalysis import multistepCircleDetection
    for (iparticle, particle) in enumerate(a.Particles[0:5]):

        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.imshow(a.img)
        circles = a.circles

        #  plot all circles in black to first ax:
        for i in circles[0, :]:
            c = plt.Circle((i[0], i[1]), i[2], fill=False, color='black', linewidth=1)
            ax1.add_artist(c)

        #  get x,y,r from particle:
        print(a.circles)
        i = a.circles[0, iparticle]

        #  plot circle found with Hough in big picture:
        try:
            c = plt.Circle((i[0], i[1]), i[2], fill=False, color='red', linewidth=1)
            ax1.add_artist(c)
            t = plt.Rectangle((i[0]-particle.crop_fac*i[2], i[1]-particle.crop_fac*i[2]),
                              2*particle.crop_fac*i[2], 2*particle.crop_fac*i[2], fill=False, color='red', linewidth=1)
            ax1.add_artist(t)

            #  plot found circle image and the circle itself in second ax:
            ax2.imshow(particle.picture)
            c = plt.Circle((np.shape(particle.picture)[0] // 2, np.shape(particle.picture)[1] // 2),
                           i[2], fill=False, color='red', linewidth=1)
            ax2.add_artist(c)
        except:
            pass

        #  find better fitting circle and plot it in green:
        new_pic, new_res = multistepCircleDetection(particle.picture, nphi=7, iterations=1, showplot=False)
        c = plt.Circle((new_res[0], new_res[1]), new_res[2], fill=False, color='green', linewidth=2)
        ax2.add_artist(c)

        # second iteration:
        new_pic, new_res = multistepCircleDetection(new_pic, nphi=7, iterations=1, showplot=False, prev_result=new_res)
        c = plt.Circle((new_res[0], new_res[1]), new_res[2], fill=False, color='green', linewidth=2, linestyle='--')
        ax2.add_artist(c)

        fig.canvas.manager.full_screen_toggle()
        plt.show()
        """
