import numpy as np


def calc_d(lattice_constant, triangular_planar_distance, layer_spacing):
    """Lattice contsant should be a list or tuple of length 3 like (0,0,1) or (1,0,1)
        triangular planar distance in angstroms
        layer spacing in angstroms
        RETURNS d in angstroms"""
    h = float(lattice_constant[0])
    k = float(lattice_constant[1])
    l = float(lattice_constant[2])
    a = float(triangular_planar_distance)
    c = float(layer_spacing)
    return 1. / np.sqrt(4. / 3. * (h ** 2 + h * k + k ** 2) / a ** 2 + (l / c) ** 2)


def calc_q(lattice_constant, triangular_planer_distance, layer_spacing):
    """Lattice contsant should be a list or tuple of length 3 like (0,0,1) or (1,0,1)
        triangular planar distance in angstroms
        layer spacing in angstroms
        RETURNS 1 in inverse angstroms"""
    d = calc_d(lattice_constant, triangular_planer_distance, layer_spacing)
    return 2 * np.pi / d


class Fitter:
    def __init__(self):
        pass

    def rings_TPP(self):
        lattice_constants = [(0, 1, 0)]