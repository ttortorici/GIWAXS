import tkinter as tk
import numpy as np
import pygix
import pyFAI


def start():
    Setup_Window().mainloop()


class Setup_Window(tk.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'
    default_pixelsize = '75'            # micron
    default_wavelength = '1.54185'      # Angstroms
    default_x_center = '1500'           # Pixels
    default_y_center = '825'            # Pixels
    default_detdist = '168'             # millimeters

    def __init__(self):
        """Set up Window"""

        tk.Tk.__init__(self)
        self.title('Calibrate PONI File')

        """Create and place labels"""
        columns = 4

        r = 0

        """Title Line"""
        tk.Label(self, text='Put in detector and beam information to calibrate .poni',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        columnspan=columns,
                                                                        sticky=tk.W)

        r += 1

        """PONI Name"""
        tk.Label(self, text='Name the calibration file',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        columnspan=2,
                                                                        sticky=tk.W)

        self.filename_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.filename_entry.grid(row=r, column=2, columnspan=columns-2, sticky=tk.E + tk.W)
        self.filename_entry.insert(0, 'cal.poni')

        """Pixel size"""
        tk.Label(self, text='Pixel dimensions (x,y) [\u03BCm]',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        sticky=tk.W)

        self.x_pixelsize_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.x_pixelsize_entry.grid(row=r, column=1, sticky=tk.E + tk.W)
        self.x_pixelsize_entry.insert(0, Setup_Window.default_pixelsize)

        self.y_pixelsize_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.y_pixelsize_entry.grid(row=r, column=2, sticky=tk.E + tk.W)
        self.y_pixelsize_entry.insert(0, Setup_Window.default_pixelsize)

        r += 1

        """X-Ray wavelength"""
        tk.Label(self, text='X-ray wavelength [\u212B]',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        sticky=tk.W)

        self.wavelength_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.wavelength_entry.grid(row=r, column=1, columnspan=columns - 1, sticky=tk.E + tk.W)
        self.wavelength_entry.insert(0, Setup_Window.default_wavelength)

        r += 1

        """Center Pixel"""
        tk.Label(self, text='Pixel Coord of Beam center (x,y) [pixels]').grid(row=r,
                                                                              column=0,
                                                                              sticky=tk.W)

        self.x_center_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.x_center_entry.grid(row=r, column=1, sticky=tk.E + tk.W)
        self.x_center_entry.insert(0, Setup_Window.default_x_center)

        self.y_center_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.y_center_entry.grid(row=r, column=2, sticky=tk.E + tk.W)
        self.y_center_entry.insert(0, Setup_Window.default_y_center)

        r += 1

        """Detector distance"""
        tk.Label(self, text='Distance between sample and detector [mm]').grid(row=r,
                                                                              column=0,
                                                                              sticky=tk.W)

        self.detdist_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.detdist_entry.grid(row=r, column=1, columnspan=columns-1, sticky=tk.E + tk.W)
        self.detdist_entry.insert(0, Setup_Window.default_detdist)

        r += 1

        """Detector rotations from sample view"""
        tk.Label(self, text='Detector-sample rotations [degrees]').grid(row=r,
                                                                        column=0,
                                                                        sticky=tk.W)

        self.rot1_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.rot1_entry.grid(row=r, column=1, sticky=tk.E + tk.W)
        self.rot1_entry.insert(0, '0')

        self.rot2_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.rot2_entry.grid(row=r, column=2, sticky=tk.E + tk.W)
        self.rot2_entry.insert(0, '0')

        self.rot3_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.rot3_entry.grid(row=r, column=3, sticky=tk.E + tk.W)
        self.rot3_entry.insert(0, '0')

        """GO"""
        tk.Button(self, text='Calibrate',
                  font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.calibrate).grid(row=r, column=columns-2, columnspan=2, sticky=tk.E + tk.W)

        r += 1
        tk.Label(self, text='2021 Teddy Tortorici',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(r=r,
                                                                        column=0,
                                                                        columnspan=columns,
                                                                        sticky=tk.E + tk.W)

    def calibrate(self):
        """Get values from box"""
        x_pixelsize = float(self.x_pixelsize_entry.get()) * 1e-6
        y_pixelsize = float(self.y_pixelsize_entry.get()) * 1e-6
        wavelength = float(self.wavelength_entry.get()) * 1e-10
        x_center = float(self.x_center_entry.get())
        y_center = float(self.y_center_entry.get())
        detdist = float(self.detdist_entry.get()) * 1e-3
        rot1 = float(self.rot1_entry.get()) * np.pi / 180.
        rot2 = float(self.rot2_entry.get()) * np.pi / 180.
        rot3 = float(self.rot3_entry.get()) * np.pi / 180.
        filename_temp = self.filename_entry.get()

        self.killWindow()

        if '.' in filename_temp:
            filename = filename_temp[:filename_temp.find('.')]
        filename += '.poni'


        detector = pyFAI.detectors.Detector(x_pixelsize, y_pixelsize)

        poni1 = y_center * x_pixelsize
        poni2 = x_center * y_pixelsize

        pg = pygix.Transform(dist=detdist, poni1=poni1, poni2=poni2,
                             rot1=rot1, rot2=rot2, rot3=rot3,
                             wavelength=wavelength, detector=detector)

        f = open(str(filename), "w")
        f.write(f'PixelSize1: {x_pixelsize}\n')
        f.write(f'PixelSize2: {y_pixelsize}\n')
        f.write(f'Distance: {detdist}\n')
        f.write(f'Poni1: {poni1}\n')
        f.write(f'Poni2: {poni2}\n')
        f.write(f'Rot1: {rot1}\n')
        f.write(f'Rot2: {rot2}\n')
        f.write(f'Rot3: {rot3}\n')
        f.write(f'Wavelength: {wavelength}')
        f.close()


    def killWindow(self):
        self.destroy()





