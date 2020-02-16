import numpy as np
import cv2

def autocanny(image, sigma=0.33):
    #from https://www.pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
    v = np.median(image)
    lower = int(max(0, (1.0-sigma)*v))
    upper = int(min(255, (1.0+sigma)*v))
    edge = cv2.Canny(image, lower, upper)
    return edge