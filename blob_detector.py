import numpy
from pathlib import Path
import numpy as np
import roifile
from matplotlib import pyplot as plt
import cv2
import os


def thresh_callback(val):
    threshold = val
    # Detect edges using Canny
    canny_output = cv2.Canny(green_blurred, threshold, threshold * 3,L2gradient=True, apertureSize=3)


    # Find contours
    contours, hierarchy = cv2.findContours(green_blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

    # filter contours
    areas = np.array([np.prod(np.max(contour[:, 0, :], axis=0) - np.min(contour[:, 0, :], axis=0)) for contour in contours])
    thresholded_idx = np.where(areas > area_threshold)[0]
    contours = [contours[i] for i in thresholded_idx]

    image_path_str = str(image_path)
    image_path_str = image_path_str[:image_path_str.rfind('.')]
    os.mkdir(image_path_str)

    cntr = 0
    for contour in contours:
        roi = roifile.ImagejRoi.frompoints(contour[:, 0, :])
        roi.tofile(image_path_str + '/' + str(cntr) + '.roi')
        cntr += 1


    # Draw contours
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    for i in range(len(contours)):
        color = (0,0,255)
        cv2.drawContours(drawing, contours, i, color, 2, cv2.LINE_8, hierarchy, 0)
    # Show in a window
    cv2.imshow('Contours', drawing)

image_path = Path('C:/Users/Daniel/Desktop/Andi project/ATCC/CsT/IFITM1-pos/Snap-3109.tiff')



im = cv2.imread(str(image_path))

red = im[:,:,2]
green = im[:,:,1]
blue = im[:,:,0]

green[green > 50] = 25

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

green_blurred = cv2.blur(green, (20,20))
green_blurred = cv2.equalizeHist(green_blurred)
green_blurred[green_blurred < 220] = 0
green_blurred[green_blurred >= 220] = 255

area_threshold = 5000


# Create Window
source_window = 'Source'
cv2.namedWindow(source_window)
cv2.imshow(source_window, green_blurred)
max_thresh = 255
thresh = 12 # initial threshold
cv2.createTrackbar('Canny Thresh:', source_window, thresh, max_thresh, thresh_callback)
thresh_callback(thresh)
cv2.waitKey()

