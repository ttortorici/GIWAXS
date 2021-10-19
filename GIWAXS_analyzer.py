import os
import glob
import numpy as np
import csv
import pylab
import matplotlib
import tkinter as tk
import matplotlib.pyplot as plt
pgf_with_rc_fonts = {"pgf.texsystem": "lualatex"}
matplotlib.rcParams.update(pgf_with_rc_fonts)
import matplotlib.gridspec as gridspec
from matplotlib import ticker
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pylab import *
import csv
import pickle
import os
from os import walk, path, makedirs
from scipy import interpolate
import re
from copy import deepcopy
from glob import glob
import timeit
from itertools import zip_longest
import pyFAI
from pyFAI.multi_geometry import MultiGeometry
from pyFAI.calibrant import get_calibrant
import pygix
#from pygix import transform
#from pygix.transform import ocl_azim_csr
#from pygix.transform import ocl_azim_lut
#from pygix.transform import ocl_sort
import fabio
# import pygix.plotting as pp
from pygix import plotting as ppl
import numpy as np
import matplotlib.pyplot as plt


def get_file(ftype='tif'):
    """Opens dialog box to get location of desired file"""
    if not ftype.lower() in ['tif', 'poni']:
        raise ValueError('invalid filetype to retrieve')

    filename = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title=f'Select {ftype.upper()}',
                                             filetypes=((f'{ftype.upper()}', f'*.{ftype.lower()}',), ('all', '*.*')))
    return filename


def load_calibration():
    poni = tk.filedialog.askopenfilename(initialdir=os.getcwd() + os.sep + 'calibrations',
                                         title='Select Calibration file',
                                         filetypes=(('PONI', '*.poni',), ('all', '*.*')))
    pg = pygix.Transform()
    pg.load(poni)
    print(pg)
    return pg


def start():
    Setup_Window().mainloop()


class Setup_Window(tk.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'
    default_angle = '0.12'      # degrees

    def __init__(self):
        """Set up Window"""

        tk.TK.__init__(self)
        self.title('Calibrate PONI File')

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
        tk.Label(self, text='How was the sample oriented in the beam?',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        sticky=tk.W)

        self.orientation_selection = tk.IntVar(self)
        self.orientation_selection.grid(row=r, column=1, columnspan=2, sticky=tk.E + tk.W)

        self.inst_selection.set(1)

        tk.Radiobutton(self, text='Horizontal', variable=self.orientation_selection, value=1,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1)
        tk.Radiobutton(self, text='Vertical', variable=self.orientation_selection, value=2,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=2)

        r += 1

        """Incident Angle"""
        tk.Label(self, text='Angle of incidence [degrees]',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        sticky=tk.W)
        self.angle_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.angle_entry.grid(row=r, column=1, sticky=tk.E + tk.W)
        self.angle_entry.insert(0, Setup_Window.default_angle)

        r += 1

        """GO"""
        tk.Button(self, text='Analyze',
                  font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.calibrate).grid(row=r, column=columns-2, columnspan=2, sticky=tk.E + tk.W)

        r += 1
        tk.Label(self, text='2021 Teddy Tortorici',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(r=r,
                                                                        column=0,
                                                                        columnspan=columns,
                                                                        sticky=tk.E + tk.W)

    def analyze(self):
        """Get values from box"""
        orientation = self.orientation_selection.get()

        self.killWindow()




    def killWindow(self):
        self.destroy()
















pg.sample_orientation = 1  # 1 is horizontal, 2 is vertical
print("Enter incident angle in degrees")
pg.incident_angle = float(input())  # indicent angle in deg

pg.tilt_angle = 0  # tilt angle of sample in deg (misalignment in "chi")



#Average all images in a folder

import os
import glob

# make sure this array is the same size as tif image.
# you can find this in pyFAI-calib2 tif_filename
array = np.zeros((1102,3070))
#set name for files to be averaged, X50*

#this pulls all tif files in the working directory
array = glob.glob(filename + '*' + '.tif')
data = []
output = {}
a = 0
output[a] = []
for i in array:
    dataFile = i
    data = fabio.open(dataFile).data
    data = np.flipud(data)
    data = np.fliplr(data)
    output[a] = data
    a = a + 1
print(a)

# print number of files opened
# for i in range(0, a):
# print(output[i])

# again make sure this is the same size as the tif image
sum0 = np.zeros((1102,3070))

# normalizing data
for i in range(0, a):
    sum1 = sum0 + output[i]
    sum0 = sum1

sum0_normalized = sum0/a
data = sum0_normalized




# line cuts and Plotting

plt.rcParams.update({'mathtext.default':  'regular' })
plt.rcParams['font.family'] = "sans-serif"
plt.rcParams['font.sans-serif'] = "Arial"
plt.rcParams['text.usetex'] = False
# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

# this produces the line cuts using pygix
i_oop, q = pg.profile_sector(data, npt=1000, chi_pos=0, chi_width=30,
  radial_range=(0, 2.5), unit='q_A^-1', correctSolidAngle=False, method="bbox")
i_ip, q = pg.profile_sector(data, npt=1000, chi_pos=78, chi_width=10,
  radial_range=(0, 2.5), unit='q_A^-1', correctSolidAngle=False, method="bbox")

### Dezingering oop and ip data with threshold ratio 2
threshold = 2
counter = 0
check_ip = 0
check_oop = 0
while counter <= 997:
    if (i_oop[counter] > threshold*i_oop[counter-2]) or\
            (i_oop[counter] > threshold*i_oop[counter+2]):
        i_oop[counter] = (i_oop[counter+2]+i_oop[counter-2])/2
        check_oop = check_oop+1
    if (i_ip[counter] > threshold*i_ip[counter-2]) or\
            (i_ip[counter] > threshold*i_ip[counter+2]):
        i_ip[counter] = (i_ip[counter+2]+i_ip[counter-2])/2
        check_ip=check_ip+1
    counter = counter + 1
# print(check_oop)
# print(check_ip)
### Dezinger round 2
counter = 0
while counter <= 997:
    if (i_oop[counter] > threshold*i_oop[counter-2]) or\
            (i_oop[counter] > threshold*i_oop[counter+2]):
        i_oop[counter] = (i_oop[counter+2]+i_oop[counter-2])/2
        check_oop = check_oop+1
    if (i_ip[counter] > threshold*i_ip[counter-2]) or\
            (i_ip[counter] > threshold*i_ip[counter+2]):
        i_ip[counter] = (i_ip[counter+2]+i_ip[counter-2])/2
        check_ip=check_ip+1
    counter = counter + 1
# print(check_oop)
# print(check_ip)
### Dezinger round 3
counter = 0
while counter <= 997:
    if (i_oop[counter] > threshold*i_oop[counter-2]) or\
            (i_oop[counter] > threshold*i_oop[counter+2]):
        i_oop[counter] = (i_oop[counter+2]+i_oop[counter-2])/2
        check_oop = check_oop+1
    if (i_ip[counter] > threshold*i_ip[counter-2]) or\
            (i_ip[counter] > threshold*i_ip[counter+2]):
        i_ip[counter] = (i_ip[counter+2]+i_ip[counter-2])/2
        check_ip=check_ip+1
    counter = counter + 1
# print(check_oop)
# print(check_ip)

fig = plt.figure()
plt.xlabel('q ($\AA^{-1}$)')
plt.ylabel('Intensity (a.u.)')
# ###adjust xlim
plt.xlim((0.11,2.2))
#plt.ylim((10,50))
plt.axes().xaxis.set_minor_locator(MultipleLocator(0.1))
plt.axes().yaxis.set_minor_locator(MultipleLocator(1))
plt.plot(q, i_oop, label="out of plane")
plt.plot(q, i_ip, label="in plane")
plt.legend()
ending = 'lin_1D.png'
filename1D = filename + ending
savefig(filename1D, bbox_inches='tight', dpi=300)

#log plots
font2 = {'family': 'Arial','color':  'black','weight': 'bold','size': 20}
fig = plt.figure()
plt.xlabel('q ($\AA^{-1}$)')
plt.ylabel('$log_{10}$ Intensity (a.u.)')
plt.yscale('log')
#plt.yticks(np.arange(1, 3, 5))
# ###adjust ylim
#plt.ylim((1.2, 3.5))
plt.xlim((0.1, 2.2))
#plt.xticks(np.arange(0.175, 2.175, 0.2))
plt.axes().xaxis.set_minor_locator(MultipleLocator(0.1))
log_i_oop = np.log10(i_oop)
log_i_ip = np.log10(i_ip)
plt.plot(q, log_i_oop, label="out of plane")
plt.plot(q, log_i_ip, label="in plane")
plt.legend()

ending = 'log_1D.png'
filename1D = filename + ending
savefig(filename1D, bbox_inches='tight', dpi=300)


#font1 = {'color':  'black','size': 25}
font1 = {'family': 'Arial','color':  'black','weight': 'bold','size': 30}
i, qxy, qz = pg.transform_reciprocal(data, correctSolidAngle=True, method="bbox")
i[i==0] = np.nan

#close('all')
fig = pylab.figure(figsize=(6,6)) ; gs = gridspec.GridSpec(1, 1); ax1 = plt.subplot(gs[0,0])
for ax in fig.get_axes():
    ax.tick_params(which='both', color='k', labelsize=20);
    ax.set_facecolor('k');
    ax1.yaxis.set_ticks_position('both');
    ax1.xaxis.set_ticks_position('both');
    # play with norm to get color scale right
    norm=mpl.colors.Normalize(vmin=0, vmax=200)
#norm = mpl.colors.SymLogNorm(linthresh=0.1, vmin=np.min(i), vmax=np.max(i))
ax1.imshow(i, norm=norm, cmap='turbo', extent=(np.min(qxy)/10, np.max(qxy)/10, np.min(qz)/10,
                                             np.max(qz)/10), origin='lower')
# ax1.imshow(np.log(i), extent=(np.min(qxy)/10, np.max(qxy)/10, np.min(qz)/10,
#                              np.max(qz)/10)
#           , vmax=7.0, vmin=3.0, cmap='jet', origin='lower')
pylab.ylim([-0.1,2.5])
pylab.xlim([-2,2])
ax1.xaxis.set_tick_params(width=1.5,length=5);
ax1.yaxis.set_tick_params(width=1.5,length=5);
ax1.set_xlabel('$q_{xy}$ ($\AA^{-1}$)', fontsize=16);
ax1.set_ylabel('$q_{z}$ ($\AA^{-1}$)', fontsize=16);
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
filename2D = filename + ending

savefig(filename2D,bbox_inches='tight', dpi = 600)

ending = '.csv'
filenamecsv = filename + ending

with open(filenamecsv.format(dataFile),"w+") as f:
    l = [q, i_ip,i_oop]
    a = zip(*l)
    writer = csv.writer(f)
    writer.writerow(["Q (1/A)","Intensity in plane (a.u.)", "Intensity out of plane (a.u.)"])
    for values in zip_longest(*l):
        writer.writerow(values)
