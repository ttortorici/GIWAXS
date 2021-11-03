import pyqtgraph as pg


def bring_to_top(win):
    # set always on top flag, makes window disappear
    win.setWindowFlags(win.windowFlags() | pg.QtCore.Qt.WindowStaysOnTopHint)
    # makes window reappear, but it's ALWAYS on top
    win.show()
    # clear always on top flag, makes window disappear
    win.setWindowFlags(win.windowFlags() & ~pg.QtCore.Qt.WindowStaysOnTopHint)
    # makes window reappear, acts like normal window now (on top now but can be underneath if you raise another window)
    win.show()