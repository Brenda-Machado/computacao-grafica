"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

class UiPoint(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('qt_design/new_point.ui', self)
