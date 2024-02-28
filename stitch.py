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

    COLUMN_OVERLAP = 10
    DEAD_BAND_PIXELS = 37
    
    def __init__(self, stitch_num, exposure_time):
        self.stitch_num = stitch_num
        self.exposure_time = exposure_time
        self.detector = Eiger1M()
        self.size = self._determine_size()

    def _determine_size(self, size) -> tuple:
        rows = self.detector.get_rows() + Stitcher.DEAD_BAND_PIXELS
        columns = self.stitch_num * (self.detector.get_columns() - Stitcher.COLUMN_OVERLAP) + Stitcher.COLUMN_OVERLAP
        return (rows, columns)
    
    def load_data(self):
        



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