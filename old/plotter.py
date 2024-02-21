import pyqtgraph as pg
import numpy as np
import window


unit_lookup = {'a': '<math>&#8491;</math>',
               'anstrom': '<math>&#8491;</math>',
               'a_inv': '<math>&#8491;<sup>-1</sup></math>',
               'inverse angstrom': '<math>&#8491;<sup>-1</sup></math>'}


def show_plot(x, y, title='', labels=('', ''), units=('', ''), fontsize=14):
    plot = pg.plot(x, y, title=title)
    for label, unit, axis in zip(labels, units, ('bottom', 'left')):
        if unit in unit_lookup.keys():
            plot.setLabel(axis, label, unit_lookup[unit], color='#FFFFFF', **{'font-size': f'{fontsize}pt'})
        else:
            plot.setLabel(axis, label, unit, color='#FFFFFF', **{'font-size': f'{fontsize}pt'})
    return plot

def show_plot2(x, y1, y2, title='', y_labels=('', ''), labels=('', ''), units=('', ''),
               colors=('g', 'y'), fontsize=14):
    plot = pg.plot()
    plot.setWindowTitle(title)
    plot.addLegend()

    c1 = plot.plot(x=x, y=y1, pen=colors[0], name=y_labels[0])
    c2 = plot.plot(x=x, y=y2, pen=colors[1], name=y_labels[1])
    for label, unit, axis in zip(labels, units, ('bottom', 'left')):
        if unit in unit_lookup.keys():
            plot.setLabel(axis, label, unit_lookup[unit], color='#FFFFFF', **{'font-size': f'{fontsize}pt'})
        else:
            plot.setLabel(axis, label, unit, color='#FFFFFF', **{'font-size': f'{fontsize}pt'})
    window.bring_to_top(plot)
    return plot


class Plot4(pg.QtGui.QMainWindow):
    def __init__(self, title='', fontsize=12, color='#FFFFFF'):
        self.fontsize = fontsize
        self.color = color

        self.app = pg.QtGui.QApplication([])
        self.win = pg.GraphicsLayoutWidget()
        self.win.resize(1900, 1000)
        self.win.setWindowTitle(title)

        # enable antiailiasing
        pg.setConfigOptions(antialias=True)

        self.p1 = self.win.addPlot(row=0, col=0)
        self.p2 = self.win.addPlot(row=0, col=1)
        self.p3 = self.win.addPlot(row=1, col=0)
        self.p4 = self.win.addPlot(row=1, col=1)

    def plot(self, which=1, x=np.array([]), y=np.array([]), title='', labels=('', ''), units=('', '')):
        if which == 1:
            p = self.p1
        elif which == 2:
            p = self.p2
        elif which == 3:
            p = self.p3
        elif which == 4:
            p = self.p4
        else:
            raise(ValueError, 'only 4 plots')

        p.setTitle(title, color=self.color, **{'font-size': f'{self.fontsize}pt'})
        p.plot(x=x, y=y)
        for label, unit, axis in zip(labels, units, ('bottom', 'left')):
            if unit in unit_lookup.keys():
                p.setLabel(axis, label, unit_lookup[unit], color=self.color, **{'font-size': f'{self.fontsize}pt'})
            else:
                p.setLabel(axis, label, unit, color=self.color, **{'font-size': f'{self.fontsize}pt'})

    def show(self):
        self.win.show()
        self.app.exec_()

    def closeEvent(self, *args, **kwargs):
        super(pg.QtGui.QMainWindow, self).closeEvent(*args, **kwargs)
        # print('klkjljlkj')