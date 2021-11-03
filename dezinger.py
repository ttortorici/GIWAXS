import os
import numpy as np
from PIL import Image, ImageDraw
from scipy import fftpack, ndimage
import fabio
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
import window


def low_pass_filter(img):
    """Blur an image using an FFT"""
    fft1 = fftpack.fftshift(fftpack.fft2(img))

    y, x = img.shape

    r = y / 1.5  # Size of circle
    bbox = ((x - r) / 2, (y - r) / 2, (x + r) / 2, (y + r) / 2)  # Create a box

    low_pass = Image.new("L", (x, y), color=0)

    draw1 = ImageDraw.Draw(low_pass)
    draw1.ellipse(bbox, fill=1)

    low_pass_array = np.array(low_pass)
    filtered = np.multiply(fft1, low_pass_array)

    ifft2 = np.real(fftpack.ifft2(fftpack.ifftshift(filtered)))
    ifft2 = np.maximum(0, np.minimum(ifft2, 255))
    return ifft2.astype('int32')


def gaussian_filter(data, sigma):
    """Blur an image using a gaussian filter"""
    return ndimage.gaussian_filter(data, sigma).astype('int32')


def find_zingers(image, cut_off, gaus_std):
    """Creates a 'truth' table of zingers at each pixel location"""
    # smoothed_img = low_pass_filter(image)
    smoothed_img = gaussian_filter(image, gaus_std)
    print(f'average value of data is {np.average(image)}, but {np.average(smoothed_img)} after smoothing.')
    dif_img = np.subtract(smoothed_img, image)

    print(f'{image.shape[0] * image.shape[1]} pixels in data')

    zinger_chart = dif_img / (smoothed_img + 1)
    anomalies1 = zinger_chart < -cut_off
    # anomalies2 = zinger_chart > cut_off * 2
    anomalies = anomalies1  # | anomalies2
    print(f'Found {np.sum(anomalies)} zingers')
    return anomalies.astype('int32')


def remove_zingers(image, cut_off, gaus_std):
    """Finds zingers and then replaces them with the average value of 2 pixels away in each direction"""
    zingers = find_zingers(image, cut_off, gaus_std)
    zinger_locs = np.where(zingers)
    max_r, max_c = image.shape
    for row, col in zip(zinger_locs[0], zinger_locs[1]):
        up = row - 2
        down = (row + 2) % max_r
        left = col - 2
        right = (col + 2) % max_c
        image[row, col] = np.average((image[up, col], image[down, col],
                                      image[row, left], image[row, right]))
    return image, zingers


def remove_zingers_from_file(filename, cut_off=1.2, gaus_std=3, dezings=1, show=False):
    # window = Plot() if show else None
    image = fabio.open(filename).data
    zingers = np.zeros(image.shape)
    if show:
        # window.add_image(image)
        w1 = pg.image(np.rot90(np.rot90(image.T)), title='Original')
    for ii in range(dezings):
        print(f'\nDezingering attempt {ii + 1}')
        image, zingers_temp = remove_zingers(image, cut_off, gaus_std)
        zingers += zingers_temp
    if show:
        w2 = pg.image(np.rot90(np.rot90(zingers.T)), title='Zinger Locations')
        w3 = pg.image(np.rot90(np.rot90(image.T)), title='Dezingered')
        winh = 303
        barh = 32
        w1.setGeometry(0, barh, 1000, winh)
        w2.setGeometry(0, barh*2+winh, 1000, winh)
        w3.setGeometry(0, barh*3+winh*2, 1000, winh)
        window.bring_to_top(w1)
        window.bring_to_top(w2)
        window.bring_to_top(w3)
    save_fname = f'{filename[:filename.find(".")]}_dz{dezings}.tif'
    Image.fromarray(image).save(save_fname)
    return save_fname


class Plot:
    def __init__(self):
        self.app = pg.QtGui.QApplication(sys.argv)
        self.win = QtGui.QMainWindow()
        self.win.resize(1900, 1000)
        self.win.setWindowTitle('Zinger Removal')

        # enable antiailiasing
        pg.setConfigOptions(antialias=True)

        # container widget with layout to add QWidgets
        self.cw = QtGui.QWidget()
        self.win.setCentralWidget(self.cw)
        self.layout = QtGui.QVBoxLayout()
        self.cw.setLayout(self.layout)

    def add_image(self, img_data):
        img_data = np.rot90(np.rot90(img_data.T))
        img = pg.ImageView()
        img.setImage(img_data)
        self.layout.addWidget(img)

    def show(self):
        self.win.show()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    filename = '/home/etortoric/Documents/GitHub/GIWAXS/raw_data/TT5mm-01-benzeneTPP_60min_flip.tif'
    remove_zingers_from_file(filename, dezings=3, show=True)
