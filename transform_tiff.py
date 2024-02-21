# numpy and plotting
import numpy as np
import pylab
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pylab as pl
from mpl_toolkits.axes_grid1 import make_axes_locatable
# pyFAI
import pyFAI
# pygix
import pygix
import fabio
import pandas as pd
from pathlib import Path
np.seterr(divide = 'ignore')

### Load the image data from the tiff. This notebook will need to be in the same folder as the tiff and .poni file
dataFile = 'Gold GIWAXS_image.tiff'
data = fabio.open(dataFile).data

close('all')

fig=figure(); gs = gridspec.GridSpec(1, 1); ax1 = plt.subplot(gs[0,0])
for ax in fig.get_axes():
    ax.tick_params(which='both', color='k'); #ax.set_facecolor(LBLU)
ax1.set_xlabel("x-pixel (#)"); ax1.set_ylabel("y-pixel (#)"); ax1.yaxis.set_ticks_position('both'); ax1.xaxis.set_ticks_position('both');# ax1.set_facecolor(LBLU)

ax1.imshow(np.log(data), vmin=1, vmax=8, origin='lower')
