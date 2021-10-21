import fabio
import numpy as np
from PIL import Image


filename = '/home/etortoric/Documents/GitHub/GIWAXS/raw_data/TT5mm-01-benzeneTPP_60min.tif'
data = fabio.open(filename).data
data_flip = np.flip(data)
Image.fromarray(data_flip).save(filename.strip('.tif') + '_flip.tif')
