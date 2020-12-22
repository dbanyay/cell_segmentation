from pathlib import Path
from zipfile import ZipFile
import roifile
import numpy as np

file_name = Path("C:/Users/Daniel/Desktop/Andi project/ATCC/CsT/IFITM1-neg/Snap-3114_cp_outlines.txt")

with open(file_name, 'r') as textfile:
    tmp_folder_path = file_name.parent / "tmp"
    tmp_folder_path.mkdir(exist_ok=True)

    # initialize zip file object
    zip_obj = ZipFile(file_name.parent / (str(file_name.stem) + '.zip'), 'w')

    line_cntr = 0
    for line in textfile:
        xy_list = list(map(int, line.rstrip().split(',')))
        x = xy_list[::2]
        y = xy_list[1::2]

        xy = np.array([x, y]).transpose()

        roi = roifile.ImagejRoi.frompoints(xy)
        tmp_path = tmp_folder_path / (str(line_cntr) + '.roi')
        roi.tofile(str(tmp_path))
        zip_obj.write(tmp_path)
        Path.unlink(Path(tmp_path))
        line_cntr += 1
    zip_obj.close()
    tmp_folder_path.rmdir()

# rm.runCommand("Associate", "true")
# rm.runCommand("Show All with labels")
