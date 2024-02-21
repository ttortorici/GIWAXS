import io as io
import xml.etree.ElementTree as ET
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import zipfile
from PIL import Image
import pathlib

def extract_rasx(filename: pathlib.Path):
    im, header, om = open_rasx(f)
    print(header)
    print(f"Incidence angle is {om} degrees")
    plt.imshow(im, origin = "lower")
    plt.savefig(f.with_suffix(".jpg"), dpi=360)
    save_tif(f.with_suffix(".tiff"), im)
    write_poni(filename, header)


def open_rasx(filename):
    with zipfile.ZipFile(filename) as myzip:
        with myzip.open("Data0/MesurementConditions0.xml") as myfile:
            tree = ET.parse(myfile)
            root = tree.getroot()
            for child in root[6]:
                if child[0].text == "*MEAS_COND_COUNTER_CENTER_X": #### Center pixel in x (pixel coordinates)
                    xcen = float(child[1].text)
                elif child[0].text == "*MEAS_COND_COUNTER_CENTER_Y": ##### Center pixel in y (pixel coordinates)
                    ycen = float(child[1].text)
                elif child[0].text == "*MEAS_COND_COUNTER_DISTANCE": #### S-D distance in m
                    clength = float(child[1].text) / 1000
            for child in root[5][0]:
                if child[0].text == "SIZE1": ##### Detector dimension in x (pixels)
                    xlen = float(child[1].text)
                elif child[0].text == "SIZE2":
                    ylen = float(child[1].text) ###### Detector dimension in y (pixels)
            twotheta = root[2][2].attrib ######### Getting the two theta value of the detector
            tthval = float(twotheta["Position"])
            omega = float(root[2][0].attrib['Position'])  #### Incidence angle
        with myzip.open('Data0/Image0.bin') as myfile:
            im = np.frombuffer(myfile.read(),  dtype='uint32', ).reshape(int(ylen), int(xlen))
        header = [ylen, xlen, ycen, xcen, clength, tthval] #### pyFAI poni uses Y-axis, X-axis order
        header = {
            "length_x": xlen,
            "length_y": ylen,
            "center_x": xcen,
            "center_y": ycen,
            "s-d_dist": clength,
            "two_theta": tthval,
        }
    return im, header, omega

def save_tif(filename, image_array):
    im = Image.fromarray(image_array)
    im.save(filename)
    
def write_poni(filename: pathlib.Path, header: list):
    filename = str(filename).split(".")[0] + ".poni"
    poni1 = header["center_y"] * 100e-6 #### Convert center pixel to m
    poni2 = header["center_x"] * 100e-6 
    rot = -np.sin(header["two_theta"] * np.pi / 180)
    lines = ['# Nota: C-Order, 1 refers to the Y axis, 2 to the X axis',
             'poni_version: 2',
             'Detector: Detector',
             f'Detector_config: {{"pixel1": 9.999999999999998e-05, "pixel2": 9.999999999999998e-05, "max_shape": [{int(header["length_y"])},{int(header["length_x"])}]}}',
             f'Distance: {header["s-d_dist"]}',
             f'Poni1: {poni1}',
             f'Poni2: {poni2}',
             'Rot1: 1e-09',
             f'Rot2: {rot}',
             'Rot3: 1e-09',
             'Wavelength: 1.5409420635495932e-10']
    with open(filename, 'w') as f:
        for line in lines:
            f.write(line)
            f.write('\n')

if __name__ == '__main__':
    import sys
    from tkinter import filedialog

    print('\nCurrently works for .rasx files obtained from 2D-GIWAXS Part Activity in SmartLab Studio-II\n') 

    if len(sys.argv) == 1:
        dir = pathlib.Path('C:\\Users\\Teddy\\OneDrive - UCB-O365\\Rogerslab3\\Teddy\\XRD\\AgBe\\COSINC')
        for f in dir.glob("*image.rasx"):
            print(f)
            extract_rasx(f)

    elif sys.argv[1].lower() == "--gui":
        list_of_files = filedialog.askopenfilenames()
        for f in list_of_files:
            print(f)
        sys.exit()

    elif sys.argv[1].lower() == "--help":
        print("`python extract_rasx.py` will extract data from every rasx in the directory defined in the script\n" \
              "`python extract_rasx.py --gui` will open a GUI dialog to select .rasx you would like to process\n" \
              "`python extract_rasx.py [dir path]` will extract all data from [dir path]\n" \
              "`python extract_rasx.py [file path]` will extract all data from the file")
        sys.exit()
    elif sys.argv[1][:-5] == ".rasx":
        extract_rasx(pathlib.Path(sys.argv[1]))
    else:
        dir = pathlib.Path(sys.argv[1])
        for f in dir.glob("*image.rasx"):
            print(f)
            extract_rasx(f)
        
    plt.show()