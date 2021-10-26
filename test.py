import numpy as np
import fabio
import os


def dezingering(data, thresh=2, attempts=1):
    print('\n---------------DEZINGERING DATA----------------')
    check = 0
    len_y, len_x = np.shape(data)
    look = 1
    buff = 2
    max = data.max()

    for attempt in range(attempts):
        '''down = data[:-look, :] > thresh * (data[look:, :] + buff)
        up = data[look:, :] > thresh * (data[:-look, :] + buff)
        right = data[:, :-look] > thresh * (data[:, look:] + buff)
        left = data[:, look:] > thresh * (data[:, :-look] + buff)

        print(np.shape(data)[0]*np.shape(data)[1])
        print(np.sum(down))
        print(np.sum(up))
        print(np.sum(right))
        print(np.sum(left))'''

        down = data > thresh * (np.vstack([data[look:, :], np.zeros(len_x)]) + buff)
        print(f'looking down: {down}')
        data[down] =
        up = data > thresh * (np.vstack([np.zeros(len_x), data[:-look, :]]) + buff)
        right = data > thresh * (np.append(data[:, look:], np.zeros((len_y, 1)), axis=1) + buff)
        left = data > thresh * (np.append(np.zeros((len_y, 1)), data[:, :-look], axis=1) + buff)

        print(np.shape(data)[0]*np.shape(data)[1])
        print(np.sum(down))
        print(np.sum(up))
        print(np.sum(right))
        print(np.sum(left))

        '''for i2 in range(look, len_x - look):
            for j2 in range(look, len_y - look):
                """Collects the values of the nearest neighbors"""
                neighbors = data[i2 - look: i2 + look + 1, j2 - look: j2 + look + 1] * shaper

                """Bool list takes the surrounding points to check if they're much bigger than their surroundings.
                Will be a list of False if everything is fine"""
                bool_list = data[i2, j2] * shaper > threshold_multiplier * neighbors
                #print(data[i2 - look: i2 + look + 1, j2 - look: j2 + look + 1])
                #print(bool_list)

                """np.sum(bool_list) will be 0 if all data points are fine"""
                if np.sum(bool_list):
                    data[i2, j2] = (data[i2 - 1, j2] + data[i2 + 1, j2] + data[i2, j2 - 1] + data[i2, j2 + 1]) / 4.
                    check += 1'''
        print(f'Dezingering applied {attempt  + 1} times and smoothed {check} times total.')
    return data


data = fabio.open(os.getcwd() + os.sep + 'raw_data' + os.sep + 'TT5mm-01-benzeneTPP_60min_flip.tif').data
print('data loaded')
dezingering(data)