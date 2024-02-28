from pyFAI.detectors import Eiger1M


class Detector(Eiger1M):

    DEAD_PIXELS = (
        (681, 646),
        (904, 561),
        (398, 579)
    )

    ROWS = 1065
    COLS = 1030

    def __init__(self):
        super().__init__()
    
    def calc_mask(self) -> np.ndarray:
        mask = super().calc_mask()
        for row, col in Detector.DEAD_PIXELS:
            mask[row, col] = 1
        return mask
    
    def get_size(self) -> tuple:
        return (Detector.ROWS, Detector.COLS)
    
    def get_rows(self) -> int:
        return Detector.ROWS
    
    def get_columns(self) -> int:
        return Detector.COLS
        

class Stitcher:
    
    def __init__(self, rows, columns, exposure_time):
        self.rows = rows
        self.columns = columns
        self.exposure_time = exposure_time
        self.detector = Eiger1M()
        self.size = 



if __name__ == "__main__":
    import matplotlib.pylab as plt
    import numpy as np

    detector = Detector()
    print(detector.get_size())
    # print(detector)
    # print(detector.mask)
    # print(np.logical_not(detector.mask))
    # print(np.sum(detector.mask))
    # print(37 * 1030)
    # plt.imshow(detector.calc_mask())
    # plt.show()