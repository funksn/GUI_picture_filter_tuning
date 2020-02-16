import lib.CircleImage as CircleImage
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import os

#todo parameter variation mit optimierung siehe https://deap.readthedocs.io/en/master/tutorials/basic/part1.html
#todo helligkeitsnormierung

a = CircleImage.CircleImage('.\\pictures\\Cam1_0001A.b16')
fig, axs = plt.subplots(2,2, sharex=True, sharey=True)
#a.cropPicture()
axs[0][0].imshow(a.img)
axs[1][0].set_title('Raw picture')
a.subtract_bg()
axs[1][0].imshow(a.canny())
axs[1][0].set_title('Picture after Background subtraction\n and canny filtering')
axs[0][1].imshow(a.canny())
axs[0][1].set_title('Picture after Background subtraction,\n canny filtering and hough transformation')
axs[1][1].imshow(a.raw_img)
axs[1][1].set_title('Raw picture with detected circles')

#axs[0].imshow(a.autocanny(sigma=0))
#axs[1].imshow(a.autocanny(filter='bilateral'))
#plt.imshow(a.img)
#plt.show()
#axs[1][0].imshow(a.autocanny(sigma=1))
a.detect_and_draw_circles(image=a.canny())
for circle in a.circles[0,:]:
    circ = plt.Circle((circle[0], circle[1]), circle[2], fill=False, color='g')
    axs[0][1].add_artist(circ)
for circle in a.circles[0, :]:
    circ = plt.Circle((circle[0], circle[1]), circle[2], fill=False, color='g')
    axs[1][1].add_artist(circ)
a.save_detected_circles()
plt.show()
