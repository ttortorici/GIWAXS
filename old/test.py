#from PyQt5 import QtGui
import sys

import pyqtgraph as pg
import numpy as np
import fabio

class ViewData(pg.QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ViewData, self).__init__(parent)
        self.widget = pg.QtGui.QWidget()
        self.widget.setLayout(pg.QtGui.QHBoxLayout())

        imv = pg.ImageView()
        data = fabio.open('/home/etortoric/Documents/GitHub/GIWAXS/raw_data/TT5mm-01-benzeneTPP_60min_flip.tif').data
        imagedata = np.rot90(np.rot90(data.T))
        imv.setImage(imagedata)

        self.widget.layout().addWidget(imv)
        self.widget.layout().addWidget(imv)
        self.widget.layout().addWidget(imv)
        self.widget.layout().addWidget(imv)
        self.setCentralWidget(self.widget)
        self.show()


def main():
    app = pg.QtGui.QApplication(sys.argv)
    vd = ViewData()
    vd.show()
    app.exec_()

if __name__ == '__main__':
    main()
