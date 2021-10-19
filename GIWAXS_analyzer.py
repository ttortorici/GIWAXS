import tkinter as tk
import pygix
import os


"""Globals that the setup window will alter"""
sample_orientation_g = -1
incident_angle_g = -1.


def startup():
    global sample_orientation_g, incident_angle_g
    Setup_Window().mainloop()
    sample_orientation = sample_orientation_g
    incident_angle = incident_angle_g
    del sample_orientation_g
    del incident_angle_g


def get_file(ftype='tif', init_dir=os.getcwd()):
    """Opens dialog box to get location of desired file"""
    if not ftype.lower() in ['tif', 'poni']:
        raise ValueError('invalid filetype to retrieve')
    filename = tk.filedialog.askopenfilename(initialdir=init_dir, title=f'Select {ftype.upper()}',
                                             filetypes=((f'{ftype.upper()}', f'*.{ftype.lower()}',), ('all', '*.*')))
    return filename


def load_calibration(poni):
    pg = pygix.Transform()
    pg.load(poni)
    print(pg)
    return pg


class Setup_Window(tk.Tk):
    FONT_SIZE = 10
    FONT = 'Arial'
    default_angle = '0.12'      # degrees

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
        tk.Label(self, text='How was the sample oriented in the beam?',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        sticky=tk.W)

        self.orientation_selection = tk.IntVar(self)
        self.orientation_selection.grid(row=r, column=1, columnspan=2, sticky=tk.E + tk.W)

        self.orientation_selection.set(1)

        tk.Radiobutton(self, text='Horizontal', variable=self.orientation_selection, value=1,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=1)
        tk.Radiobutton(self, text='Vertical', variable=self.orientation_selection, value=2,
                       font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r, column=2)

        r += 1

        """Incident Angle"""
        tk.Label(self, text='Angle of incidence [degrees]',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        sticky=tk.W)
        self.angle_entry = tk.Entry(self, font=(Setup_Window.FONT, Setup_Window.FONT_SIZE))
        self.angle_entry.grid(row=r, column=1, sticky=tk.E + tk.W)
        self.angle_entry.insert(0, Setup_Window.default_angle)

        r += 1

        """GO"""
        tk.Button(self, text='Analyze',
                  font=(Setup_Window.FONT, Setup_Window.FONT_SIZE),
                  command=self.analyze).grid(row=r, column=columns-2, columnspan=2, sticky=tk.E + tk.W)

        r += 1
        tk.Label(self, text='2021 Teddy Tortorici',
                 font=(Setup_Window.FONT, Setup_Window.FONT_SIZE)).grid(row=r,
                                                                        column=0,
                                                                        columnspan=columns,
                                                                        sticky=tk.E + tk.W)

    def analyze(self):
        global sample_orientation_g, incident_angle_g
        """Get values from box"""
        sample_orientation_g = int(self.orientation_selection.get())
        incident_angle_g = float(self.angle_entry.get())

        self.killWindow()

    def killWindow(self):
        self.destroy()











