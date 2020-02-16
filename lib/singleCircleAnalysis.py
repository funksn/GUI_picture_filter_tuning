import numpy as np
import math
import circle_fit as cf
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt


def interp_along_radius(img, phi, centre):
    ny, nx = np.shape(img)
    # center points:
    img_centre = (nx // 2, ny // 2)
    if img_centre == centre:  # take midpoint of image:
        cx = nx // 2
        cy = ny // 2
        x = np.arange(min(cx, cy))
    else:
        cx, cy = centre
        #  max radius can only be as long as smallest distance to image border
        smallest = min(ny-cx, cx, nx-cy, cy)
        import math
        x = np.arange(math.floor(smallest))
    xx = x*np.cos(phi)+cx
    yy = x*np.sin(phi)+cy
    intensity_along_line = img[np.uint(np.round(xx)), np.uint(np.round(yy))]
    return xx, yy, intensity_along_line


def center_of_intensity(I, exclude_border=None, showplot=False):
    ny, nx = np.shape(I)

    if showplot:
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.imshow(I)

    if exclude_border is not None:
        I[0:int(exclude_border*ny), 0:int(exclude_border*nx)] = 0
        I[int((1-exclude_border)*ny):-1, int((1-exclude_border)*nx):-1] = 0

    if showplot:
        ax2.imshow(I)

    Idot = np.zeros((2, 1))
    for i in range(ny):
        for j in range(nx):
            Idot += I[i, j]*np.array([[i], [j]])
    try:
        centre = 1/np.sum(I)*Idot
    except:
        centre = [nx, ny]

    if showplot:
        ax2.scatter(centre[1], centre[0])
        plt.show()

    return centre


def multistepCircleDetection(sc_img, settings, prev_result=None, showplot=True, iterations=2):
    if prev_result is None:
        pres = None
        #  estimate center by means of intesity distribution (center of intensity)
        centre = center_of_intensity(sc_img, exclude_border=0.1, showplot=showplot)
        pres = [centre[0, 0], centre[1, 0], 5]
        print(" > Iteration 1")
        sc_img, [xc, yc, r] = singleCircleAnalysis(sc_img, settings, prev_result=pres, showplot=showplot)
        print(" > [RESULT]: r=%3.1f" % r)
    else:  # else increase iterations by 1 so range has len>0
        iterations += 1
        xc, yc, r = prev_result
    for i in range(iterations-1):
        #  pres = [xc, yc, r]
        pres = [np.shape(sc_img)[0]//2, np.shape(sc_img)[1]//2, r]
        print(" > Iteration %2d" % (i+2))
        sc_img, [xc, yc, r] = singleCircleAnalysis(sc_img, settings, nphi=nphi, prev_result=pres, showplot=showplot)
        print(" > [RESULT]: r=%3.1f" % r)
    return sc_img, [xc, yc, r]


def singleCircleAnalysis(sc_img, settings, prev_result=None, showplot=True, iterations=2):
    """
    Analyzes an image with only one circle in it. Having more is possible but will most likely fail.
    A result by means of hough transform or earlier investigation can be passed (cx, cy, r). If not, cx, cy is set to
    centre of image.
    :param sc_img: circle image
    :param nphi: number of angles at which lines will be used to evaluate intensity from centre point towards image
                 border
    :param prev_result: list or numpy array ordered like [cx, cy, r] whith center points cx, cy and radius r
    :param showplot: results will be plotted. default is True
    :return: image with circle where center of image is center of found circle. Therefore image may be smaller in size
    """
    nphi = settings['nphi']
    ny, nx = np.shape(sc_img)
    phi_ls = np.linspace(0, 2*math.pi*(1-1/nphi), nphi)
    # do it once to get length of line:
    # print("prev_result", prev_result)
    _, _, tmp = interp_along_radius(sc_img, 0, centre=(prev_result[0], prev_result[1]))
    intensity_lines = np.zeros(shape=(len(tmp), len(phi_ls)))
    pts_of_max_int = np.zeros(shape=(nphi, 2))

    xcentre = nx/2
    ycentre = ny/2

    if showplot:
        fig, (axs1, axs2, axs3) = plt.subplots(1, 3, figsize=(10, 5))
        axs2.imshow(sc_img)

    intensity_lines = np.zeros(shape=(len(tmp), len(phi_ls)))
    pts_of_max_int = np.zeros(shape=(nphi, 2))
    for (i, p) in enumerate(phi_ls):
        x, y, tmp = interp_along_radius(sc_img, p, centre=(prev_result[0], prev_result[1]))
        #  put line into array:
        intensity_lines[:, i] = tmp
        pts_of_max_int[i, 0] = np.mean(x[np.where(tmp == np.amax(tmp))[0]])
        pts_of_max_int[i, 1] = np.mean(y[np.where(tmp == np.amax(tmp))[0]])
        if showplot:
            axs2.plot(x, y, 'k--')

    xmax = pts_of_max_int[:, 0]
    ymax = pts_of_max_int[:, 1]
    # fit circle through pts:
    xc, yc, r, _ = cf.least_squares_circle(np.array([ymax, xmax]).transpose())
    if r < settings['minRad'] or r > settings['maxRad']:
        # if found radius outside of defined range, set to zero
        r = np.nan

    if showplot:
        axs2.scatter(ymax, xmax, c='r')
        # circle from hough:
        if prev_result is not None:
            c = plt.Circle((prev_result[0], prev_result[1]), prev_result[2], fill=False, color='red',
                           linestyle='--', linewidth=3)
            axs2.add_artist(c)
        # circle newly found:
        if r is not np.nan:
            c = plt.Circle((xc, yc), r, fill=False, color='black', linewidth=3)
            axs2.add_artist(c)
            axs2.scatter(xc, yc, c='g', marker='+', s=20000)

    lx = np.shape(sc_img)[0]
    ly = np.shape(sc_img)[1]
    dx = min(abs(lx-xc), lx)-1
    dy = min(abs(ly-yc), ly)-1

    cropnew=False
    if cropnew:
        return_img = sc_img[int(yc - dy):int(yc + dy), int(xc - dx):int(xc + dx)]
        # translate coordinates of new circle to new image:
        xc = xc - (xc - dx)
        yc = yc - (yc - dy)
    else:
        return_img = sc_img

    if showplot:
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

        # print preview of new image and plot newly found circle in there (Note the displacement)
        if r is not np.nan:
            axs3.imshow(return_img)
            c = plt.Circle((xc, yc), r, fill=False, color='black', linewidth=3)
            axs3.add_artist(c)
            plt.show()

    return return_img, [xc, yc, r]
