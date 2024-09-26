"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('qt_design/test_ui.ui', self)

        canvas = QtGui.QPixmap(400, 300)
        canvas.fill(Qt.white)
        self.mainLabel.setPixmap(canvas)
        self.draw_something()

    def draw_something(self):
        painter = QtGui.QPainter(self.mainLabel.pixmap())
        painter.drawLine(10, 10, 300, 200)
        painter.end()

    def drawPoints(self, qp):
        qp.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        size = self.size()

        if size.height() <= 1 or size.height() <= 1:
            return

        qp.drawPoint(500, 500)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.show()
app.exec_()