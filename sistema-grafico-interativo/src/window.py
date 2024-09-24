"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

import sys
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from dataclasses import dataclass
from object import Point, Line, Wireframe
from point import UiPoint
from line import UiLine
from wireframe import UiPolygon
from container import Container
from transform import UiTransform

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('src/qt_design/test_ui.ui', self)

        self.setCanvas()
        self.setPainter()
        self.setButtons()

        self.indexes = [1, 1, 1]
        self.displayFile = []

        self.vpSize = [0, 0, 400, 400]
        self.wSize = [0, 0, 400, 400]
        
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

        self.transButton.clicked.connect(self.transform_window)
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
        if new_point_dialog.exec_() and new_point_dialog.x_value.text() and new_point_dialog.y_value.text():
            print("New point")
            x = int(new_point_dialog.x_value.text())
            y = int(new_point_dialog.y_value.text())
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
        if new_line_dialog.exec_() and new_line_dialog.x_value1.text() and new_line_dialog.x_value2.text() and new_line_dialog.y_value1.text() and new_line_dialog.y_value2.text():
            print("New line")
            
            x1 = int(new_line_dialog.x_value1.text())
            x2 = int(new_line_dialog.x_value2.text())
            y1 = int(new_line_dialog.y_value1.text())
            y2 = int(new_line_dialog.y_value2.text())
            new_line = Line(Point(x1, y1, ""), Point(x2, y2, ""), "Line {}".format(self.indexes[1]))
            self.displayFile.append(new_line)
            self.indexes[1] += 1
            self.objectList.addItem(new_line.name)
            if new_line_dialog.rValue.text() and new_line_dialog.gValue.text() and new_line_dialog.bValue.text():
        
                self.pen = QtGui.QPen((QtGui.QColor(int(new_line_dialog.rValue.text()), int(new_line_dialog.gValue.text()), int(new_line_dialog.bValue.text()), 255))) 
                self.pen.setWidth(5)
                self.painter.setPen(self.pen)
            self.drawOne(new_line)

            self.status.addItem("New Line Added")
        else:

            self.status.addItem("Failure! Something is not correct with the line")

        self.update()
    
    def new_polygon_window(self):
        new_polygon_dialog = UiPolygon()
        if new_polygon_dialog.exec_() and new_polygon_dialog.point_list:
            print("New polygon")
            new_poly = Wireframe(new_polygon_dialog.poly_list, "Polygon {}".format(self.indexes[2]))
            self.displayFile.append(new_poly)
            self.indexes[2] += 1
            self.objectList.addItem(new_poly.name)
            if new_polygon_dialog.rValue.text() and new_polygon_dialog.gValue.text() and new_polygon_dialog.bValue.text():
                self.pen = QtGui.QPen((QtGui.QColor(int(new_polygon_dialog.rValue.text()), int(new_polygon_dialog.gValue.text()), int(new_polygon_dialog.bValue.text()), 255))) 
                self.pen.setWidth(5)
                self.painter.setPen(self.pen)
            self.drawOne(new_poly)
            self.status.addItem("New Polygon Added")
        else:
            self.status.addItem("Failure! Something is not correct with the polygon")
        self.update()

    def transform_window(self):
        if self.objectList.currentRow() == -1:
            self.status.addItem("Error: you need to select an object.")
            return

        transform_dialog = UiTransform()
        if transform_dialog.exec_():
            if transform_dialog.transX.text() or transform_dialog.transY.text():
                obj = self.displayFile[self.objectList.currentRow()]
                print(obj.name)
                if transform_dialog.transX.text():
                    Dx = int(transform_dialog.transX.text())
                else:
                    Dx = 0

                if transform_dialog.transY.text():
                    Dy = int(transform_dialog.transY.text())
                else:
                    Dy = 0

                self.translation(obj, Dx, Dy)
                self.status.addItem(obj.name + " suceeded on translation.")
                self.drawAll()

            if transform_dialog.escX.text() or transform_dialog.escY.text():
                obj = self.displayFile[self.objectList.currentRow()]
                print(obj.name)

                if transform_dialog.escX.text():
                    Sx = int(transform_dialog.escX.text())
                else:
                    Sx = 1

                if transform_dialog.escY.text():
                    Sy = int(transform_dialog.escY.text())
                else:
                    Sy = 1

                self.escalation(obj, Sx, Sy)
                self.status.addItem(obj.name + " suceeded on escalation.")
                self.drawAll()

            if transform_dialog.rot_angulo.text():
                obj = self.displayFile[self.objectList.currentRow()]
                print(obj.name)
                angle = int(transform_dialog.rot_angulo.text())
                self.rotation(obj, angle, 
                             transform_dialog.rotOrigem.isChecked(), 
                             transform_dialog.rotObject.isChecked(),
                             transform_dialog.rotPoint.isChecked(),
                             transform_dialog.rotPointX.text(),
                             transform_dialog.rotPointY.text())
                self.status.addItem(obj.name + " suceeded on rotation.")
                self.drawAll()
                self.status.addItem(obj.name + " suceeded on transformation")
    
    def find_center(self, obj):
        if obj.type == "Point":
            return (obj.x, obj.y)
        
        if obj.type == "Line":
            x = (obj.p1.x + obj.p2.x)/2
            y = (obj.p1.y + obj.p2.y)/2
            
            return (x, y)
        
        if obj.type == "Polygon":
            x, y = 0, 0
            for i in obj.points:
                x += i.x
                y += i.y 

            x, y = x//len(obj.points), y//len(obj.points)
            
            return (x, y)

    def translation(self, obj, Dx, Dy):
        if obj.type == "Point":
            P = [obj.x, obj.y, 1]
            T = [   [1, 0, 0],
                    [0, 1, 0],
                    [Dx, Dy, 1]
                ]
            (X,Y,W) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
        
        elif obj.type == "Line":
            P1 = [obj.p1.x, obj.p1.y, 1]
            P2 = [obj.p2.x, obj.p2.y, 1]
            T = [   [1, 0, 0],
                    [0, 1, 0],
                    [Dx, Dy, 1]
                ]
            (X1, Y1, W1) = np.matmul(P1, T)
            (X2, Y2, W2) = np.matmul(P2, T)
            obj.p1.x = X1
            obj.p1.y = Y1
            obj.p2.x = X2
            obj.p2.y = Y2

        elif obj.type == "Polygon":
            T = [   [1, 0, 0],
                    [0, 1, 0],
                    [Dx, Dy, 1]
                ]
            for p in obj.points:
                P = (p.x, p.y, 1)
                (X,Y,W) = np.matmul(P, T)
                p.x = X
                p.y = Y 

    def escalation(self, obj, Sx, Sy):
        centroInicial = self.find_center(obj)
        
        if obj.type == "Point":
            P = [obj.x, obj.y, 1]
            T = [   [Sx, 0, 0],
                    [0, Sy, 0],
                    [0, 0, 1]
                ]
            (X,Y,W) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
        
        elif obj.type == "Line":
            P1 = [obj.p1.x, obj.p1.y, 1]
            P2 = [obj.p2.x, obj.p2.y, 1]
            T = [   [Sx, 0, 0],
                    [0, Sy, 0],
                    [0, 0, 1]
                ]
            (X1, Y1, W1) = np.matmul(P1, T)
            (X2, Y2, W2) = np.matmul(P2, T)
            obj.p1.x = X1
            obj.p1.y = Y1
            obj.p2.x = X2
            obj.p2.y = Y2

        elif obj.type == "Polygon":
            centroInicial = self.find_center(obj)

            T = [   [Sx, 0, 0],
                    [0, Sy, 0],
                    [0, 0, 1]
                ]
            for p in obj.points:
                P = (p.x, p.y, 1)
                (X,Y,W) = np.matmul(P, T)
                p.x = X
                p.y = Y 

        final_center = self.find_center(obj)
        dist = (centroInicial[0] - final_center[0], centroInicial[1] - final_center[1])
        self.translation(obj, dist[0], dist[1])

    def rotation(self, obj, degree, toOrigin, toObject, toPoint, pX, pY):
        initial_center = self.find_center(obj)
        
        if toObject:
            self.translation(obj, -initial_center[0], -initial_center[1])
        elif toPoint:
            if not pX or not pY:
                self.status.addItem("Error: rotation point was not set.")
                return
            self.translation(obj, -int(pX), -int(pY))

        if obj.type == "Point":
            P = [obj.x, obj.y, 1]
            T = [   [np.cos(degree), -np.sin(degree), 0],
                    [np.sin(degree), np.cos(degree), 0],
                    [0, 0, 1]
                ]
            (X,Y,W) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
        
        elif obj.type == "Line":
            P1 = [obj.p1.x, obj.p1.y, 1]
            P2 = [obj.p2.x, obj.p2.y, 1]
            T = [   [np.cos(degree), -np.sin(degree), 0],
                    [np.sin(degree), np.cos(degree), 0],
                    [0, 0, 1]
                ]
            (X1, Y1, W1) = np.matmul(P1, T)
            (X2, Y2, W2) = np.matmul(P2, T)
            obj.p1.x = X1
            obj.p1.y = Y1
            obj.p2.x = X2
            obj.p2.y = Y2

        elif obj.type == "Polygon":
            print(toOrigin)
            print(toObject)
            print(toPoint)
            T = [   [np.cos(degree), -np.sin(degree), 0],
                    [np.sin(degree), np.cos(degree), 0],
                    [0, 0, 1]
                 ]
            for p in obj.points:
                P = (p.x, p.y, 1)
                (X,Y,W) = np.matmul(P, T)
                p.x = X
                p.y = Y 

        if toObject:
            self.translation(obj, initial_center[0], initial_center[1])
        elif toPoint:
            self.translation(obj, int(pX), int(pY))

    def zoomViewportIn(self):
        self.cgViewport.xMax += 10
        self.cgViewport.xMin -= 10
        self.cgViewport.yMax += 10
        self.cgViewport.yMin -= 10
        self.drawAll()

    def zoomViewportOut(self):
        self.cgViewport.xMax -= 10
        self.cgViewport.xMin += 10
        self.cgViewport.yMax -= 10
        self.cgViewport.yMin += 10
        self.drawAll()

    def panRight(self):
        self.cgWindow.xMax += 100
        self.cgWindow.xMin += 100
        self.drawAll()

    def panLeft(self):
        self.cgWindow.xMax -= 100
        self.cgWindow.xMin -= 100
        self.drawAll()
    
    def panUp(self):
        self.cgWindow.yMax += 100
        self.cgWindow.yMin += 100
        self.drawAll()

    def panDown(self):
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