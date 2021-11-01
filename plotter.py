import pyqtgraph as pg
import pyqtgraph.exporters


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
