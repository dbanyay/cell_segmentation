from pathlib import Path
from blob_detector import blob_detector, IntensityMetrics
from time import time
import numpy as np
from scipy.stats import ttest_ind, norm
from matplotlib import pyplot as plt

time_start = time()
path = Path('C:/Users/Daniel/Desktop/Andi project/ATCC')
save_images = True
green_threshold = 10

output_path = path / 'output_segments'
Path.mkdir(output_path, exist_ok=True)
if save_images == True:
    save_image_path = path / 'output_images'
    Path.mkdir(save_image_path, exist_ok=True)

pos_points_list = []
neg_points_list = []

for tiff_file_path in path.glob('**/*.tiff'):
    if 'h0t0z' not in str(tiff_file_path) and 'merge' not in str(tiff_file_path):
        print(f'Processing {tiff_file_path}...')

        points = blob_detector(tiff_file_path=tiff_file_path,
                               save_images=save_images,
                               save_image_path=save_image_path,
                               zip_output_path=output_path,
                               green_threshold=green_threshold,
                               intensity_metric=IntensityMetrics.mean)

        if '-pos' in str(tiff_file_path):
            pos_points_list.append(points)
        elif '-neg' in str(tiff_file_path):
            neg_points_list.append(points)

# trick to flatten 2d list
pos_points = np.array(sum(pos_points_list, []))
neg_points = np.array(sum(neg_points_list, []))

# filter out non-contour paint values
pos_points = pos_points[pos_points > 70]
neg_points = neg_points[neg_points > 70]

pos_mean = np.mean(pos_points)
neg_mean = np.mean(neg_points)

pos_std = np.std(pos_points)
neg_std = np.std(neg_points)

print(f'\n\nPOS average intensity: {pos_mean:.1f}+-{pos_std:.1f}')
print(f'NEG average intensity: {neg_mean:.1f}+-{neg_std:.1f}')

relative_difference = (pos_mean - neg_mean) / (pos_mean + neg_mean) * 100
print(f'Relative difference (pos-neg): {relative_difference:.1f}%')

ttest, pval = ttest_ind(neg_points, pos_points, equal_var=False)
print("p-value", pval)

print(f'\nTotal time elapsed: {time() - time_start:.1f}s')

plt.subplot(211)
x_pos = np.linspace(0, 255, 100)
y_pos = norm.pdf(x_pos, pos_mean, pos_std)

x_neg = np.linspace(0, 255, 100)
y_neg = norm.pdf(x_neg, neg_mean, neg_std)

plt.plot(x_pos, y_pos, color='green')
plt.plot(x_neg, y_neg, color='red')
plt.legend(['pos', 'neg'])
plt.title('Pixel intensity distribution')

plt.subplot(212)
plt.boxplot([pos_points, neg_points])
plt.xticks([1, 2], ['pos', 'neg'])
plt.title('Pixel intensity distribution')

plt.show()
