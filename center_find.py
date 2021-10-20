import tkinter as tk





if __name__ == '__main__':
    def get_file():
        """Opens dialog box to get location of desired file"""
        init_dir = os.getcwd()
        if not ftype.lower() in ['tif', 'poni']:
            raise ValueError('invalid filetype to retrieve')
        filename = tk.filedialog.askopenfilename(initialdir=init_dir, title='Select TIF',
                                                 filetypes=(('TIF', '*.tif',), ('all', '*.*')))
        return filename