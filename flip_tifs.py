import fabio
import numpy as np
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import filedialog
import os
import glob
from scipy import fftpack, ndimage
import matplotlib.pylab as plt


class Setup_Window(tk.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'
    default_data_path = f'{os.getcwd()}{os.sep}raw_data{os.sep}unflipped'
    default_output_path = f'{os.getcwd()}{os.sep}raw_data'

    def __init__(self):
        """Set up Window"""

        tk.Tk.__init__(self)
        self.title('Select TIFFs to rotate by pi')

        """Create and place labels"""
        columns = 3

        r = 0

        """Directory location"""

        tk.Label(self, text='Directory with files to flip: ',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)
        self.path_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.path_entry.grid(row=r, column=1, columnspan=3, sticky=tk.E + tk.W)

        self.path_entry.insert(0, Setup_Window.default_data_path)

        tk.Button(self, text='...', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.dir_select).grid(row=r, column=4, sticky=tk.E + tk.W)

        r += 1

        """output location"""

        tk.Label(self, text='Directory to save to: ',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)
        self.output_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.output_entry.grid(row=r, column=1, columnspan=3, sticky=tk.E + tk.W)

        self.output_entry.insert(0, Setup_Window.default_output_path)

        tk.Button(self, text='...', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.out_select).grid(row=r, column=4, sticky=tk.E + tk.W)

        r += 1

        """All or Some"""

        self.all_files_bool = tk.IntVar(self)

        self.all_files_bool.set(1)

        tk.Radiobutton(self, text='All files in directory', variable=self.all_files_bool, value=1,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1)
        tk.Radiobutton(self, text='Just the following files', variable=self.all_files_bool, value=0,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=2)

        r += 1

        """The some files"""
        self.files_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.files_entry.grid(row=r, column=0, columnspan=columns, sticky=tk.E + tk.W)
        self.files_entry.insert(0, "separate file names with ', ' or click the '...' -->")
        tk.Button(self, text='...', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.file_select).grid(row=r, column=4, sticky=tk.E + tk.W)

        r += 1

        """GO"""
        tk.Button(self, text='START FLIPPING', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.start_flipping).grid(row=r, column=columns-2, columnspan=2, sticky=tk.E + tk.W)

        r += 1
        tk.Label(self, text='2021 Teddy Tortorici',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        columnspan=columns,
                                                                        sticky=tk.E + tk.W)

    def dir_select(self):
        """Opens dialog box to select directory where the TIFFs you'd like to flip are."""
        init_dir = self.path_entry.get()
        path = filedialog.askdirectory(initialdir=init_dir, title='Select Working Directory')
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)

    def out_select(self):
        """Opens dialog box to select directory where the TIFFs will be saved after flipping"""
        init_out = self.output_entry.get()
        output = filedialog.askdirectory(initialdir=init_out, title='Where to save files')
        self.output_entry.delete(0, tk.END)
        self.path_entry.insert(0, output)

    def file_select(self):
        """Opens dialog box to select files and the pastes the names into the entry box
        This will change the directory entry box as well if you move directories here."""
        files_init = filedialog.askopenfilenames(initialdir=self.path_entry.get(), title='Select Files to Flip',
                                                 filetypes=(('TIFFs', '*.tif',), ('all', '*.*')))
        files = [''] * len(files_init)
        path = files_init[0][:files_init[0].rfind('/')]
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, path)

        for ii, f in enumerate(files_init):
            files[ii] = f.split('/')[-1]
        self.files_entry.delete(0, tk.END)
        self.files_entry.insert(0, str(files).strip('[').strip(']').replace("'", ''))

    def low_pass_filter(self, data):
        fft1 = fftpack.fftshift(fftpack.fft2(data))

        y, x = data.shape

        r = y / 1.5                                                     # Size of circle
        bbox = ((x - r) / 2, (y - r) / 2, (x + r) / 2, (y + r) / 2)     # Create a box

        low_pass = Image.new("L", (x, y), color=0)

        draw1 = ImageDraw.Draw(low_pass)
        draw1.ellipse(bbox, fill=1)

        low_pass_array = np.array(low_pass)
        filtered = np.multiply(fft1, low_pass_array)

        ifft2 = np.real(fftpack.ifft2(fftpack.ifftshift(filtered)))
        ifft2 = np.maximum(0, np.minimum(ifft2, 255))
        return ifft2.astype('int32')

    def gaussian_filter(self, data, sigma):
        return ndimage.gaussian_filter(data, sigma).astype('int32')

    def find_zingers(self, image, cut_off, gaus_std):
        # smoothed_img = self.low_pass_filter(image)
        smoothed_img = self.gaussian_filter(image, gaus_std)
        print(f'average value of data is {np.average(image)}, but {np.average(smoothed_img)} after smoothing.')
        dif_img = np.subtract(smoothed_img, image)

        # print('\nsample from data')
        # starty = 248
        # startx = 1567
        # look_range = 12
        # print(image[starty:starty + look_range, startx:startx + look_range])
        # print('\nsame range smoothed')
        # print(smoothed_img[starty:starty + look_range, startx:startx + look_range])
        # print('\ndifferences')
        # print(dif_img[starty:starty + look_range, startx:startx + look_range])
        print(f'{image.shape[0] * image.shape[1]} pixels in data')
        # print(f'{np.sum(smoothed_img == 0)} zeros in smoothed data')
        # print(f'{np.sum(dif_img == 0)} zeros in dif')
        # print(f'{np.sum(dif_img < 0)} negative numbers in dif')
        zinger_chart = dif_img / (smoothed_img + 1)
        # print(anomalies[starty:starty + look_range, startx:startx + look_range])
        anomalies1 = zinger_chart < -cut_off
        anomalies2 = zinger_chart > cut_off
        anomalies = anomalies1 | anomalies2
        print(f'Found {np.sum(anomalies)} zingers')
        return anomalies.astype('int32')

    def remove_zingers(self, image, cut_off, gaus_std):
        zingers = self.find_zingers(image, cut_off, gaus_std)
        zinger_locs = np.where(zingers)
        max_r, max_c = image.shape
        for row, col in zip(zinger_locs[0], zinger_locs[1]):
            up = row - 2
            down = (row + 2) % max_r
            left = col - 2
            right = (col + 2) % max_c
            image[row, col] = np.average((image[up, col], image[down, col],
                                          image[row, left], image[row, right]))
        return image


    def start_flipping(self):
        """Get values from box"""
        os.chdir(self.path_entry.get())     # change current working directory
        print(f'\nTaking files from:\n    {os.getcwd()}')
        if self.all_files_bool.get():
            filenames = glob.glob('*.tif')
        else:
            filenames = self.files_entry.get().split(', ')
        print('\nFlipping the following files:')
        for filename in filenames:
            print(f'    {filename}')
            data = fabio.open(filename).data
            data_flip = np.flip(data)
            for _ in range(3):
                data_flip = self.remove_zingers(data_flip, 1.2, 3)
            fname = filename[:filename.find('.')]       # strip everything after the first '.'
            save_name = f'{self.output_entry.get()}{os.sep}{fname}_flip-dz.tif'
            Image.fromarray(data_flip).save(save_name)
        self.killWindow()

    def killWindow(self):
        self.destroy()

if __name__ == '__main__':
    Setup_Window().mainloop()
