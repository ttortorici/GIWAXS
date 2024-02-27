from pyFAI.detectors import Eiger1M


class Detector(Eiger1M):
    def __init__(self):
        super().__init__()
        mask = self.calc_mask()
        dead_pixels = (
            (681, 646),
            (904, 561),
            (398, 579)
        )
        for row, col in dead_pixels:
            mask[row, col] = 1
        np.logical_not(self.mask)



if __name__ == "__main__":
    import matplotlib.pylab as plt
    import numpy as np

    detector = Detector()
    print(detector)
    print(detector.mask)
    print(np.logical_not(detector.mask))
    print(np.sum(detector.mask))
    print(37 * 1030)
    plt.imshow(detector.calc_mask())
    plt.show()