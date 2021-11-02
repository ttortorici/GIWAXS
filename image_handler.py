import os
import pyqtgraph as pg
import numpy as np
import fabio
from PIL import Image


def view(filename):
    pg.image(np.rot90(np.rot90(fabio.open(filename).data.T)))


def size(filename):
    img = fabio.open(filename).data
    return img.shape


def flip(filename, save_path):
    """Finds a tif at filename and rotates the image 180 degrees and then saves it in the save_path"""
    data_to_flip = fabio.open(filename).data
    data_flipped = np.flip(data_to_flip)
    # extract just the name of the file to save
    slash_loc = filename.replace('/', os.sep).rfind(os.sep)
    save_fname = filename[slash_loc + 1:filename.find('.')]
    save_fname = f'{save_path}{os.sep}{save_fname}_flip.tif'
    Image.fromarray(data_flipped).save(save_fname)
    return save_fname