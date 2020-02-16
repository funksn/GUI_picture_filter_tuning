import matplotlib
matplotlib.use("TkAgg")
from mpl_toolkits.axes_grid1 import make_axes_locatable

from lib.CircleImage import *
import lib.Particle
import numpy as np
import os
import matplotlib.pyplot as plt
from tikzplotlib import save as tikz_save


def settings1(picpath, folderpath):
    settings = {'par1': 50, 'par2': 2, 'dp': 0.4, 'minDist': 15, 'minRad': 5, 'maxRad': 20}
    pic = CircleImage(folderpath + '\\' + picpath, settings)
    pic.detect_circles()  # image=pic)
    return pic


def settings2(picpath, folderpath):
    settings = {'par1': 50, 'par2': 5, 'dp': 0.4, 'minDist': 15, 'minRad': 5, 'maxRad': 20}
    pic = CircleImage(folderpath + '\\' + picpath, settings)
    pic.subtract_bg()
    pic.medfilt(ksize=3)
    pic.subtract_bg()
    pic.laplace(ksize=9)
    pic.subtract_bg()
    pic.detect_circles()  # image=pic)
    return pic

def settings3(picpath, folderpath):
    #everything like one, but without normalization in the beginning
    settings = {'par1': 15, 'par2': 1, 'dp': 13, 'minDist': 20, 'minRad': 5, 'maxRad': 20}
    pic = CircleImage(folderpath + '\\' + picpath, settings, normalize=False)
    pic.detect_circles()  # image=pic)
    return pic

def settings4(picpath, folderpath):
    settings = {'par1': 200, 'par2': 30, 'dp': 0.4, 'minDist': 15, 'minRad': 5, 'maxRad': 20}
    pic = CircleImage(folderpath + '\\' + picpath, settings)
    pic.subtract_bg()
    pic.medfilt(ksize=3)
    pic.subtract_bg()
    pic.laplace(ksize=9)
    pic.subtract_bg()
    pic.detect_circles()  # image=pic)
    return pic

def settings5(picpath, folderpath):
    settings = {}
    pic = CircleImage(folderpath + '\\' + picpath, settings)
    pic.canny(lower_th_canny=30, upper_th_canny=230)
    pic.get_enclosing_circle()
    return pic

def settings6(picpath, folderpath):
    settings = {'par1': 50, 'par2': 2, 'dp': 18, 'minDist': 15, 'minRad': 5, 'maxRad': 20}
    pic = CircleImage(folderpath + '\\' + picpath, settings)
    pic.detect_circles()  # image=pic)
    return pic

def evaluate(filtersettings = 1):
    folderpath = r'C:\Users\Stefan\bwSyncAndShare\LehrlaborEnergietechnik (Matthias Probst)\imgs\LaserDuenn_Vol250_pd200\Cam1_001A'
    pics = os.listdir(folderpath)
    for pic in pics:
        print(pic)
        if pic.split('.')[-1]=='tiff': #and pic.split['0'][0] != 'processed':
            picpath = pic
            if filtersettings == 1:
                pic = settings1(picpath, folderpath)
            if filtersettings == 2:
                pic=settings2(picpath, folderpath)
            if filtersettings == 3:
                pic = settings3(picpath, folderpath)
            if filtersettings == 4:
                pic = settings4(picpath, folderpath)
            if filtersettings == 5:
                pic = settings5(picpath, folderpath)
            if filtersettings == 6:
                pic = settings6(picpath, folderpath)

            fig, axs = plt.subplots(1, 3)

            fig.set_tight_layout(True)
            vmin = min(image.min() for image in [pic.raw_img_norm, pic.img])
            vmax = max(image.max() for image in [pic.raw_img_norm, pic.img])

            img3 = axs[0].imshow(pic.raw_img)
            axs[0].set_title('Rohbild')
            axs[0].set_xlabel('in px')
            axs[0].set_ylabel('in px')
            divider = make_axes_locatable(axs[0])
            cax3 = divider.append_axes("right", size="5%", pad=0.05)
            cbar1 = fig.colorbar(img3, cax=cax3)
            cbar1.set_label('Intensität')

            img2 = axs[1].imshow(pic.img, vmin=vmin, vmax=vmax)
            axs[1].set_title('vorkonditioniertes\n Bild')
            axs[1].set_xlabel('in px')
            axs[1].set_ylabel('in px')
            divider = make_axes_locatable(axs[1])
            cax2 = divider.append_axes("right", size="5%", pad =0.05)
            cbar2=fig.colorbar(img2, cax=cax2)
            cbar2.set_label('norm. Intensität')


            img1 = axs[2].imshow(pic.raw_img_norm, vmin=vmin, vmax=vmax)
            axs[2].set_title('normalisiertes\n Bild')
            axs[2].set_xlabel('in px')
            axs[2].set_ylabel('in px')
            divider = make_axes_locatable(axs[2])
            cax1 = divider.append_axes("right", size="5%", pad=0.05)
            cbar3 = fig.colorbar(img1, cax=cax1)
            cbar3.set_label('norm. Intensität')


            try:
                if filtersettings == 5:
                    circle=pic.circles
                    circ = plt.Circle(circle[0], circle[1], fill=False, color='r')
                    circ2 = plt.Circle(circle[0], circle[1], fill=False, color='r')
                    circ3 = plt.Circle(circle[0], circle[1], fill=False, color='r')
                    axs[2].add_artist(circ)
                    axs[1].add_artist(circ2)
                    axs[0].add_artist(circ3)
                else:
                    for circle in pic.circles[0, :]:
                        circ = plt.Circle((circle[0], circle[1]), circle[2], fill=False, color='r')
                        circ2 = plt.Circle((circle[0], circle[1]), circle[2], fill=False, color='r')
                        circ3 = plt.Circle((circle[0], circle[1]), circle[2], fill=False, color='r')
                        axs[2].add_artist(circ)
                        axs[1].add_artist(circ2)
                        axs[0].add_artist(circ3)
            except TypeError:
                print('circle detection didnt work, please try with different parameter')
            if not os.path.exists(folderpath + '\\Filtersettings' + str(filtersettings)):
                os.mkdir(folderpath + '\\Filtersettings' + str(filtersettings))
            #plt.show
            #tikz_save(folderpath + '\\Filtersettings' + str(filtersettings) + '\\' + picpath.split('\\')[-1].replace('.tiff', '.tex'))
            #plt.show()
            plt.savefig(folderpath + '\\Filtersettings' + str(filtersettings) + '\\' + picpath.split('\\')[-1].replace('.tiff', '.pdf'), bbox_inches='tight')
            plt.savefig(folderpath + '\\Filtersettings' + str(filtersettings) + '\\' + picpath.split('\\')[-1].replace('.tiff', '.png'), bbox_inches='tight')

            print(folderpath + '\\Filtersettings' + str(filtersettings) + '\\' + picpath.split('\\')[-1])
            pic.save_detected_circles(savepath=folderpath + '\\Filtersettings' + str(filtersettings) + '\\' + picpath.split('\\')[-1].replace('.tiff', '_detected.npy'), fileFormat='numpy')
        plt.close('all')

#for i in range(6,7):
#    print(i)
evaluate(filtersettings=4)