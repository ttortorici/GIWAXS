from pyFAI.detectors import Eiger1M
from pathlib import Path
import numpy as np
import fabio
import matplotlib.pylab as plt


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
        self.detector = Detector()
        self.size = self._determine_size()

    def _determine_size(self) -> tuple:
        rows = self.detector.get_rows() + Stitcher.DEAD_BAND_PIXELS
        columns = self.stitch_num * (self.detector.get_columns() - Stitcher.COLUMN_OVERLAP) + Stitcher.COLUMN_OVERLAP
        return (rows, columns)
    
    def load_data(self, directory: Path):
        data = np.empty(self.size)
        mask = np.empty(self.size)
        for scol in range(1, self.stitch_num + 1):
            for srol in range(1, 3):
                file = directory / f"1_{scol}_{srol}"
                file_data = fabio.open(file).data
                file_mask = self.detector.calc_mask()
                file_data *= np.logical_not(file_mask)
                # file_mask[np.where(file_data) < 0] = 1



                



if __name__ == "__main__":
    stitcher = Stitcher(3, 10)
    stitcher.load_data(Path("D:\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\TPP Films\\BTB-TPP\\2024 Film Growth\\Film 1\\GIWAXS TT5-06"))
