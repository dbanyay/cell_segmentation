import numpy as np
import roifile
from matplotlib import pyplot as plt
import cv2
from pathlib import Path
from zipfile import ZipFile
from scipy.stats import ttest_ind
from collections import Counter

class IntensityMetrics:
    mean = 'mean'
    min = 'min'
    max = 'max'
    intDen = 'IntDen'


def save_contour_roi(contours=None,
                     out_path='',
                     tiff_path=''):
    zip_obj = ZipFile(out_path / (str(tiff_path.stem) + '.zip'), 'w')
    cntr = 0
    for contour in contours:
        roi = roifile.ImagejRoi.frompoints(contour[:, 0, :])
        tmp_path = str(Path.cwd() / 'tmp' / (str(cntr) + '.roi'))
        roi.tofile(tmp_path)
        zip_obj.write(tmp_path)
        Path.unlink(Path(tmp_path))
        cntr += 1
    zip_obj.close()


def get_masked_points(contours='', img_channel=None, intensity_metric=IntensityMetrics.mean):

    cells = np.zeros(255, dtype=np.int)

    for i in range(len(contours)):
        cimg = np.zeros_like(img_channel)

        # Create a mask image that contains the contour filled in
        cv2.drawContours(cimg, contours, i, color=255, thickness=-1)

        # Access the image pixels and create a 1D numpy array then add to list
        mask = np.where(cimg == 255)
        points = img_channel[mask[0], mask[1]]
        points = points[points > 70]
        points_hist = Counter(points)

        for key in list(points_hist.keys()):
            cells[key] += points_hist[key]

    # results[i]['area'] = cv2.contourArea(contours[i])
    # results[i]['min'] = np.min(points)
    # results[i]['max'] = np.max(points)
    # results[i]['mean'] = np.mean(points)
    # results[i]['IntDen'] = results[i]['mean'] * results[i]['area']
    #
    # intensity_metric_value = [result[intensity_metric] for result in results.values()]

    return cells


def find_contours(img, blur_kernel_size=5, area_threshold=1000, color_threshold=100):
    # Gaussian blur image to eliminate sharp edges
    img_blurred = cv2.blur(img, (blur_kernel_size, blur_kernel_size))

    # create binary image
    img_blurred_tmp = img_blurred.copy()
    img_blurred_tmp[img_blurred_tmp < color_threshold] = 0
    img_blurred_tmp[img_blurred_tmp >= color_threshold] = 255

    # Find contours
    contours, hierarchy = cv2.findContours(img_blurred_tmp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

    # filter contours
    areas = np.array(
        [np.prod(np.max(contour[:, 0, :], axis=0) - np.min(contour[:, 0, :], axis=0)) for contour in
         contours])
    thresholded_idx = np.where(areas > area_threshold)[0]
    contours = [contours[i] for i in thresholded_idx]

    return contours


def blob_detector(tiff_file_path='',
                  save_images=False,
                  save_image_path='',
                  zip_output_path='',
                  green_threshold=10,
                  blue_threshold=20,
                  red_threshold=10,
                  area_threshold=1000,
                  intensity_metric=IntensityMetrics.mean):
    im = cv2.imread(str(tiff_file_path))

    red = im[:, :, 2]
    green = im[:, :, 1]
    blue = im[:, :, 0]

    # get green contours
    green_contours = find_contours(green, blur_kernel_size=20, area_threshold=area_threshold,
                                   color_threshold=green_threshold)
    # get green contoured red points
    cell_averages = get_masked_points(contours=green_contours, img_channel=red, intensity_metric=IntensityMetrics.mean)

    # get blue contours
    blue_contours = find_contours(blue, blur_kernel_size=5, area_threshold=500, color_threshold=75)

    # save image
    im_copy = im.copy()
    cv2.drawContours(im_copy, green_contours, -1, (0, 255, 255), 3)
    cv2.drawContours(im_copy, blue_contours, -1, (255, 0, 0), 3)

    cell_sum = 0
    cell_num = 0

    for i in range(len(cell_averages)):
        cell_sum += cell_averages[i] * i
        cell_num += cell_averages[i]


    # add avg red intensity
    text = f'Average red intensity: {cell_sum/cell_num:.1f}'
    cv2.putText(img=im_copy, text=text, org=(10, im_copy.shape[1] - 10), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL,
                fontScale=1,
                color=(0, 0, 255))

    # setup text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = '/'.join(tiff_file_path.parts[-4:])

    # get boundary of this text
    textsize = cv2.getTextSize(text, font, 1, 2)[0]

    # get coords based on boundary
    textX = int((im_copy.shape[1] - textsize[0]) / 2)
    textY = int(textsize[1] * 1.2)

    cv2.putText(img=im_copy, text=text, org=(textX, textY), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=1,
                color=(255, 255, 255))

    # Save image
    cv2.imwrite(f'{str(save_image_path / str(tiff_file_path.stem + "_segmented.png"))}', im_copy)

    # save contour to zip to be read with imageJ
    save_contour_roi(contours=green_contours, out_path=zip_output_path, tiff_path=tiff_file_path)

    return cell_averages
