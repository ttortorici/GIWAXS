import numpy as np
import matplotlib.pylab as plt
from matplotlib.colors import LogNorm
from pathlib import Path
import fabio
from pyFAI.geometry import Geometry
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'


def open_tiff(file_name: Path) -> np.ndarray:
    return fabio.open(file_name).data


def show_tiff(tiff: np.ndarray, title=None):
    plt.figure()
    plt.imshow(np.log10(tiff + 1))
    if title is not None:
        plt.title(title)

def save_data(directory: Path, filename: str, numpy_array: np.ndarray):
    if filename[-4:] != ".csv":
        filename.replace('.', '_')
        filename += ".csv"
    numpy_array.tofile(directory / filename, sep=',')


class TransformGIWAXS:

    def __init__(self, incident_angle_degrees, tilt_angle_degrees=0.):
        self.calibration_poni = Geometry()
        self.incident_angle = np.deg2rad(incident_angle_degrees)
        self.tilt_angle = np.deg2rad(tilt_angle_degrees)
        self.alpha_scattered = np.empty(0, dtype=np.float64)  # will be array size of data
        self.phi_scattered = np.empty(0, dtype=np.float64)  # will be array size of data
        self.q_vec = np.empty(0, dtype=np.float64)  # will be 3 x size of data
        self.q_xy = np.empty(0, dtype=np.float64)   # will be array size of data
        self.shape = (0, 0)  # will be shape of date
        self.beam_y_px = 0.0  # will be poni-y in pixels
        self.beam_x_px = 0.0  # will be poni-x in pixels
        self.det_dist_px = 0.0  # will be sample-detector distance in units of pixels

    def load(self, poni_file_name: Path):
        self.calibration_poni.load(poni_file_name)
        self.shape = self.calibration_poni.get_shape()
        self.beam_x_px = self.calibration_poni.get_poni2() / self.calibration_poni.get_pixel2()
        self.beam_y_px = float(self.shape[0]) - self.calibration_poni.get_poni1() / self.calibration_poni.get_pixel1()
        self.det_dist_px = self.calibration_poni.get_dist() / self.calibration_poni.get_pixel1()
        self.calculate_scattering_angles()
        self.calculate_q_vector()
    
    def calculate_scattering_angles(self):
        x = np.arange(self.shape[1]).reshape(1, self.shape[1])
        y = np.arange(self.shape[0]).reshape(self.shape[0], 1)
        #d = self.det_dist_px
        y_lab = self.beam_x_px - x
        z_lab = self.beam_y_px - y
        if self.tilt_angle:
            tilt_cos = np.cos(self.tilt_angle)
            tilt_sin = np.sin(self.tilt_angle)
            y_rot = y_lab * tilt_cos - z_lab * tilt_sin
            z_rot = z_lab * tilt_cos + y_lab * tilt_sin
            sum_dsq_ysq = self.det_dist_px * self.det_dist_px + y_rot * y_rot
            self.alpha_scattered = np.arcsin(z_rot / np.sqrt(sum_dsq_ysq + z_rot * z_rot)) - self.incident_angle
            self.phi_scattered = np.arcsin(y_rot / np.sqrt(sum_dsq_ysq))
        else:
            sum_dsq_ysq = self.det_dist_px * self.det_dist_px + y_lab * y_lab
            self.alpha_scattered = np.arcsin(z_lab / np.sqrt(sum_dsq_ysq + z_lab * z_lab)) - self.incident_angle
            self.phi_scattered = np.arcsin(y_lab / np.sqrt(sum_dsq_ysq))
            self.phi_scattered = np.repeat(self.phi_scattered, self.shape[0], axis=0)
            print(self.phi_scattered.shape)


    def calculate_q_vector(self):
        cos_alpha = np.cos(self.alpha_scattered)
        self.q_vec = np.array([
            cos_alpha * np.cos(self.phi_scattered) - np.cos(self.incident_angle),
            cos_alpha * np.sin(self.phi_scattered),
            np.sin(self.alpha_scattered) + np.sin(self.incident_angle)
        ])
        self.q_vec *= 2 * np.pi / (self.calibration_poni.get_wavelength() * 1e10)
        self.q_xy = np.sqrt(self.q_vec[0] * self.q_vec[0] + self.q_vec[1] * self.q_vec[1]) * ((self.q_vec[1] > 0) * 2 - 1)
        
        # print(self.beam_y_px, self.beam_x_px)
        # print(self.shape)
        # print(self.q_vec[0, 256, 1491])
        # print(self.q_vec[0, 931, 1491])
        # directions = ["x", "y", "z"]
        # ranges = ((-1, 0, 8), (-2, 2, 8), (.1, 2.5, 8))
        # for ii in range(len(directions)):
        #     fig = plt.figure(facecolor="w")
        #     ax1 = plt.subplot()
        # 
        #     pos = ax1.imshow(self.q_vec[ii])
        #     ax1.contour(self.q_vec[ii], np.linspace(*ranges[ii]), colors='white')
        #     # ax1.plot(beam_center_x, beam_center_y, 'ro', markersize=1)
        #     # ax1.plot(beam_center_x,  two_alpha_point, 'ro', markersize=1)
        #     ax1.set_title("$q_{{{}}}$ amount at each pixel".format(directions[ii]))
        #     ax1.set_xlabel("column (pixels)")
        #     ax1.set_ylabel("row (pixels)")
        #     fig.colorbar(pos, ax=ax1, shrink=0.7)

    def transform_image(self, data, exposure_time, weights=None, scale=1):
        image_shape = (int(self.shape[0] * scale), int(self.shape[1] * scale))
        # q_xy = np.sqrt(self.q_vec[0] * self.q_vec[0] + self.q_vec[1] * self.q_vec[1]) * ((self.q_vec[1] > 0) * 2 - 1)
        # q_z = self.q_vec[2]

        # beam center from top left corner of detector in q
        extent = (-np.max(self.q_xy), -np.min(self.q_xy), np.min(self.q_vec[2]), np.max(self.q_vec[2]))
        beam_center_qxy_tranfromed = np.max(self.q_xy)
        beam_center_qz_transformed = np.max(self.q_vec[2])
        # move into detector from (top left corner is origin)
        qxy_det_origin = beam_center_qxy_tranfromed - self.q_xy
        qz_det_origin = beam_center_qz_transformed - self.q_vec[2]
        # rescale so largest q reaches edge of detector in pixels
        qxy_det_origin *= (image_shape[1] - 2) / np.max(qxy_det_origin)
        qz_det_origin *= (image_shape[0] - 2) / np.max(qz_det_origin)

        # floor the locations to get pixel locations
        qxy_det_origin_floor = np.floor(qxy_det_origin)
        qz_det_origin_floor = np.floor(qz_det_origin)
        x_det_px_loc = qxy_det_origin_floor.astype(int)
        y_det_px_loc = qz_det_origin_floor.astype(int)
        x_remainder = qxy_det_origin - qxy_det_origin_floor
        y_remainder = qz_det_origin - qz_det_origin_floor
        x_remainder_compliment = 1 - x_remainder
        y_remainder_compliment = 1 - y_remainder
        current_pixel_weight = x_remainder_compliment * y_remainder_compliment
        x_neighbor_weight = x_remainder * y_remainder_compliment
        y_neighbor_weight = x_remainder_compliment * y_remainder
        diag_neighbor_weight = x_remainder * y_remainder
        
        data = data.astype(np.float64)
        transformed_data = np.zeros(image_shape, np.float64)
        transformed_weights = np.zeros(image_shape, np.float64)
        if weights is None:
            weights = np.ones(data.shape, dtype=np.float64) * exposure_time
        else:
            weights = weights.astype(np.float64)
        for rr in range(self.shape[0]):
            for cc in range(self.shape[1]):
                row = y_det_px_loc[rr, cc]
                col = x_det_px_loc[rr, cc]
                transformed_data[row, col] += data[rr, cc] * current_pixel_weight[rr, cc]
                transformed_weights[row, col] += weights[rr, cc] * current_pixel_weight[rr, cc]

                transformed_data[row, col + 1] += data[rr, cc] * x_neighbor_weight[rr, cc]
                transformed_weights[row, col + 1] += weights[rr, cc] * x_neighbor_weight[rr, cc]
                
                transformed_data[row + 1, col] += data[rr, cc] * y_neighbor_weight[rr, cc]
                transformed_weights[row + 1, col] += weights[rr, cc] * y_neighbor_weight[rr, cc]
                
                transformed_data[row + 1, col + 1] += data[rr, cc] * diag_neighbor_weight[rr, cc]
                transformed_weights[row + 1, col + 1] += weights[rr, cc] * diag_neighbor_weight[rr, cc]
        intesity_adjuster = exposure_time / transformed_weights
        intesity_adjuster[np.where(intesity_adjuster == np.infty)] = 0
        transformed_data *= intesity_adjuster
    
        fig = plt.figure(figsize=(10, 5), facecolor="w")
        ax1 = plt.subplot()
        for ax in fig.get_axes():
            ax.tick_params(which='both', color='k', direction = 'in')
            ax.set_facecolor("b")
        ax1.set_xlabel(r"q$_\mathregular{xy}\ (\mathregular{\AA}^{-1})$")
        ax1.set_ylabel(r"q$_\mathregular{z}\ (\mathregular{\AA}^{-1})$")
        ax1.yaxis.set_ticks_position('both')
        ax1.xaxis.set_ticks_position('both')
        # pos = ax1.imshow(np.log10(transformed_data+10), extent=extent)
        pos = ax1.imshow(transformed_data+1, extent=extent, norm=LogNorm(1, np.max(transformed_data)))
        fig.colorbar(pos, ax=ax1, shrink=0.7)
        # divider = make_axes_locatable(ax1)
        # cax = divider.append_axes("right", size="5%", pad=0.05)
        plt.show()
        return transformed_data, transformed_weights
    
    def transform_cake(self, data, exposure_time, weights=None, bins_azi=1000, bins_q=1000):
        cake_shape = (bins_q, bins_azi)
        data_cake = np.zeros(cake_shape, dtype=np.float64)
        weights_cake = np.zeros(cake_shape, dtype=np.float64)
        
        data = data.astype(np.float64)
        if weights is None:
            weights = np.ones(data.shape, dtype=np.float64)
        else:
            weights = weights.astype(np.float64)

        q_magnitude = np.sqrt(np.sum(self.q_vec * self.q_vec, axis=0))
        azimuthal = np.arctan2(self.q_xy, self.q_vec[2])
        degree_cutoff = np.deg2rad(100)
        invalid = np.where(np.logical_or(azimuthal < -degree_cutoff, azimuthal > degree_cutoff))
        q_magnitude[invalid] = 0
        azimuthal[invalid] = 0
        weights[invalid] = 0

        b_azi_c = np.max(azimuthal)
        b_q_c = np.max(q_magnitude)
        extent = (np.min(azimuthal), np.max(azimuthal), np.min(q_magnitude), np.max(q_magnitude))

        azi_det_origin = b_azi_c - azimuthal
        q_det_origin = b_q_c - q_magnitude
        
        azi_det_origin *= (cake_shape[1] - 2) / np.max(azi_det_origin)
        q_det_origin *= (cake_shape[0] - 2) / np.max(q_det_origin)

        azi_det_origin_floor = np.floor(azi_det_origin)
        q_det_origin_floor = np.floor(q_det_origin)
        x_px_loc = azi_det_origin_floor.astype(int)
        y_px_loc = q_det_origin_floor.astype(int)

        x_remainder = azi_det_origin - azi_det_origin_floor
        y_remainder = q_det_origin - q_det_origin_floor
        x_remainder_compliment = 1 - x_remainder
        y_remainder_compliment = 1 - y_remainder
        current_pixel_weight = x_remainder_compliment * y_remainder_compliment
        x_neighbor_weight = x_remainder * y_remainder_compliment
        y_neighbor_weight = x_remainder_compliment * y_remainder
        diag_neighbor_weight = x_remainder * y_remainder

        for rr in range(data.shape[0]):
            for cc in range(data.shape[1]):
                row = y_px_loc[rr, cc]
                col = x_px_loc[rr, cc]
                data_cake[row, col] += data[rr, cc] * current_pixel_weight[rr, cc]
                weights_cake[row, col] += weights[rr, cc] * current_pixel_weight[rr, cc]
                data_cake[row, col + 1] += data[rr, cc] * x_neighbor_weight[rr, cc]
                weights_cake[row, col + 1] += weights[rr, cc] * x_neighbor_weight[rr, cc]

                data_cake[row + 1, col] += data[rr, cc] * y_neighbor_weight[rr, cc]
                weights_cake[row + 1, col] += weights[rr, cc] * y_neighbor_weight[rr, cc]

                data_cake[row + 1, col + 1] += data[rr, cc] * diag_neighbor_weight[rr, cc]
                weights_cake[row + 1, col + 1] += weights[rr, cc] * diag_neighbor_weight[rr, cc]
        intesity_adjuster = 10. / weights_cake
        intesity_adjuster[np.where(intesity_adjuster == np.infty)] = 0
        data_cake_adj = intesity_adjuster * data_cake

        fig = plt.figure(facecolor="w")
        ax1 = plt.subplot()
        pos = ax1.imshow(data_cake_adj+1, extent=extent, norm=LogNorm(1, np.max(data_cake)))
        ax1.set_title("Caked image with exposure time adjustment")
        ax1.set_xlabel(r"$\Omega$")
        ax1.set_ylabel(r"$q\ (\mathregular{\AA}^{-1})$")
        fig.colorbar(pos, ax=ax1, shrink=0.7)

        return data_cake, weights_cake
        
    

if __name__ == "__main__":
    from tiff_loader import load_from
    # directory = Path("C:\\Users\\Teddy\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\TPP Films\\BTB-TPP\\2024 Film Growth\\Film 1\\GIWAXS TT5-06")
    # transformer = TransformGIWAXS(0.23, .15)
    
    # directory = Path("C:\\Users\\Teddy\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\TPP Films\\BTB-TPP\\2024 Film Growth\\Film 2\\XRD\\TT5-09\\Thick sio2\\rotation 1")
    # directory = Path("C:\\Users\\Teddy\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\TPP Films\\BTB-TPP\\2024 Film Growth\\Film 2\\XRD\\calibration")
    directory = Path("C:\\Users\\Teddy\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\TPP Films\\BTB-TPP\\2024 Film Growth\\Film 2\\XRD\\TT5-09\\Thick sio2\\rotation 2\\non-grazing")
    transformer = TransformGIWAXS(8.81)

    transformer.load(directory / "cal.poni")

    # show_tiff(transformer.q_unit[0])
    # show_tiff(transformer.q_unit[1])
    # plt.plot(transformer.q_unit[1, :, int(transformer.shape[1] / 2)])
    # plt.plot(transformer.q_unit[1, int(transformer.shape[0] / 2), :])
    
    # data = open_tiff(directory / "GIWAXS-30min-BTBaTPP-teddy-20240130.tif")
    
    data, weight = load_from(directory)

    data_t, weights_t = transformer.transform_image(data, np.max(data), weight, .9)
    # transformer.transform_cake(data, 10, weight)
    plt.show()
    
    