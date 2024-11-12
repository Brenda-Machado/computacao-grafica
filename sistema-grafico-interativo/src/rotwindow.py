"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

from PyQt5 import QtWidgets, uic

class UiRotWin(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('src/qt_design/run_window.ui', self)