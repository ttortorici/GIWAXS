import tkinter as tk
from tkinter import filedialog
import os
import fabio
import numpy as np
import matplotlib.pyplot as plt
import pylab
from pylab import MultipleLocator, savefig, mpl
import matplotlib.gridspec as gridspec
import pygix


"""Globals that the setup window will alter and then get deleted after use"""
sample_orientation_g = -1
incident_angle_g = -1.
cal_path_g = ''
data_path_g = ''
filename = ''


def main():
    Setup_Window().mainloop()

    pg = load_calibration()
    data = dezingering(load_data(), threshold_multiplier=2, attempts=3)

    plot_line_cuts(pg)

    # font1 = {'color':  'black','size': 25}
    font1 = {'family': 'Arial', 'color': 'black', 'weight': 'bold', 'size': 30}
    i, qxy, qz = pg.transform_reciprocal(data, correctSolidAngle=True, method="bbox")
    i[i == 0] = np.nan

    # close('all')
    fig = pylab.figure(figsize=(6, 6))
    gs = gridspec.GridSpec(1, 1)
    ax1 = plt.subplot(gs[0, 0])
    for ax in fig.get_axes():
        ax.tick_params(which='both', color='k', labelsize=20)
        ax.set_facecolor('k')
        ax1.yaxis.set_ticks_position('both')
        ax1.xaxis.set_ticks_position('both')
        # play with norm to get color scale right
        norm = mpl.colors.Normalize(vmin=0, vmax=200)
    # norm = mpl.colors.SymLogNorm(linthresh=0.1, vmin=np.min(i), vmax=np.max(i))
    ax1.imshow(i, norm=norm, cmap='turbo', extent=(np.min(qxy) / 10, np.max(qxy) / 10, np.min(qz) / 10,
                                                   np.max(qz) / 10), origin='lower')
    # ax1.imshow(np.log(i), extent=(np.min(qxy)/10, np.max(qxy)/10, np.min(qz)/10,
    #                              np.max(qz)/10)
    #           , vmax=7.0, vmin=3.0, cmap='jet', origin='lower')
    pylab.ylim([-0.1, 2.5])
    pylab.xlim([-2, 2])
    ax1.xaxis.set_tick_params(width=1.5, length=5)
    ax1.yaxis.set_tick_params(width=1.5, length=5)
    ax1.set_xlabel('$q_{xy}$ ($\AA^{-1}$)', fontsize=16)
    ax1.set_ylabel('$q_{z}$ ($\AA^{-1}$)', fontsize=16)
    # norm = mpl.colors.Normalize(vmin=0,vmax=10) # colorbar range
    # sm = plt.cm.ScalarMappable(cmap='turbo',norm=norm)
    # sm.set_array([])
    # # cb = plt.colorbar(sm,ticks=np.linspace(6,3,4),fraction=0.046,pad=0.04)
    # # cb.set_label(label='log(intensity)', fontdict=font1)
    # divider = make_axes_locatable(ax)
    # cax = divider.append_axes("right", size="5%", pad=0.08)
    # cb = colorbar(sm, cax=cax)
    # cb.set_label(label='Intensity (arb. units)', fontdict=font1)
    ending = '_2D.png'
    filename2D = 'processed_data' + os.sep + filename + ending

    savefig(filename2D, bbox_inches='tight', dpi=600)

    ending = '.csv'
    filenamecsv = filename + ending

    '''with open(filenamecsv.format(dataFile), "w+") as f:
        l = [q, i_ip, i_oop]
        a = zip(*l)
        writer = csv.writer(f)
        writer.writerow(["Q (1/A)", "Intensity in plane (a.u.)", "Intensity out of plane (a.u.)"])
        for values in zip_longest(*l):
            writer.writerow(values)'''


def sector_cut(pg, data, chi_center=0, chi_width=180., radial_range=(0, 2.5), filename=''):
    """This saves a plot of a line cut using pygic
    pg - calibration object
    data - tif data set
    chi_center - azimuthal angle starting on the z axis and moving clockwise positive [degrees]
    chi_width = total angle of cut centered around chi_center [degrees]"""
    i_linecut, q = pg.profile_sector(data, npt=1000, chi_pos=chi_center, chi_width=chi_width,
                                     radial_range=radial_range, unit='q_A^-1', correctSolidAngle=False, method='bbox')
    return q, i_linecut

def plot_ip_oop_whole():
    pass


def plot_line_cuts(q, i_oop, i_ip):
    global filename
    """this produces the line cuts using pygix
    chi_pos = azimuthal angle z=0 with clockwise positive [degrees]
    chi_width = total angle centered around chi_pos [degrees]
    radial_range = [q space]
    correctSolidAngle = always False
    method = 'bbox'"""
    # Out of plane
    i_oop, q = pg.profile_sector(data, npt=1000, chi_pos=0, chi_width=30,
                                 radial_range=(0, 2.5), unit='q_A^-1', correctSolidAngle=False, method="bbox")
    # In plane
    i_ip, _ = pg.profile_sector(data, npt=1000, chi_pos=78, chi_width=10,
                                radial_range=(0, 2.5), unit='q_A^-1', correctSolidAngle=False, method="bbox")

    fig = plt.figure()
    plt.xlabel('q ($\AA^{-1}$)')
    plt.ylabel('Intensity (a.u.)')
    # ###adjust xlim
    # plt.xlim((0.11, 2.2))
    # plt.ylim((10,50))
    plt.axes().xaxis.set_minor_locator(MultipleLocator(0.1))
    plt.axes().yaxis.set_minor_locator(MultipleLocator(1))
    plt.plot(q, i_oop, label="out of plane")
    plt.plot(q, i_ip, label="in plane")
    plt.legend()
    ending = 'lin_1D.png'
    filename1D = 'processed_data' + os.sep + 'filename' + ending
    savefig(filename1D, bbox_inches='tight', dpi=300)

    # log plots
    font2 = {'family': 'Arial', 'color': 'black', 'weight': 'bold', 'size': 20}
    fig = plt.figure()
    plt.xlabel('q ($\AA^{-1}$)')
    plt.ylabel('$log_{10}$ Intensity (a.u.)')
    plt.yscale('log')
    # plt.yticks(np.arange(1, 3, 5))
    # ###adjust ylim
    # plt.ylim((1.2, 3.5))
    plt.xlim((0.1, 2.2))
    # plt.xticks(np.arange(0.175, 2.175, 0.2))
    # plt.axes().xaxis.set_minor_locator(MultipleLocator(0.1))
    log_i_oop = np.log10(i_oop)
    log_i_ip = np.log10(i_ip)
    plt.plot(q, log_i_oop, label="out of plane")
    plt.plot(q, log_i_ip, label="in plane")
    plt.legend()

    savefig(f'processed_data{os.sep}{filename}log_1D.png', bbox_inches='tight', dpi=300)


def load_calibration():
    global cal_path_g, sample_orientation_g, incident_angle_g
    print('\n\n---------------CALIBRATING---------------')
    pg = pygix.Transform()
    pg.load(cal_path_g)

    print(f'\nCalibrating with:\n    {cal_path_g}')

    pg.sample_orientation = sample_orientation_g
    pg.incident_angle = incident_angle_g  # * np.pi / 180.
    pg.title_angle = 0

    sample_orientation = 'horizontal' if sample_orientation_g == 1 else 'vertical'
    print(f'\nWith a {sample_orientation} sample,')
    print(f'and an incident angle of {incident_angle_g}\u00B0')

    print(f'\nX-Ray wavelength is {pg._wavelength * 1e10} A')
    print(f'\nDetector-sample distance is {pg._dist * 1e3} mm')
    print(f'\nDetector pixel size is {pg.detector._pixel1 * 1e6} x {pg.detector._pixel2 * 1e6} \u03BCm')
    print(f'\nBeam center is ({pg._poni2 / pg.detector._pixel1}, {pg._poni1 / pg.detector._pixel2}) pixels')
    print(f'\nPoint of normal incidence is ({pg._poni1 * 1e3}, {pg._poni2 * 1e3}) mm')
    print(f'\nTilt angle is {pg._tilt_angle}\u00B0\n')
    del sample_orientation_g
    del incident_angle_g
    del cal_path_g
    return pg


def load_data():
    global data_path_g, filename
    print('\n\n---------------LOADING DATA---------------')
    data = fabio.open(data_path_g).data
    print(f'\nLoading data:\n    {data_path_g}\n')
    filename = data_path_g.replace('/', os.sep).split(os.sep)[-1].strip('.tif')
    del data_path_g
    return data


def get_file(ftype='tif', init_dir=os.getcwd()):
    """Opens dialog box to get location of desired file"""
    if not ftype.lower() in ['tif', 'poni']:
        raise ValueError('invalid filetype to retrieve')
    filename = filedialog.askopenfilename(initialdir=init_dir, title=f'Select {ftype.upper()}',
                                          filetypes=((f'{ftype.upper()}', f'*.{ftype.lower()}',), ('all', '*.*')))
    return filename


def dezingering(data, threshold_multiplier=2, attempts=3):
    print('\n---------------DEZINGERING DATA----------------')
    check = 0
    len_x, len_y = np.shape(data)
    look = 2

    """Shaper is a star burst cross of 1s with 0s in the corners and center. This grabs the nearest neighbors of
    distance: look.
    eg [[0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [1, 1, 0, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0]"""
    shaper = np.ones((2 * look + 1, 2 * look + 1))
    for i1 in range(2 * look + 1):
        for j1 in range(2  * look + 1):
            if abs(look - i1) + abs(look - j1) > look:
                shaper[i1, j1] = 0.
    shaper[look, look] = 0.

    for attempt in range(attempts):
        for i2 in range(look, len_x - look):
            for j2 in range(look, len_y - look):
                """Collects the values of the nearest neighbors"""
                neighbors = data[i2 - look: i2 + look + 1, j2 - look: j2 + look + 1] * shaper

                """Bool list takes the surrounding points to check if they're much bigger than their surroundings.
                Will be a list of False if everything is fine"""
                bool_list = data[i2, j2] * shaper > threshold_multiplier * neighbors
                #print(data[i2 - look: i2 + look + 1, j2 - look: j2 + look + 1])
                #print(bool_list)

                """np.sum(bool_list) will be 0 if all data points are fine"""
                if np.sum(bool_list):
                    data[i2, j2] = (data[i2 - 1, j2] + data[i2 + 1, j2] + data[i2, j2 - 1] + data[i2, j2 + 1]) / 4.
                    check += 1
        print(f'Dezingering applied {attempt  + 1} times and smoothed {check} times total.')
    return data


class Setup_Window(tk.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'
    default_angle = '0.12'      # degrees
    default_calibration_path = os.getcwd() + os.sep + 'calibration'
    default_calibration_fname = 'agbh.poni'
    default_data_path = os.getcwd() + os.sep + 'raw_data'
    default_data_fname = 'TT5mm-01-benzeneTPP_60min_flip.tif'

    def __init__(self):
        """Set up Window"""

        tk.Tk.__init__(self)
        self.title('Setup')

        """Create and place labels"""
        columns = 3

        r = 0

        """Title Line"""
        tk.Label(self, text='Set up analysis',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        columnspan=columns,
                                                                        sticky=tk.W)

        r += 1

        """Sample orientation"""
        tk.Label(self, text='Sample Orientation',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)

        self.orientation_selection = tk.IntVar(self)

        self.orientation_selection.set(1)

        tk.Radiobutton(self, text='Horizontal', variable=self.orientation_selection, value=1,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1)
        tk.Radiobutton(self, text='Vertical', variable=self.orientation_selection, value=2,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=2)

        tk.Label(self, text='                                                                  ',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=3, sticky=tk.W)

        r += 1

        """Incident Angle"""
        tk.Label(self, text='Incident Angle [\u00B0]',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)
        self.angle_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.angle_entry.grid(row=r, column=1, columnspan=2, sticky=tk.E + tk.W)
        self.angle_entry.insert(0, Setup_Window.default_angle)

        r += 1

        """Calibration location"""

        tk.Label(self, text='Calibration',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)
        self.calibration_path_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.calibration_path_entry.grid(row=r, column=1, columnspan=3, sticky=tk.E + tk.W)

        calibration_path = Setup_Window.default_calibration_path + os.sep + Setup_Window.default_calibration_fname
        self.calibration_path_entry.insert(0, calibration_path)

        tk.Button(self, text='...', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.open_cal).grid(row=r, column=4, sticky=tk.E + tk.W)

        r += 1

        """Data location"""

        tk.Label(self, text='Data',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)
        self.data_path_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.data_path_entry.grid(row=r, column=1, columnspan=3, sticky=tk.E + tk.W)

        data_path = Setup_Window.default_data_path + os.sep + Setup_Window.default_data_fname
        self.data_path_entry.insert(0, data_path)

        tk.Button(self, text='...', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.open_data).grid(row=r, column=4, sticky=tk.E + tk.W)

        r += 1

        """GO"""
        tk.Button(self, text='Analyze', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.analyze).grid(row=r, column=columns-2, columnspan=2, sticky=tk.E + tk.W)

        r += 1
        tk.Label(self, text='2021 Teddy Tortorici',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        columnspan=columns,
                                                                        sticky=tk.E + tk.W)

    def open_cal(self):
        calibration_path = get_file(ftype='poni', init_dir=Setup_Window.default_calibration_path)
        self.calibration_path_entry.delete(0, tk.END)
        self.calibration_path_entry.insert(0, calibration_path)

    def open_data(self):
        data_path = get_file(ftype='tif', init_dir=Setup_Window.default_data_path)
        self.data_path_entry.delete(0, tk.END)
        self.data_path_entry.insert(0, data_path)

    def analyze(self):
        global sample_orientation_g, incident_angle_g, cal_path_g, data_path_g
        """Get values from box"""
        sample_orientation_g = int(self.orientation_selection.get())
        incident_angle_g = float(self.angle_entry.get())
        cal_path_g = self.calibration_path_entry.get()
        data_path_g = self.data_path_entry.get()

        self.killWindow()

    def killWindow(self):
        self.destroy()


if __name__ == '__main__':
    main()
