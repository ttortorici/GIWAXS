from pyFAI.detectors import Eiger1M
from pathlib import Path
import numpy as np
import fabio
from itertools import product
import matplotlib.pylab as plt
from matplotlib.colors import LogNorm
from old.dezinger import remove_zingers


class Detector(Eiger1M):

    DEAD_PIXELS = (np.array([681, 904, 398], dtype=np.int64),   # rows
                   np.array([646, 561, 579], dtype=np.int64))   # columns

    ISSUE_QUADS = ((255, 808),       # start rows
                   (255, 513, 771))  # start columns

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
    
    def __init__(self, stitch_rows: int, stitch_columns: int, exposure_time: int):
        self.stitch_rows = int(stitch_rows)
        self.stitch_columns = int(stitch_columns)
        self.exposure_time = int(int(exposure_time) / 2)
        self.detector = Detector()
        self.size = self._determine_size()

        
    def _determine_size(self) -> tuple:
        rows = self.detector.get_rows() + Stitcher.DEAD_BAND_PIXELS
        columns = self.stitch_columns * (self.detector.get_columns() - Stitcher.COLUMN_OVERLAP) + Stitcher.COLUMN_OVERLAP
        return (rows, columns)
    
    def load_data(self, directory: Path):
        data = np.zeros(self.size, dtype=np.uint32)
        weight = np.zeros(self.size, dtype=np.uint32)
        base_mask = np.ones((self.detector.ROWS, self.detector.COLS), dtype=np.uint32)
        base_mask[self.detector.DEAD_PIXELS] = 0
        for row_start_quad in self.detector.ISSUE_QUADS[0]:
            for col_start_quad in self.detector.ISSUE_QUADS[1]:
                base_mask[row_start_quad:(row_start_quad + 4), col_start_quad:(col_start_quad + 4)] = 0
        for scol, srow, sbandoff in product(range(self.stitch_columns), range(self.stitch_rows), range(2)):
            file = directory / f"{srow + 1}_{scol + 1}_{sbandoff + 1}"
            print(f"stitching {file.name}")
            file_data = fabio.open(file).data
            mask = base_mask.copy()
            mask[np.where(file_data == self.detector.MAX_INT)] = 0
            file_data *= mask
            file_data, zingers = remove_zingers(file_data, 1.2, .5)
            # print(zingers)
            start_row = (1 - sbandoff) * Stitcher.DEAD_BAND_PIXELS + (self.stitch_rows - 1 - srow) * (self.detector.ROWS - Stitcher.COLUMN_OVERLAP)
            start_column = scol * (self.detector.COLS - Stitcher.COLUMN_OVERLAP)
            data[start_row:(start_row + self.detector.ROWS), start_column:(start_column + self.detector.COLS)] += file_data
            weight[start_row:(start_row + self.detector.ROWS), start_column:(start_column + self.detector.COLS)] += mask
        weight *= self.exposure_time
        return data, weight
    

if __name__ == "__main__":
    stitcher = Stitcher(1, 3, 10)
    directory = Path("C:\\Users\\Teddy\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\TPP Films\\BTB-TPP\\2024 Film Growth\\Film 2\\XRD\\TT5-09\\Thin sio2")
    # directory = Path("D:\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\TPP Films\\BTB-TPP\\2024 Film Growth\\Film 1\\GIWAXS TT5-06")
    # data, weight = stitcher.load_data(directory)
    data = fabio.open(directory / "1_3_2").data
    plt.figure()
    plt.imshow(data+1, norm=LogNorm(1, np.max(data)))
    plt.figure()
    data, _ = remove_zingers(data, 1.2, .5)
    plt.imshow(data+1, norm=LogNorm(1, np.max(data)))
    plt.show()
    