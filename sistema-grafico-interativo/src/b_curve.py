"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from point import UiPoint
from object import Point

class UiBCurve(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('src/qt_design/new_b_curve.ui', self)

        self.curve_list = []

        self.point.clicked.connect(self.point_window)

    def point_window(self):
        new_point_dialog = UiPoint()
        if new_point_dialog.exec_() and new_point_dialog.xValue.text() and new_point_dialog.yValue.text():
            print("New Point")
            x = int(new_point_dialog.xValue.text())
            y = int(new_point_dialog.yValue.text())
            print(x)
            print(y)
            new_point = Point(x, y, "")
            self.curve_list.append(new_point)
            self.point_list.addItem("New Point Added {},{}".format(x,y))
        self.update()
