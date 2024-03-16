from pyFAI.detectors import Eiger1M
from pathlib import Path
import numpy as np
import fabio
from itertools import product
import matplotlib.pylab as plt


class Detector(Eiger1M):

    DEAD_PIXELS = (np.array([681, 904, 398], dtype=np.int64),
                   np.array([646, 561, 579], dtype=np.int64))

    ROWS = 1065
    COLS = 1030

    MAX_INT = (1 << 32) - 1

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
    
    def __init__(self, stitch_rows, stitch_columns, exposure_time):
        self.stitch_rows = stitch_rows
        self.stitch_columns = stitch_columns
        self.exposure_time = exposure_time
        self.detector = Detector()
        self.size = self._determine_size()
        
    def _determine_size(self) -> tuple:
        rows = self.detector.get_rows() + Stitcher.DEAD_BAND_PIXELS
        columns = self.stitch_columns * (self.detector.get_columns() - Stitcher.COLUMN_OVERLAP) + Stitcher.COLUMN_OVERLAP
        return (rows, columns)
    
    def load_data(self, directory: Path):
        data = np.zeros(self.size, dtype=np.uint32)
        weight = np.zeros(self.size, dtype=np.uint8)
        for scol, srow, srow2 in product(range(self.stitch_columns), range(self.stitch_rows), range(2)):
            file = directory / f"{srow + 1}_{scol + 1}_{srow2 + 1}"
            file_data = fabio.open(file).data
            mask = np.ones(file_data.shape, dtype=np.int64)
            mask[np.where(file_data == self.detector.MAX_INT)] = 0
            mask[self.detector.DEAD_PIXELS] = 0
            file_data *= mask
            start_row = (1 - srow2) * Stitcher.DEAD_BAND_PIXELS + (self.stitch_rows - 1 - srow) * (self.size[0] - Stitcher.COLUMN_OVERLAP)
            start_column = scol * (self.size[1] - Stitcher.COLUMN_OVERLAP)
            data[start_row, start_column] += file_data
            weight[start_row, start_column] += mask
        plt.imshow(data)
        plt.show()


                



if __name__ == "__main__":
    stitcher = Stitcher(1, 3, 10)
    # stitcher.load_data(Path("D:\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\TPP Films\\BTB-TPP\\2024 Film Growth\\Film 1\\GIWAXS TT5-06"))
    stitcher.load_data(Path("C:\\Users\\Teddy\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\TPP Films\\BTB-TPP\\2024 Film Growth\\Film 1\\GIWAXS TT5-06"))
