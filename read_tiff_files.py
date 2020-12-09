from pathlib import Path

path = Path('C:/Users/Daniel/Desktop/Andi project/ATCC')

for tiff_file_path in path.glob('**/*.tiff'):
    if 'h0t0z' not in str(tiff_file_path) and 'merge' not in str(tiff_file_path):
        print(f'file path: {tiff_file_path}')
