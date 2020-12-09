from pathlib import Path
from blob_detector import blob_detector
from time import time
import numpy as np

time_start = time()
path = Path('C:/Users/Daniel/Desktop/Andi project/ATCC')
save_images = True
green_threshold = 10

output_path = path / 'output_segments'
Path.mkdir(output_path, exist_ok=True)
if save_images == True:
    save_image_path = path / 'output_images'
    Path.mkdir(save_image_path, exist_ok=True)

pos_avg_intensity = []
neg_avg_intensity = []


for tiff_file_path in path.glob('**/*.tiff'):
    if 'h0t0z' not in str(tiff_file_path) and 'merge' not in str(tiff_file_path):
        print(f'Processing {tiff_file_path}...')

        avg_intensity = blob_detector(tiff_file_path=tiff_file_path,
                                      save_images=save_images,
                                      save_image_path=save_image_path,
                                      zip_output_path=output_path,
                                      green_threshold=green_threshold)

        if 'pos' in str(tiff_file_path):
            pos_avg_intensity.append(avg_intensity)
        elif 'neg' in str(tiff_file_path):
            neg_avg_intensity.append(avg_intensity)

print(f'\n\nPOS average intensity: {np.mean(pos_avg_intensity):.1f}')
print(f'NEG average intensity: {np.mean(neg_avg_intensity):.1f}')

relative_difference = (np.mean(pos_avg_intensity) - np.mean(neg_avg_intensity)) / (np.mean(pos_avg_intensity) + np.mean(neg_avg_intensity)) *100
print(f'Relative difference (pos-neg): {relative_difference:.1f}%')



print(f'\nTotal time elapsed: {time() - time_start:.1f}s')
