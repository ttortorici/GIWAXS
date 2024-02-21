import numpy as np
import matplotlib.pylab as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import pygix
import fabio
import pandas as pd
from pathlib import Path
# np.seterr(divide = 'ignore')


def open_tiff(file_name: Path) -> np.ndarray:
    return fabio.open(file_name).data


def show_tiff(tiff: np.ndarray):
    plt.figure()
    plt.imshow(np.log10(tiff + 2))


def main(directory: Path, filename: str):
    pg = pygix.Transform()
    pg.load(directory / "cal.poni")
