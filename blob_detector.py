import numpy as np
import roifile
from matplotlib import pyplot as plt
import cv2
from pathlib import Path
from zipfile import ZipFile


def save_contour_roi(contours=None,
                     out_path='',
                     tiff_path=''):

    zip_obj = ZipFile(out_path / (str(tiff_path.stem) + '.zip'),'w')
    cntr = 0
    for contour in contours:
        roi = roifile.ImagejRoi.frompoints(contour[:, 0, :])
        tmp_path = str(Path.cwd() / 'tmp' / (str(cntr) + '.roi'))
        roi.tofile(tmp_path)
        zip_obj.write(tmp_path)
        Path.unlink(Path(tmp_path))
        cntr += 1
    zip_obj.close()

def calculate_red_intensity(contours, red):

    for i in range(len(contours)):
        # Create a mask image that contains the contour filled in
        cimg = np.zeros_like(red)
        cv2.drawContours(cimg, contours, i, color=255, thickness=-1)

        # Access the image pixels and create a 1D numpy array then add to list
        pts = np.where(cimg == 255)
        avg_intensity = np.mean(red[pts[0], pts[1]])

    return avg_intensity


def blob_detector(tiff_file_path='',
                  save_images=False,
                  save_image_path='',
                  zip_output_path='',
                  green_threshold=10,
                  area_threshold=5000):
    im = cv2.imread(str(tiff_file_path))

    red = im[:, :, 2]
    green = im[:, :, 1]
    blue = im[:, :, 0]

    # Gaussian blur image to eliminate sharp edges
    green_blurred = cv2.blur(green, (20, 20))

    # create binary image
    green_blurred_tmp = green_blurred.copy()
    green_blurred_tmp[green_blurred_tmp < green_threshold] = 0
    green_blurred_tmp[green_blurred_tmp >= green_threshold] = 255

    # Find contours
    contours, hierarchy = cv2.findContours(green_blurred_tmp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

    # filter contours
    areas = np.array(
        [np.prod(np.max(contour[:, 0, :], axis=0) - np.min(contour[:, 0, :], axis=0)) for contour in contours])
    thresholded_idx = np.where(areas > area_threshold)[0]
    contours = [contours[i] for i in thresholded_idx]

    # calculate red intensity
    avg_red_intensity = calculate_red_intensity(contours, red)

    # save contour to zip to be read with imageJ
    save_contour_roi(contours=contours, out_path=zip_output_path, tiff_path=tiff_file_path)

    im_copy = im.copy()
    cv2.drawContours(im_copy, contours, -1, (0, 255, 255), 3)

    # Save image
    cv2.imwrite(f'{str(save_image_path / str(tiff_file_path.stem + "_segmented.png"))}', im_copy)

    return avg_red_intensity
