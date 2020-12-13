from pathlib import Path
import numpy as np
import roifile
from matplotlib import pyplot as plt
import cv2
import os
from copy import deepcopy


def thresh_callback(val):
    threshold = val
    # Detect edges using Canny
    # canny_output = cv2.Canny(green_blurred, threshold, threshold * 3,L2gradient=True, apertureSize=3)

    green_blurred_tmp = deepcopy(green_blurred)
    green_blurred_tmp[green_blurred_tmp < threshold] = 0
    green_blurred_tmp[green_blurred_tmp >= threshold] = 255

    # Find contours
    contours, hierarchy = cv2.findContours(green_blurred_tmp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

    # filter contours
    areas = np.array(
        [np.prod(np.max(contour[:, 0, :], axis=0) - np.min(contour[:, 0, :], axis=0)) for contour in contours])
    thresholded_idx = np.where(areas > area_threshold)[0]
    contours = [contours[i] for i in thresholded_idx]

    # image_path_str = str(image_path)
    # image_path_str = image_path_str[:image_path_str.rfind('.')]
    # os.mkdir(image_path_str)
    #
    # cntr = 0
    # for contour in contours:
    #     roi = roifile.ImagejRoi.frompoints(contour[:, 0, :])
    #     roi.tofile(image_path_str + '/' + str(cntr) + '.roi')
    #     cntr += 1

    # Draw contours
    i = -1
    # im_copy = im.copy()
    im_copy = green_blurred_tmp.copy()

    # cv2.drawContours(im_copy, contours, -1, (255, 0, 0), 3)
    # Show in a window
    cv2.imshow('Contours', im_copy)


image_path = Path('C:/Users/Daniel/Desktop/Andi project/ATCC/ZL/IFITM1-pos/Snap-3093.tiff')

im = cv2.imread(str(image_path))

red = im[:, :, 2]
green = im[:, :, 1]
blue = im[:, :, 0]

plt.subplot(131)
plt.imshow(red)
plt.title('red')

plt.subplot(132)
plt.imshow(green)
plt.title('green')

plt.subplot(133)
plt.imshow(blue)
plt.title('blue')

plt.colorbar()

green_blurred = cv2.blur(red, (1, 1))
area_threshold = 0

# green_blurred = cv2.equalizeHist(green_blurred)
# green_blurred[green_blurred < 220] = 0
# green_blurred[green_blurred >= 220] = 255


# Create Window
source_window = 'Source'
cv2.namedWindow(source_window)
cv2.imshow(source_window, green_blurred)
max_thresh = 255
thresh = 10  # initial threshold
cv2.createTrackbar('Thresh:', source_window, thresh, max_thresh, thresh_callback)
thresh_callback(thresh)
cv2.waitKey()
