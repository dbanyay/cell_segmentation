from pathlib import Path
from zipfile import ZipFile
import roifile
import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar

root = tk.Tk()
root.withdraw()

folder_path = Path(filedialog.askdirectory(title="Select folder with the outline.txt files..."))

progress_bar_window = tk.Tk()
progress_bar_window.title("Processing files...")
progress_bar_window.geometry('600x100')

num_files = len(list(folder_path.glob('*outlines.txt')))
bar = Progressbar(progress_bar_window, length=500)
bar['value'] = 0
bar['maximum'] = 500

bar.update()
bar.grid(column=0, row=0)
bar.pack()

file_cntr = 1
for file_path in folder_path.glob('*outlines.txt'):

    with open(file_path, 'r') as textfile:
        tmp_folder_path = file_path.parent / "tmp"
        tmp_folder_path.mkdir(exist_ok=True)

        # initialize zip file object
        zip_obj = ZipFile(file_path.parent / (str(file_path.stem) + '.zip'), 'w')

        line_cntr = 0
        for line in textfile:
            try:
                xy_list = list(map(int, line.rstrip().split(',')))
                x = xy_list[::2]
                y = xy_list[1::2]

                xy = [(x_new, y_new) for x_new, y_new in zip(x, y)]

                roi = roifile.ImagejRoi.frompoints(xy)
                tmp_path = tmp_folder_path / (str(line_cntr) + '.roi')
                roi.tofile(str(tmp_path))
                zip_obj.write(tmp_path)
                Path.unlink(Path(tmp_path))
                line_cntr += 1
            except:
                print(f'Could not read {str(file_path)}')
        zip_obj.close()
        tmp_folder_path.rmdir()

    file_path.unlink()

    bar['value'] = int(file_cntr / num_files * 500)
    progress_bar_window.update()
    file_cntr += 1
