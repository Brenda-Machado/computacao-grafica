"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from dataclasses import dataclass
from object import Point, Line, Wireframe
from point import UiPoint
from line import UiLine
from wireframe import UiPolygon
from container import Container

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('src/qt_design/test_ui.ui', self)

        self.setCanvas()
        self.setPainter()
        self.setButtons()

        #Determina o nome do objeto
        self.indexes = [1, 1, 1]
        self.displayFile = []

        self.vpSize = [400, 400, 800, 800]
        self.wSize = [0, 0, 1200, 1200]
        
        self.cgViewport = Container(self.vpSize[0], self.vpSize[1], self.vpSize[2], self.vpSize[3])
        self.cgWindow = Container(self.wSize[0], self.wSize[1], self.wSize[2], self.wSize[3])


    def viewportTransformation(self, point):
        xvp = (point.x - self.cgWindow.xMin)/(self.cgWindow.xMax - self.cgWindow.xMin) * (self.cgViewport.xMax - self.cgViewport.xMin) 
        yvp = (1 - ((point.y - self.cgWindow.yMin)/(self.cgWindow.yMax - self.cgWindow.yMin))) * (self.cgViewport.yMax - self.cgViewport.yMin)

        return (round(xvp), round(yvp))
    
    def setCanvas(self):
        canvas = QtGui.QPixmap(400, 400)
        canvas.fill(Qt.white)
        self.mainLabel.setPixmap(canvas)

    def setPainter(self):
        self.painter = QtGui.QPainter(self.mainLabel.pixmap())
        self.pen = QtGui.QPen(Qt.red)
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)

    def setButtons(self):
        self.newPoint.clicked.connect(self.new_point_window)
        self.newLine.clicked.connect(self.new_line_window)
        self.newPoligon.clicked.connect(self.new_polygon_window)

        self.zoomPlus.clicked.connect(self.zoomViewportIn)
        self.zoomMinus.clicked.connect(self.zoomViewportOut)

        self.panRightButton.clicked.connect(self.panRight)
        self.panLeftButton.clicked.connect(self.panLeft)
        self.panUpButton.clicked.connect(self.panUp)
        self.panDownButton.clicked.connect(self.panDown)

        self.RestoreButtom.clicked.connect(self.restoreOriginal)
        self.clear.clicked.connect(self.drawAll)

    def drawOne(self, object):
        if object.type == "Point":
            (x, y) = self.viewportTransformation(object)
            print(x)
            print(y)
            self.painter.drawPoint(x, y)
        elif object.type == "Line":
            (x1, y1) = self.viewportTransformation(object.p1)
            (x2,y2) = self.viewportTransformation(object.p2)
            print(f"Point 1 ({x1}, {y1})")
            print(f"Point 2 ({x2}, {y2})")
            self.painter.drawLine(x1, y1, x2, y2)
        elif object.type == "Polygon":
            ps = []
            for p in object.points:
                ps.append(self.viewportTransformation(p))
            
            for i in range(1, len(ps)):
                self.painter.drawLine(ps[i-1][0], ps[i-1][1], ps[i][0], ps[i][1])
            self.painter.drawLine(ps[-1][0], ps[-1][1], ps[0][0], ps[0][1])

    def drawAll(self):
        self.mainLabel.pixmap().fill(Qt.white)
        for object in self.displayFile:
            self.drawOne(object)
        self.update()

    def new_point_window(self):
        new_point_dialog = UiPoint()
        if new_point_dialog.exec_() and new_point_dialog.xValue.text() and new_point_dialog.yValue.text():
            print("New point")
            x = int(new_point_dialog.xValue.text())
            y = int(new_point_dialog.yValue.text())
            new_point = Point(x, y, "Point {}".format(self.indexes[0]))
            self.displayFile.append(new_point)
            self.indexes[0] += 1
            self.objectList.addItem(new_point.name)
            self.drawOne(new_point)

            self.status.addItem("New Point Added")
        else:
            self.status.addItem("Failure! Something is not correct with the point")

        self.update()

    def new_line_window(self):
        new_line_dialog = UiLine()
        if new_line_dialog.exec_() and new_line_dialog.xValue1.text() and new_line_dialog.xValue2.text() and new_line_dialog.yValue1.text() and new_line_dialog.yValue2.text():
            print("New line")
            
            x1 = int(new_line_dialog.xValue1.text())
            x2 = int(new_line_dialog.xValue2.text())
            y1 = int(new_line_dialog.yValue1.text())
            y2 = int(new_line_dialog.yValue2.text())
            new_line = Line(Point(x1, y1, ""), Point(x2, y2, ""), "Line {}".format(self.indexes[1]))
            self.displayFile.append(new_line)
            self.indexes[1] += 1
            self.objectList.addItem(new_line.name)
            self.drawOne(new_line)

            self.status.addItem("New Line Added")
        else:

            self.status.addItem("Failure! Something is not correct with the line")

        self.update()
    
    def new_polygon_window(self):
        new_polygon_dialog = UiPolygon()
        if new_polygon_dialog.exec_() and new_polygon_dialog.point_list:
            print("New polygon")
            new_poly = Wireframe(new_polygon_dialog.polyList, "Polygon {}".format(self.indexes[2]))
            self.displayFile.append(new_poly)
            self.indexes[2] += 1
            self.objectList.addItem(new_poly.name)
            self.drawOne(new_poly)
            self.status.addItem("New Polygon Added")
        else:
            self.status.addItem("Failure! Something is not correct with the polygon")
        self.update()

    def zoomViewportIn(self):
        #clamp()
        self.cgViewport.xMax += 10
        self.cgViewport.xMin -= 10
        self.cgViewport.yMax += 10
        self.cgViewport.yMin -= 10
        self.drawAll()

    def zoomViewportOut(self):
        #clamp()
        self.cgViewport.xMax -= 10
        self.cgViewport.xMin += 10
        self.cgViewport.yMax -= 10
        self.cgViewport.yMin += 10
        self.drawAll()

    def panRight(self):
        #clamp()
        self.cgWindow.xMax += 100
        self.cgWindow.xMin += 100
        self.drawAll()

    def panLeft(self):
        #clamp()
        self.cgWindow.xMax -= 100
        self.cgWindow.xMin -= 100
        self.drawAll()
    
    def panUp(self):
        #clamp()
        self.cgWindow.yMax += 100
        self.cgWindow.yMin += 100
        self.drawAll()

    def panDown(self):
        #clamp()
        self.cgWindow.yMax -= 100
        self.cgWindow.yMin -= 100
        self.drawAll()

    def restoreOriginal(self):
        self.cgViewport.xMin = self.vpSize[0]
        self.cgViewport.yMin = self.vpSize[1]
        self.cgViewport.xMax = self.vpSize[2]
        self.cgViewport.yMax = self.vpSize[3]
    
        self.cgWindow.xMin = self.wSize[0]
        self.cgWindow.yMin = self.wSize[1]
        self.cgWindow.xMax = self.wSize[2]
        self.cgWindow.yMax = self.wSize[3]
        
        self.drawAll()