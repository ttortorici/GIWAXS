import pyqtgraph as pg
import numpy as np
import fabio


def view_tif(filename):
    pg.image(np.rot90(fabio.open(filename).data, -1))

