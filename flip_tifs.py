import fabio
import numpy as np
from PIL import Image
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
        self.data_flip = None

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

    def low_pass_filter(self, keep_fraction):
        print(f'\nAppling low pass filter with fractional cut off of {keep_fraction}')
        plt.figure()
        plt.imshow(self.data_flip)
        data_fft = fftpack.fft2(self.data_flip)
        data_fft2 = data_fft.copy()

        def plot_spectrum(data_fft):
            from matplotlib.colors import LogNorm
            plt.imshow(np.abs(data_fft), norm=LogNorm(vmin=5))
            plt.colorbar()
        plt.figure()
        plot_spectrum(data_fft)

        r, c = data_fft2.shape
        """set all rows with indices between r*keep_fraction and r*(1-keep_fraction) to 0"""
        data_fft2[int(r*keep_fraction):int(r*(1-keep_fraction))] = 0
        # data_fft2[0:int(r * keep_fraction)] = 0
        """now with columns"""
        data_fft2[:, int(c * keep_fraction):int(c*(1-keep_fraction))] = 0
        # data_fft2[:, 0:int(c * keep_fraction)] = 0

        plt.figure()
        plot_spectrum(data_fft2)

        self.data_flip = fftpack.ifft2(data_fft2).real

        plt.figure()
        plt.imshow(self.data_flip)

        plt.show()
        
    def gaussian_filter(self, filtering):
        self.data_flip = ndimage.gaussian_filter(self.data_flip, filtering)


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
            self.data_flip = np.flip(data)
            #if self.flip_entry.get():
            if 1:
                self.low_pass_filter(.1)
                # self.gaussian_filter(4)
            fname = filename[:filename.find('.')]       # strip everything after the first '.'
            save_name = f'{self.output_entry.get()}{os.sep}{fname}_flip-d.tif'
            Image.fromarray(self.data_flip).save(save_name)
        self.killWindow()

    def killWindow(self):
        self.destroy()

if __name__ == '__main__':
    Setup_Window().mainloop()