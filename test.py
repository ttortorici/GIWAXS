import tkinter as tk
import os


sample_orientation_g = -1
incident_angle_g = -1.
cal_path_g = ''
data_path_g = ''


def get_file(ftype='tif', dir=os.getcwd()):
    """Opens dialog box to get location of desired file"""
    if not ftype.lower() in ['tif', 'poni']:
        raise ValueError('invalid filetype to retrieve')
    filename = tk.filedialog.askopenfilename(initialdir=dir, title=f'Select {ftype.upper()}',
                                             filetypes=((f'{ftype.upper()}', f'*.{ftype.lower()}',), ('all', '*.*')))
    return filename


def start():
    global sample_orientation_g, incident_angle_g
    Setup_Window().mainloop()
    sample_orientation = sample_orientation_g
    incident_angle = incident_angle_g
    del(sample_orientation_g)
    del(incident_angle_g)
    return sample_orientation, incident_angle


class Setup_Window(tk.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'
    default_angle = '0.12'      # degrees
    default_calibration_path = os.getcwd() + os.sep + 'calibrations'
    default_calibration_fname = 'cal.poni'
    default_data_path = os.getcwd() + os.sep + 'raw_data'
    default_data_fname = 'TT5mm-01-benzeneTPP_60min.tif'

    def __init__(self):
        """Set up Window"""

        tk.Tk.__init__(self)
        self.title('Calibrate PONI File')

        """Create and place labels"""
        columns = 3

        r = 0

        """Title Line"""
        tk.Label(self, text='Set up analysis',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        columnspan=columns,
                                                                        sticky=tk.W)

        r += 1

        """Sample orientation"""
        tk.Label(self, text='Sample Orientation',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)

        self.orientation_selection = tk.IntVar(self)

        self.orientation_selection.set(1)

        tk.Radiobutton(self, text='Horizontal', variable=self.orientation_selection, value=1,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1)
        tk.Radiobutton(self, text='Vertical', variable=self.orientation_selection, value=2,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=2)

        r += 1

        """Incident Angle"""
        tk.Label(self, text='Incident Angle [\u00B0]',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)
        self.angle_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.angle_entry.grid(row=r, column=1, columnspan=2, sticky=tk.E + tk.W)
        self.angle_entry.insert(0, Setup_Window.default_angle)

        r += 1

        """Calibration location"""

        tk.Label(self, text='Calibration',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)
        self.calibration_path_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.calibration_path_entry.grid(row=r, column=1, columnspan=2, sticky=tk.E + tk.W)

        self.calibration_path = Setup_Window.default_calibration_path + os.sep + Setup_Window.default_calibration_fname
        self.calibration_path_entry.insert(0, self.calibration_path)

        tk.Button(self, text='...', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.open_cal).grid(row=r, column=3, sticky=tk.E + tk.W)

        r += 1

        """Data location"""

        tk.Label(self, text='Data',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=0, sticky=tk.W)
        self.data_path_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.data_path_entry.grid(row=r, column=1, columnspan=2, sticky=tk.E + tk.W)

        self.data_path = Setup_Window.default_data_path + os.sep + Setup_Window.default_data_fname
        self.data_path_entry.insert(0, self.data_path)

        tk.Button(self, text='...', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.open_data).grid(row=r, column=3, sticky=tk.E + tk.W)

        r += 1

        """GO"""
        tk.Button(self, text='Analyze', font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.analyze).grid(row=r, column=columns-2, columnspan=2, sticky=tk.E + tk.W)

        r += 1
        tk.Label(self, text='2021 Teddy Tortorici',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        columnspan=columns,
                                                                        sticky=tk.E + tk.W)

    def open_cal(self):
        self.calibration_path = get_file(ftype='poni', dir=Setup_Window.default_calibration_path)
        self.calibration_path_entry.delete(0, tk.END)
        self.calibration_path_entry.insert(0, self.calibration_path)

    def open_data(self):
        self.data_path = get_file(ftype='tif', dir=Setup_Window.default_data_path)
        self.data_path_entry.delete(0, tk.END)
        self.data_path_entry.insert(0, self.data_path)

    def analyze(self):
        global sample_orientation_g, incident_angle_g
        """Get values from box"""
        sample_orientation_g = int(self.orientation_selection.get())
        incident_angle_g = float(self.angle_entry.get())

        self.killWindow()

    def killWindow(self):
        self.destroy()


if __name__ == '__main__':
    print(start())
