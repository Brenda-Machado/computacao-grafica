"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

from PyQt5 import QtWidgets, uic

from point_3d import UiPoint3D
from edge import UiEdge
from object import Point3D

class UiObject3D(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('src/qt_design/new_object_3d.ui', self)

        self.poly_list = []
        self.list_edge = []

        self.point_index = 0
        self.edge_index = 0

        self.point.clicked.connect(self.new_point_window)
        self.edge.clicked.connect(self.new_edge_window)

    def new_point_window(self):
        new_point_window_dialog = UiPoint3D()

        if new_point_window_dialog.exec_() and new_point_window_dialog.xValue.text() and new_point_window_dialog.yValue.text():

            x = int(new_point_window_dialog.xValue.text())
            y = int(new_point_window_dialog.yValue.text())
            z = int(new_point_window_dialog.zValue.text())

            new_point = Point3D(x, y, z)
            self.poly_list.append(new_point)
            self.point_list.addItem("New Point Added {},{}".format(x,y))
            self.point_index += 1

        self.update()
        
    def new_edge_window(self):
        new_edge_dialog = UiEdge()

        if new_edge_dialog.exec_() and new_edge_dialog.p1.text() and new_edge_dialog.p2.text():
            
            if (int(new_edge_dialog.p1.text()) < 0) or (int(new_edge_dialog.p1.text()) >= len(self.poly_list)): 
                return
            if (int(new_edge_dialog.p2.text()) < 0) or (int(new_edge_dialog.p2.text()) >= len(self.poly_list)): 
                return
            
            p1 = int(new_edge_dialog.p1.text())
            p2 = int(new_edge_dialog.p2.text())
            self.list_edge.append((p1, p2))
            self.edge_list.addItem("{}: Edge ({} -> {})".format(self.edge_index, p1, p2))
            self.edge_index += 1
        
        self.update()
