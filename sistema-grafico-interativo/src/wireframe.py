"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

from PyQt5 import QtWidgets, uic
from point import UiPoint
from object import Point

class UiPolygon(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('src/qt_design/new_polygon.ui', self)

        self.poly_list = []

        self.point.clicked.connect(self.new_point_window)

    def new_point_window(self):
        new_point_window_dialog = UiPoint()
        if new_point_window_dialog.exec_() and new_point_window_dialog.xValue.text() and new_point_window_dialog.yValue.text():
            print("New Point")
            x = int(new_point_window_dialog.xValue.text())
            y = int(new_point_window_dialog.yValue.text())
            print(x)
            print(y)
            new_point = Point(x, y, "")
            self.poly_list.append(new_point)
            self.point_list.addItem("New Point Added {},{}".format(x,y))
        self.update()