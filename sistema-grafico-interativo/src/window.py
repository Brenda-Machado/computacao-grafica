"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from functools import reduce
from object import BSplineCurve, Point, Line, Wireframe, Curve2D, Point3D, Object3D
from point import UiPoint
from line import UiLine
from wireframe import UiPolygon
from curve import UiCurve
from b_curve import UiBCurve
from container import Container
from transform import UiTransform
from rotwindow import UiRotWin
from descriptorobj import DescriptorOBJ
from object_3d import UiObject3D
from point_3d import UiPoint3D
from bezier_curve import UiBezierCurve
from transform_3d import UiTransform3D
from curve_fd import UiCurveFd

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('src/qt_design/test_ui.ui', self)

        self.setCanvas()
        self.setPainter()
        self.setButtons()

        self.indexes = [1, 1, 1, 1, 1, 1, 1]
        self.displayFile = []

        self.vpSize = [0, 0, 400, 400]
        self.wSize = [0, 0, 400, 300]
        self.windowAngle = [0,0,0]
        self.projmode = "ortogonal"
        self.perspd = 100
        
        self.cgViewport = Container(self.vpSize[0], self.vpSize[1], self.vpSize[2], self.vpSize[3])
        self.cgWindow = Container(self.wSize[0], self.wSize[1], self.wSize[2], self.wSize[3])
        self.cgWindowPPC = Container(-1,-1,1,1)
        self.cgSubcanvas = Container(20, 20, 380, 380)
        self.descObj = DescriptorOBJ()
        
        
        self.ppcMatrix =    [   [0, 0, 0],
                                [0, 0, 0],
                                [0, 0, 0]
                            ]

        self.ppcMatrix3D =      [   [0, 0, 0, 0],
                                    [0, 0, 0, 0],
                                    [0, 0, 0, 0],
                                    [0, 0, 0, 0]
                                ]
        
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawBorder()

    def viewportTransformation(self, point):
        xvp = (point.cn_x - self.cgWindowPPC.xMin)/(self.cgWindowPPC.xMax - self.cgWindowPPC.xMin) * (self.cgViewport.xMax - self.cgViewport.xMin) 
        yvp = (1 - ((point.cn_y - self.cgWindowPPC.yMin)/(self.cgWindowPPC.yMax - self.cgWindowPPC.yMin))) * (self.cgViewport.yMax - self.cgViewport.yMin)
        
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
        self.newCurve.clicked.connect(self.new_curve_window)
        self.newBSCurve.clicked.connect(self.new_b_curve_window)
        self.newbibezier.clicked.connect(self.new_3d_bezier_window)
        self.newbifd.clicked.connect(self.new_curve_fd_window)

        self.newPoint3D.clicked.connect(self.new_point_3d_window)
        self.newObject3D.clicked.connect(self.new_object_3d_window)

        self.zoomPlus.clicked.connect(self.zoomViewportIn)
        self.zoomMinus.clicked.connect(self.zoomViewportOut)

        self.panRightButton.clicked.connect(self.panRight)
        self.panLeftButton.clicked.connect(self.panLeft)
        self.panUpButton.clicked.connect(self.panUp)
        self.panDownButton.clicked.connect(self.panDown)

        self.transButton.clicked.connect(self.transform_window)
        self.rotWindowButton.clicked.connect(self.run_window)
        self.RestoreButtom.clicked.connect(self.restoreOriginal)
        self.loadButton.clicked.connect(self.loadObjs)

        self.perspSlider.valueChanged.connect(self.perspChange)
        self.projOrt.toggled.connect(self.drawAll)
        self.projPersp.toggled.connect(self.drawAll)

    def drawBorder(self, color=Qt.red):
        self.pen = QtGui.QPen(color)
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)
        points = [(20, 20), (20, 380), (380, 20), (380, 380)]

        polygon = QtGui.QPolygonF()

        for point in points:
            new_point = QtCore.QPointF(point[0], point[1])
            polygon.append(new_point)

        path = QtGui.QPainterPath()
        path.addPolygon(polygon)
        self.painter.setBrush(QtGui.QColor(Qt.red))
        self.painter.drawLine(polygon[0], polygon[1])
        self.painter.drawLine(polygon[0], polygon[2])
        self.painter.drawLine(polygon[1], polygon[3])
        self.painter.drawLine(polygon[2], polygon[3])
        self.update()
    
    def drawOne(self, object):
        self.pen = QtGui.QPen(QtGui.QColor(object.color[0], object.color[1], object.color[2], 255))
        self.pen.setWidth(5)
        self.painter.setPen(self.pen)
        
        if object.dimension == 2:
            self.drawOne2D(object)
        else:
            self.drawOne3D(object)
        self.update()

    def drawOne2D(self, object):
        self.applyPPCmatrixOne(object)

        if object.type == "Point":
            (x, y) = self.viewportTransformation(object)
            if self.pointClipping(x,y):
                self.painter.drawPoint(x, y)

        elif object.type == "Line":
            (x1, y1) = self.viewportTransformation(object.p1)
            (x2,y2) = self.viewportTransformation(object.p2)

            if self.csCheck.isChecked():
                clipRes = self.csLineClipping(x1, y1, x2, y2)
            else:
                clipRes = self.lbLineClipping(x1, y1, x2, y2)

            if clipRes[0]:
                self.painter.drawLine(int(clipRes[1]), int(clipRes[2]), int(clipRes[3]), int(clipRes[4]))

        elif object.type == "Polygon":
            ps = []
            fill_p = []

            for p in object.points:
                ps.append(self.viewportTransformation(p))

            ok, newobj = self.Waclippig(ps)
            nps = newobj[0]
            
            if not ok: 
                return

            for i in range(1, len(nps)):
                self.painter.drawLine(int(nps[i-1][0]), int(nps[i-1][1]), int(nps[i][0]), int(nps[i][1]))
            
                if object.filled:
                    fill_p.append((int(nps[i-1][0]), int(nps[i-1][1])))

            if object.filled:
                fill_p.append((int(nps[-1][0]), int(nps[-1][1])))

            if fill_p:
                polygon = QtGui.QPolygonF()

                for point in fill_p:
                    new_point = QtCore.QPointF(point[0], point[1])
                    polygon.append(new_point)

                path = QtGui.QPainterPath()
                path.addPolygon(polygon)
                self.painter.setBrush(QtGui.QColor(*object.color))
                self.painter.drawPath(path)
                
            if nps[-1] == nps[:-1][-1]: 
                return 
            
            self.painter.drawLine(int(nps[-1][0]), int(nps[-1][1]), int(nps[0][0]), int(nps[0][1]))
        
        elif object.type == "Curve":
            ps = []

            for p in object.points:
                ps.append(self.viewportTransformation(p))
            
            nps = self.curve_clipping(ps)

            if nps:
                for i in range(1, len(nps)):
                    self.painter.drawLine(int(nps[i-1][0]), int(nps[i-1][1]), int(nps[i][0]), int(nps[i][1]))
    
    def drawOne3D(self, object):
        self.applyPPCmatrixOne(object)
        
        if object.type == "Point3D":
            (x, y) = self.viewportTransformation(object)
            
            if self.pointClipping(x,y):
                self.painter.drawPoint(x, y)
                
        elif object.type == "Object3D":
            if (any(p.z < 0 for p in object.points)): 
                return
            
            ps = []
            for p in object.points:
                ps.append(self.viewportTransformation(p))

            nedges = []

            for e in object.edges:
                x1 = ps[e[0]][0]
                y1 = ps[e[0]][1]
                x2 = ps[e[1]][0]
                y2 = ps[e[1]][1]
                ok, nx1, ny1, nx2, ny2 = self.csLineClipping(x1, y1, x2, y2)
                
                if ok:
                    nedges.append(((nx1, ny1),(nx2, ny2)))

            for (p1, p2) in nedges:
                self.painter.drawLine(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]))
        

    def drawAll(self):
        self.mainLabel.pixmap().fill(Qt.white)
        self.drawBorder()

        for object in self.displayFile:
            self.drawOne(object)
            self.drawBorder()
            self.update()
    
    def pointClipping(self, x, y):
        xIn = False
        yIn = False

        if x <= self.cgSubcanvas.xMax and self.cgSubcanvas.xMin <= x:
            xIn = True

        if y <= self.cgSubcanvas.yMax and self.cgSubcanvas.yMin <= y:
            yIn = True

        return xIn and yIn
    
    def rcFinder(self, x, y):
        res = 0
        if y > self.cgSubcanvas.yMax:
            res += 8
        elif y < self.cgSubcanvas.yMin:
            res += 4

        if x < self.cgSubcanvas.xMin:
            res += 1
        elif x > self.cgSubcanvas.xMax:
            res += 2
        return res

    def csLineClipping(self, ox1, oy1, ox2, oy2):
        x1 = ox1
        y1 = oy1

        x2 = ox2
        y2 = oy2

        rc1 = 0
        rc2 = 0
        
        rc1 = rc1 | self.rcFinder(x1, y1)
        rc2 = rc2 | self.rcFinder(x2, y2)

        while True:
            if rc1 == rc2 and rc1 == 0:
                return (True, x1, y1, x2, y2)
            elif rc1 & rc2 != 0:
                return (False, 0, 0, 0, 0)
            
            intX = 0
            intY = 0

            if rc1 != 0:
                rcMax = rc1
            else:
                rcMax = rc2

            if rcMax & 8  == 8:
                intX = x1 + (x2 - x1) * (self.cgSubcanvas.yMax - y1) / (y2 - y1)
                intY = self.cgSubcanvas.yMax
            if rcMax & 4 == 4:
                intX = x1 + (x2 - x1) * (self.cgSubcanvas.yMin - y1) / (y2 - y1)
                intY = self.cgSubcanvas.yMin
            if rcMax & 2 == 2:
                intY = y1 + (y2 - y1) * (self.cgSubcanvas.xMax - x1) / (x2 - x1)
                intX = self.cgSubcanvas.xMax
            if rcMax & 1 == 1:
                intY = y1 + (y2 - y1) * (self.cgSubcanvas.xMin - x1) / (x2 - x1)
                intX = self.cgSubcanvas.xMin

            if rcMax == rc1:
                x1 = intX
                y1 = intY
                rc1 = 0
                rc1 = self.rcFinder(x1, y1)
            else:
                x2 = intX
                y2 = intY
                rc2 = 0
                rc2 = self.rcFinder(x2, y2)

    def lbLineClipping(self, ox1, oy1, ox2, oy2):
        x1 = ox1
        y1 = oy1
        x2 = ox2
        y2 = oy2

        p1 = -(x2 - x1)
        p2 = -p1
        p3 = -(y2 - y1)
        p4 = -p3

        q1 = x1 - self.cgSubcanvas.xMin
        q2 = self.cgSubcanvas.xMax - x1
        q3 = y1 - self.cgSubcanvas.yMin
        q4 = self.cgSubcanvas.yMax - y1

        ps = [p1, p2, p3, p4]
        qs = [q1, q2, q3, q4]

        pcond = False
        qcond = False

        for p in ps:
            if p == 0:
                pcond = True
                break
        if pcond:
            for q in qs:
                if q < 0:
                    qcond = True
        if qcond:
            return (False, 0, 0, 0, 0)
        
        negs = []
        for i in range(4):
            if ps[i] < 0:
                negs.append((ps[i], i))

        poss = []
        for i in range(4):
            if ps[i] > 0:
                poss.append((ps[i], i))

        rns = []
        for neg in negs:
            rns.append(qs[neg[1]]/neg[0])

        rps = []
        for pos in poss:
            rps.append(qs[pos[1]]/pos[0])

        u1 = max(0, max(rns))
        u2 = min(1, min(rps))

        if u1 > u2:
            return (False, 0, 0, 0, 0)
        
        ix1 = x1 + u1 * p2
        iy1 = y1 + u1 * p4

        ix2 = x1 + u2 * p2
        iy2 = y1 + u2 * p4

        return (True, ix1, iy1, ix2, iy2)
    
    def w_a_get_window_index(self, window_vertices, point, code):
        x, y = point
        if x == self.cgSubcanvas.xMax:
            index = window_vertices.index(
                ((self.cgSubcanvas.xMax, self.cgSubcanvas.yMin), 0))
            window_vertices.insert(index, (point, code))

        if x == self.cgSubcanvas.xMin:
            index = window_vertices.index(
                ((self.cgSubcanvas.xMin, self.cgSubcanvas.yMax), 0))
            window_vertices.insert(index, (point, code))

        if y == self.cgSubcanvas.yMax:
            index = window_vertices.index(
                ((self.cgSubcanvas.xMax, self.cgSubcanvas.yMax), 0))
            window_vertices.insert(index, (point, code))

        if y == self.cgSubcanvas.yMin:
            index = window_vertices.index(
                ((self.cgSubcanvas.xMin, self.cgSubcanvas.yMin), 0))
            window_vertices.insert(index, (point, code))

        return window_vertices


    def waLimites(self, points):
        inside = []

        for p in points:
            if (p[0] >= self.cgSubcanvas.xMin
                and p[1] >= self.cgSubcanvas.yMin) and (
                p[0] <= self.cgSubcanvas.xMax
                and p[1] <= self.cgSubcanvas.yMax):
                inside.append(p)

        return inside

    def Waclippig(self, coordinates):
        points_inside = self.waLimites(coordinates)

        if not points_inside:
            return False, [None]
        
        win_vers = [((self.cgSubcanvas.xMin, self.cgSubcanvas.yMax), 0), 
                    ((self.cgSubcanvas.xMax, self.cgSubcanvas.yMax), 0), 
                    ((self.cgSubcanvas.xMax, self.cgSubcanvas.yMin), 0), 
                    ((self.cgSubcanvas.xMin, self.cgSubcanvas.yMin), 0)]
        
        obj_vertices = [(list(c), 0) for c in coordinates]

        total_points = len(coordinates)
        points_inserted = []

        for i in range(total_points):
            p0 = list(coordinates[i])
            p1 = list(coordinates[(i + 1) % total_points])
            
            np0 = [None, None]
            np1 = [None, None]

            visivel, np0[0], np0[1], np1[0], np1[1] = self.csLineClipping(p0[0], p0[1], p1[0], p1[1])
            
            if visivel:
                if np1 != p1:
                    point_idx = obj_vertices.index((p0, 0)) + 1
                    obj_vertices.insert(point_idx, (np1, 2))
                    win_vers = self.w_a_get_window_index(win_vers, np1, 2)

                if np0 != p0:
                    point_idx = obj_vertices.index((p0, 0)) + 1
                    obj_vertices.insert(point_idx, (np0, 1))
                    points_inserted.append((np0, 1))
                    win_vers = self.w_a_get_window_index(win_vers, np0, 1)

    
        new_polygons = []
        new_points = []

        if points_inserted != []:
            while points_inserted != []:
                ref = points_inserted.pop(0)
                rf_p, _ = ref 
                inside_points = [rf_p]
                point_idx = obj_vertices.index(ref) + 1
                new_points.append(ref)

                obj_len = len(obj_vertices)
                for aux_index in range(obj_len):
                    (p, c) = obj_vertices[(point_idx + aux_index) % obj_len]
                    new_points.append((p, c))
                    inside_points.append(p)
                    if c != 0:
                        break 

                ultimo_ponto = new_points[-1]
                point_idx = win_vers.index(ultimo_ponto)
                win_len = len(win_vers)
                for aux_index in range(win_len):
                    (p, c) = win_vers[(point_idx + aux_index) % win_len]
                    new_points.append((p, c))
                    inside_points.append(p)
                    if c != 0:
                        break

                new_polygons.append(inside_points)
            coordinate = new_polygons
        else:
            coordinate = [coordinates]

        return True, coordinate
    
    def curve_clipping(self, points):
        clip_points = []
        started = False

        for i in range(1, len(points)):
            p1 = points[i-1]
            p2 = points[i]

            x1 = p1[0]
            y1 = p1[1]

            x2 = p2[0]
            y2 = p2[1]

            clipped = self.csLineClipping(x1, y1, x2, y2)
            if clipped[0]:
                if started == False: 
                    started = True
                
                clip_points.append((clipped[1], clipped[2]))
                clip_points.append((clipped[3], clipped[4]))
            else:
                if started: 
                    break

        return clip_points

    def new_point_window(self):
        new_point_dialog = UiPoint()

        if new_point_dialog.exec_() and new_point_dialog.xValue.text() and new_point_dialog.yValue.text():
            
            x = int(new_point_dialog.xValue.text())
            y = int(new_point_dialog.yValue.text())
            new_point = Point(x, y, "Point {}".format(self.indexes[0]), 0, 0)
            self.displayFile.append(new_point)
            self.indexes[0] += 1
            self.objectList.addItem(new_point.name)

            if new_point_dialog.rValue.text() and new_point_dialog.gValue.text() and new_point_dialog.bValue.text():
                new_point.color = (int(new_point_dialog.rValue.text()), int(new_point_dialog.gValue.text()), int(new_point_dialog.bValue.text()), 255)
            else:
                new_point.color = (0,0,0,255)

            self.drawOne(new_point)

            self.status.addItem("New Point Added")

        else:
            self.status.addItem("Failure! Something is not correct with the point")

        self.update()

    def new_line_window(self):
        new_line_dialog = UiLine()
        if new_line_dialog.exec_() and new_line_dialog.xValue1.text() and new_line_dialog.xValue2.text() and new_line_dialog.yValue1.text() and new_line_dialog.yValue2.text():
            
            x1 = int(new_line_dialog.xValue1.text())
            x2 = int(new_line_dialog.xValue2.text())
            y1 = int(new_line_dialog.yValue1.text())
            y2 = int(new_line_dialog.yValue2.text())

            new_line = Line(Point(x1, y1, ""), Point(x2, y2, ""), "Line {}".format(self.indexes[1]))
            self.displayFile.append(new_line)
            self.indexes[1] += 1
            self.objectList.addItem(new_line.name)

            if new_line_dialog.rValue.text() and new_line_dialog.gValue.text() and new_line_dialog.bValue.text():
                new_line.color = (int(new_line_dialog.rValue.text()), int(new_line_dialog.gValue.text()), int(new_line_dialog.bValue.text()), 255)
            else:
                new_line.color = (0,0,0,255)

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
                new_poly.color = (int(new_polygon_dialog.rValue.text()), int(new_polygon_dialog.gValue.text()), int(new_polygon_dialog.bValue.text()), 255)
            else:
                new_poly.color = (0,0,0,255)

            if new_polygon_dialog.fillCheckBox.isChecked():
                new_poly.filled = True

            self.drawOne(new_poly)
            self.status.addItem("New Polygon Added")

        else:
            self.status.addItem("Failure! Something is not correct with the polygon")
        
        self.update()
    
    def new_curve_window(self):
        new_curve_dialog = UiCurve()

        if new_curve_dialog.exec_() and len(new_curve_dialog.point_list) >= 4 and new_curve_dialog.precision.text():
            
            ps = new_curve_dialog.curve_list
            precision = float(new_curve_dialog.precision.text())
            cont = 0

            if new_curve_dialog.c1.isChecked(): 
                cont = 1
            elif new_curve_dialog.c2.isChecked(): 
                cont = 2
            elif new_curve_dialog.c3.isChecked(): 
                cont = 3

            if cont == 0 and len(new_curve_dialog.point_list) % 4 != 0:
                self.status.addItem("Number of points must be multiple of 4!")
                self.update()
                return
            elif cont == 1 and (len(new_curve_dialog.point_list) - 4) % 3 != 0:
                self.status.addItem("Number of points must be 4 plus a multiple of 3!")
                self.update()
                return
            elif cont == 2 and (len(new_curve_dialog.point_list) - 4) % 2 != 0:
                self.status.addItem("Number of points must be 4 plus a multiple of 2!")
                self.update()
                return

            curve_points = self.makeCurve(ps, precision, cont)
            new_curve = Curve2D(curve_points, "Curva {}".format(self.indexes[2]))
            self.displayFile.append(new_curve)
            self.indexes[3] += 1
            self.objectList.addItem(new_curve.name)

            if new_curve_dialog.rValue.text() and new_curve_dialog.gValue.text() and new_curve_dialog.bValue.text():
                new_curve.color = ((int(new_curve_dialog.rValue.text()), int(new_curve_dialog.gValue.text()), int(new_curve_dialog.bValue.text()), 255))
            else:
                new_curve.color = (0,0,0,255)

            self.drawOne(new_curve)
            self.status.addItem("New Curve Added")

        else:
            self.status.addItem("Failure! Something is not correct with the curve")
        
        self.update()
    
    def new_b_curve_window(self):
        new_b_curve_dialog = UiBCurve()

        if new_b_curve_dialog.exec_() and len(new_b_curve_dialog.point_list) >= 4 and new_b_curve_dialog.precision.text():
            
            ps = new_b_curve_dialog.curve_list
            precision = float(new_b_curve_dialog.precision.text())
            curve_points = self.makeBSCurve(ps, precision)
            new_curve = BSplineCurve(curve_points, "Curve {}".format(self.indexes[2]))
            self.displayFile.append(new_curve)
            self.indexes[4] += 1
            self.objectList.addItem(new_curve.name)

            if new_b_curve_dialog.rValue.text() and new_b_curve_dialog.gValue.text() and new_b_curve_dialog.bValue.text():
                new_curve.color = ((int(new_b_curve_dialog.rValue.text()), int(new_b_curve_dialog.gValue.text()), int(new_b_curve_dialog.bValue.text()), 255))
            else:
                new_curve.color = (0,0,0,255)

            self.drawOne(new_curve)
            self.status.addItem("New B-Spline Curve Added")

        else:
            self.status.addItem("Failure! Something is not correct with the curve")
        
        self.update()
    
    def new_point_3d_window(self):
        new_point_dialog = UiPoint3D()

        if new_point_dialog.exec_() and (
            new_point_dialog.xValue.text() and 
            new_point_dialog.yValue.text() and
            new_point_dialog.zValue.text()):
            
            x = int(new_point_dialog.xValue.text())
            y = int(new_point_dialog.yValue.text())
            z = int(new_point_dialog.zValue.text())
            
            new_point = Point3D(x, y, z, "Point 3D{}".format(self.indexes[5]), 0, 0)
            self.displayFile.append(new_point)
            self.indexes[5] += 1
            self.objectList.addItem(new_point.name)

            if new_point_dialog.rValue.text() and new_point_dialog.gValue.text() and new_point_dialog.bValue.text():
                new_point.color = (int(new_point_dialog.rValue.text()), int(new_point_dialog.gValue.text()), int(new_point_dialog.bValue.text()), 255)
            else:
                new_point.color = (0,0,0,255)

            self.drawOne(new_point)
            self.status.addItem("New Point 3D Added")

        else:
            self.status.addItem("Failure! Something is not correct with the point")

        self.update()
        
    def new_object_3d_window(self):
        new_object_window = UiObject3D()

        if new_object_window.exec_() and new_object_window.poly_list and new_object_window.edge_list:
            new_object = Object3D(new_object_window.poly_list, new_object_window.edge_list,"Polygon {}".format(self.indexes[2]))
            self.displayFile.append(new_object)
            self.indexes[2] += 1
            self.objectList.addItem(new_object.name)

            if new_object_window.rValue.text() and new_object_window.gValue.text() and new_object_window.bValue.text():
                new_object.color = ((int(new_object_window.rValue.text()), int(new_object_window.gValue.text()), int(new_object_window.bValue.text()), 255))
            else:
                new_object.color = (0,0,0,255)

            self.drawOne(new_object)
            self.status.addItem("New Object 3D Added")

        else:
            self.status.addItem("Failure! Something is not correct with the object")

        self.update()
    
    def new_3d_bezier_window(self):
        new_bezier_curve = UiBezierCurve()

        p1 = Point3D(int(new_bezier_curve.xValue.text()), int(new_bezier_curve.yValue.text()), int(new_bezier_curve.zValue.text()))
        p2 = Point3D(int(new_bezier_curve.xValue_2.text()), int(new_bezier_curve.yValue_2.text()), int(new_bezier_curve.zValue_2.text()))
        p3 = Point3D(int(new_bezier_curve.xValue_3.text()), int(new_bezier_curve.yValue_3.text()), int(new_bezier_curve.zValue_3.text()))
        p4 = Point3D(int(new_bezier_curve.xValue_4.text()), int(new_bezier_curve.yValue_4.text()), int(new_bezier_curve.zValue_4.text()))
        p5 = Point3D(int(new_bezier_curve.xValue_5.text()), int(new_bezier_curve.yValue_5.text()), int(new_bezier_curve.zValue_5.text()))
        p6 = Point3D(int(new_bezier_curve.xValue_6.text()), int(new_bezier_curve.yValue_6.text()), int(new_bezier_curve.zValue_6.text()))
        p7 = Point3D(int(new_bezier_curve.xValue_7.text()), int(new_bezier_curve.yValue_7.text()), int(new_bezier_curve.zValue_7.text()))
        p8 = Point3D(int(new_bezier_curve.xValue_8.text()), int(new_bezier_curve.yValue_8.text()), int(new_bezier_curve.zValue_8.text()))
        p9 = Point3D(int(new_bezier_curve.xValue_9.text()), int(new_bezier_curve.yValue_9.text()), int(new_bezier_curve.zValue_9.text()))
        p10 = Point3D(int(new_bezier_curve.xValue_10.text()), int(new_bezier_curve.yValue_10.text()), int(new_bezier_curve.zValue_10.text()))
        p11 = Point3D(int(new_bezier_curve.xValue_11.text()), int(new_bezier_curve.yValue_11.text()), int(new_bezier_curve.zValue_11.text()))
        p12 = Point3D(int(new_bezier_curve.xValue_12.text()), int(new_bezier_curve.yValue_12.text()), int(new_bezier_curve.zValue_12.text()))
        p13 = Point3D(int(new_bezier_curve.xValue_13.text()), int(new_bezier_curve.yValue_13.text()), int(new_bezier_curve.zValue_13.text()))
        p14 = Point3D(int(new_bezier_curve.xValue_14.text()), int(new_bezier_curve.yValue_14.text()), int(new_bezier_curve.zValue_14.text()))
        p15 = Point3D(int(new_bezier_curve.xValue_15.text()), int(new_bezier_curve.yValue_15.text()), int(new_bezier_curve.zValue_15.text()))
        p16 = Point3D(int(new_bezier_curve.xValue_16.text()), int(new_bezier_curve.yValue_16.text()), int(new_bezier_curve.zValue_16.text()))
        
        precision = 0.2
        
        ps = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16]
        
        gbsx = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        gbsy = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        gbsz = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        
        p = 0

        for i in range(4):
            for j in range(4):
                gbsx[i][j] = ps[p].x
                gbsy[i][j] = ps[p].y
                gbsz[i][j] = ps[p].z
                p += 1
        
        mb = [[-1, 3, -3, 1],
              [3, -6, 3, 0],
              [-3, 3, 0, 0],
              [1, 0, 0, 0]]
        
        newxs = []
        newys = []
        newzs = []
        
        for s in np.arange(0, 1, precision):
            for t in np.arange(0, 1, precision):
                mats = [s**3, s**2, s, 1]
                matt = [t**3, t**2, t, 1]
                xst = reduce(np.dot, [mats, mb, gbsx, np.array(mb).T, np.array(matt).T])
                yst = reduce(np.dot, [mats, mb, gbsy, np.array(mb).T, np.array(matt).T])
                zst = reduce(np.dot, [mats, mb, gbsz, np.array(mb).T, np.array(matt).T])
                newxs.append(xst)
                newys.append(yst)
                newzs.append(zst)
                
        points = []
        edges = []
        zipped = list(zip(newxs, newys, newzs))

        for p in zipped:
            points.append(Point3D(p[0], p[1], p[2]))
            
        for i in range(1, len(points)):
            edges.append((i-1, i))
            
        newbibezier = Object3D(points, edges, "Curve 3D {}".format(self.indexes[6]))
        self.displayFile.append(newbibezier)
        self.indexes[6] += 1
        self.objectList.addItem(newbibezier.name)
        self.drawOne(newbibezier)
        self.status.addItem("New Object 3D Added")
        self.update()
    
    def new_curve_fd_window(self):

        NewBfFdDialog = UiCurveFd()
        matrix = []

        if NewBfFdDialog.exec_() and NewBfFdDialog.xValue.text():
            linhaValues = int(NewBfFdDialog.xValue.text())
            matrix =  [[None for _ in range(linhaValues)] for _ in range(linhaValues)]

            for linha in range(linhaValues):
                for coluna in range(linhaValues):
                    
                    novoPontoDialog = UiPoint3D()
                    if novoPontoDialog.exec_() and (
                        novoPontoDialog.xValue.text() and 
                        novoPontoDialog.yValue.text() and
                        novoPontoDialog.zValue.text()):
                        
                        x = int(novoPontoDialog.xValue.text())
                        y = int(novoPontoDialog.yValue.text())
                        z = int(novoPontoDialog.zValue.text())
                        
                        matrix[linha][coluna] = Point3D(x, y, z)

        ns = 2
        nt = 2
        
        ax = [[0 for _ in range(linhaValues)]] * linhaValues
        ay = [[0 for _ in range(linhaValues)]] * linhaValues
        az = [[0 for _ in range(linhaValues)]] * linhaValues
        
        matrix = self.testeMatrix()
        p = 0

        for i in range(linhaValues):
            for j in range(linhaValues):
                print(matrix[i][j])
                ax[i][j] = matrix[i][j].x
                ay[i][j] = matrix[i][j].y
                az[i][j] = matrix[i][j].z
                p += 1
                
        b = [[-1, 3, -3, 1],
              [3, -6, 3, 0],
              [-3, 3, 0, 0],
              [1, 0, 0, 0]]
        
        cx = np.dot(np.dot(b, ax), b)
        cy = np.dot(np.dot(b, ay), b)
        cz = np.dot(np.dot(b, az), b)

        deltaS = 1/(ns-1)
        deltaT = 1/(nt-1)
        
        Es = [[0 for _ in range(4)]] * 4
        Et = [[0 for _ in range(4)]] * 4
        
        Es[0][0] = 0
        Es[0][1] = 0
        Es[0][2] = 0
        Es[0][3] = 1
        Es[1][0] = deltaS ** 3
        Es[1][1] = deltaS ** 2
        Es[1][2] = deltaS
        Es[1][3] = 0
        Es[2][0] = 6 * (deltaS ** 3)
        Es[2][1] = 2 * (deltaS ** 2)
        Es[2][2] = 0
        Es[2][3] = 0
        Es[3][0] = 6 * (deltaS ** 3)
        Es[3][1] = 0
        Es[3][2] = 0
        Es[3][3] = 0
        Et[0][0] = 0
        Et[0][1] = 0
        Et[0][2] = 0
        Et[0][3] = 1
        Et[1][0] = deltaT ** 3
        Et[1][1] = deltaT ** 2
        Et[1][2] = deltaT
        Et[1][3] = 0
        Et[2][0] = 6 * (deltaT ** 3)
        Et[2][1] = 2 * (deltaT ** 2)
        Et[2][2] = 0
        Et[2][3] = 0
        Et[3][0] = 6 * (deltaT ** 3)
        Et[3][1] = 0
        Et[3][2] = 0
        Et[3][3] = 0

        Et = np.array(Et).T
        
        DDx, DDy, DDz = self.refazDD(cx, cy, cz, Es, Et)

        points = []
        edges = []
        
        for i in range(ns):
            self.umaCurva(nt,
                          DDx[0][0], DDx[0][1], DDx[0][2], DDx[0][3],
                          DDy[0][0], DDy[0][1], DDy[0][2], DDy[0][3],
                          DDz[0][0], DDz[0][1], DDz[0][2], DDz[0][3],
                          points, edges)
            self.somaDD(DDx, DDy, DDz)
            
        DDx, DDy, DDz = self.refazDD(cx, cy, cz, Es, Et)
        
        DDx = np.array(DDx).T
        DDy = np.array(DDy).T
        DDz = np.array(DDz).T
        
        for i in range(nt):
            self.umaCurva(ns,
                          DDx[0][0], DDx[0][1], DDx[0][2], DDx[0][3],
                          DDy[0][0], DDy[0][1], DDy[0][2], DDy[0][3],
                          DDz[0][0], DDz[0][1], DDz[0][2], DDz[0][3],
                          points, edges)
            self.somaDD(DDx, DDy, DDz)
            

        newbifd = Object3D(points, edges)
        self.displayFile.append(newbifd)
        self.indexes[6] += 1
        self.objectList.addItem(newbifd.name)
        self.drawOne(newbifd)
        self.status.addItem("Polígono 3D adicionado com sucesso.")
        self.update()
        
    
    def refazDD(self, cx, cy, cz, Es, Et):
        DDx = np.dot(np.dot(Es, cx), Et)
        DDy = np.dot(np.dot(Es, cy), Et)
        DDz = np.dot(np.dot(Es, cz), Et)

        return (DDx, DDy, DDz)
    
    def testeMatrix(self):
        p11 = Point3D(150, 190, 170)
        p12 = Point3D(190, 190, 170)
        p13 = Point3D(130, 190, 170)
        p14 = Point3D(170, 190, 170)
        
        p21 = Point3D(190, 190, 180)
        p22 = Point3D(100, 140, 180)
        p23 = Point3D(190, 140, 180)
        p24 = Point3D(160, 190, 180)
        
        p31 = Point3D(130, 190, 190)
        p32 = Point3D(190, 140, 190)
        p33 = Point3D(160, 140, 190)
        p34 = Point3D(160, 190, 190)
        
        p41 = Point3D(170, 190, 200)
        p42 = Point3D(160, 190, 200)
        p43 = Point3D(160, 190, 200)
        p44 = Point3D(160, 190, 200)
        matrix = [  [p11, p12, p13, p14],
                    [p21, p22, p23, p24],
                    [p31, p32, p33, p34],
                    [p41, p42, p43, p44]]
        return matrix    
    
    def umaCurva(self, n,   x, Dx, D2x, D3x, 
                            y, Dy, D2y, D3y,
                            z, Dz, D2z, D3z,
                            points, edges):
        
        oldX, oldY, oldZ = x, y, z
        points.append(Point3D(oldX, oldY, oldZ))
        
        for i in range(1, n):
            x += Dx
            Dx += D2x
            D2x += D3x
            
            y += Dy
            Dy += D2y
            D2y += D3y
            
            z += Dz
            Dz += D2z
            D2z += D3z
            
            points.append(Point3D(x, y, z))
            edges.append((i-1, i))
            oldX = x
            oldY = y
            oldZ = z
            
    def somaDD(self, DDx, DDy, DDz):
        DDx[0][0] += DDx[1][0]
        DDx[0][1] += DDx[1][1]
        DDx[0][2] += DDx[1][2]
        DDx[0][3] += DDx[1][3]
        DDy[0][0] += DDy[1][0]
        DDy[0][1] += DDy[1][1]
        DDy[0][2] += DDy[1][2]
        DDy[0][3] += DDy[1][3]
        DDz[0][0] += DDz[1][0]
        DDz[0][1] += DDz[1][1]
        DDz[0][2] += DDz[1][2]
        DDz[0][3] += DDz[1][3]
    
        DDx[1][0] += DDx[2][0]
        DDx[1][1] += DDx[2][1]
        DDx[1][2] += DDx[2][2]
        DDx[1][3] += DDx[2][3]

        DDy[1][0] += DDy[2][0]
        DDy[1][1] += DDy[2][1]
        DDy[1][2] += DDy[2][2]
        DDy[1][3] += DDy[2][3]

        DDz[1][0] += DDz[2][0]
        DDz[1][1] += DDz[2][1]
        DDz[1][2] += DDz[2][2]
        DDz[1][3] += DDz[2][3]
        
        DDx[2][0] += DDx[3][0]
        DDx[2][1] += DDx[3][1]
        DDx[2][2] += DDx[3][2]
        DDx[2][3] += DDx[3][3]
        
        DDy[2][0] += DDy[3][0]
        DDy[2][1] += DDy[3][1]
        DDy[2][2] += DDy[3][2]
        DDy[2][3] += DDy[3][3]
        
        DDz[2][0] += DDz[3][0]
        DDz[2][1] += DDz[3][1]
        DDz[2][2] += DDz[3][2]
        DDz[2][3] += DDz[3][3]

    def getBlending(self, t):
        return [(1 - t) ** 3, 3 * t * ((1 - t) ** 2), 3 * (t ** 2) * (1 - t), t ** 3]

    def makeCurve(self, poly_list, precision, cont):
        prelistsX = []
        prelistsY = []
        newlistsX = []
        newlistsY = []
        
        step = 0

        if cont == 0: 
            step = 4
        elif cont == 1: 
            step = 3
        elif cont == 2: 
            step = 2
        elif cont == 3: 
            step = 1

        for i in range(3, len(poly_list), step):
            prelistsX.append([poly_list[i-3].x, poly_list[i-2].x, poly_list[i-1].x, poly_list[i].x])
            prelistsY.append([poly_list[i-3].y, poly_list[i-2].y, poly_list[i-1].y, poly_list[i].y])

        for i in range(len(prelistsX)):
            t = 0

            while t < 1:
                newlistsX.append(np.dot(self.getBlending(t), prelistsX[i]))
                newlistsY.append(np.dot(self.getBlending(t), prelistsY[i]))
                t += precision

            newlistsX.append(np.dot(self.getBlending(1), prelistsX[i]))
            newlistsY.append(np.dot(self.getBlending(1), prelistsY[i]))
        
        coords = list(zip(newlistsX, newlistsY))
        ps = []

        for c in coords:
            ps.append(Point(c[0], c[1]))
        return ps
    
    def calculate_bspline_param(self, points, precision):
        MBS = np.array(
        [
            [-1 / 6, 1 / 2, -1 / 2, 1 / 6],
            [1 / 2, -1, 1 / 2, 0],
            [-1 / 2, 0, 1 / 2, 0],
            [1 / 6, 2 / 3, 1 / 6, 0],
        ]
        )

        GBS_x = []
        GBS_y = []
        for point in points:
            GBS_x.append(point.x)
            GBS_y.append(point.y)

        GBS_x = np.array([GBS_x]).T 
        coeff_x = MBS.dot(GBS_x).T[0]
        aX, bX, cX, dX = coeff_x
        init_diff_x = [
               dX,
                aX * (precision ** 3) + bX * (precision ** 2) + cX * precision,
                6 * aX * (precision ** 3) + 2 * bX * (precision ** 2),
                6 * aX * (precision ** 3)
                    ]

        GBS_y = np.array([GBS_y]).T 
        coeff_y = MBS.dot(GBS_y).T[0]
        aY, bY, cY, dY = coeff_y
        init_diff_y = [
               dY,
                aY * (precision ** 3) + bY * (precision ** 2) + cY * precision,
                6 * aY * (precision ** 3) + 2 * bY * (precision ** 2),
                6 * aY * (precision ** 3)
                    ]
        return init_diff_x, init_diff_y

    def makeBSCurve(self, poly_list, precision):
        spline_points = []
        iterations = int(1/precision)
        num_points = len(poly_list)
        min_points = 4 

        for i in range(0, num_points):
            upper_bound = i + min_points

            if upper_bound > num_points:
                break
            points = poly_list[i:upper_bound]
            
            delta_x, delta_y = self.calculate_bspline_param(points, precision)
            x = delta_x[0]
            y = delta_y[0]

            spline_points.append(Point(x, y))
            for _ in range(0, iterations):
                x += delta_x[1]
                delta_x[1] += delta_x[2] 
                delta_x[2] += delta_x[3]
                
                y += delta_y[1]
                delta_y[1] += delta_y[2] 
                delta_y[2] += delta_y[3]

                spline_points.append(Point(x, y))

        return spline_points

    def transform_window(self):
        if self.objectList.currentRow() == -1:
            self.status.addItem("Error: you need to select an object.")
            return

        if self.displayFile[self.objectList.currentRow()].dimension == 2:
            self.transform2D()
        else:
            self.transform3D()
    
    def transform2D(self):
        transform_dialog = UiTransform()

        if transform_dialog.exec_():

            if transform_dialog.transX.text() or transform_dialog.transY.text():
                obj = self.displayFile[self.objectList.currentRow()]

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

    def transforma3D(self):
        transform_dialog = UiTransform3D()

        if transform_dialog.exec_():

            if transform_dialog.transX.text() or transform_dialog.transY.text() or transform_dialog.transZ.text():
                obj = self.displayFile[self.objectList.currentRow()]

                if transform_dialog.transX.text():
                    Dx = int(transform_dialog.transX.text())
                else:
                    Dx = 0

                if transform_dialog.transY.text():
                    Dy = int(transform_dialog.transY.text())
                else:
                    Dy = 0
                    
                if transform_dialog.transZ.text():
                    Dz = int(transform_dialog.transZ.text())
                else:
                    Dz = 0

                self.translation3D(obj, Dx, Dy, Dz)
                self.status.addItem(obj.name + " suceeded on translation.")
                self.drawAll()

            if transform_dialog.escX.text() or transform_dialog.escY.text() or transform_dialog.escZ.text():
                obj = self.displayFile[self.objectList.currentRow()]

                if transform_dialog.escX.text():
                    Sx = int(transform_dialog.escX.text())
                else:
                    Sx = 1

                if transform_dialog.escY.text():
                    Sy = int(transform_dialog.escY.text())
                else:
                    Sy = 1
                    
                if transform_dialog.escZ.text():
                    Sz = int(transform_dialog.escZ.text())
                else:
                    Sz = 1

                self.escalation3D(obj, Sx, Sy, Sz)
                self.status.addItem(obj.name + " suceeded on escalation.")
                self.drawAll()

            if transform_dialog.rotX.text() or transform_dialog.rotY.text() or transform_dialog.rotZ.text():
                obj = self.displayFile[self.objectList.currentRow()]
                
                if transform_dialog.rotX.text():
                    Rx = int(transform_dialog.rotX.text())
                else:
                    Rx = 0
                    
                if transform_dialog.rotY.text():
                    Ry = int(transform_dialog.rotY.text())
                else:
                    Ry = 0
                    
                if transform_dialog.rotZ.text():
                    Rz = int(transform_dialog.rotZ.text())
                else:
                    Rz = 0
                    
                self.rotation3D(obj, Rx, Ry, Rz, 
                             transform_dialog.rotOrigem.isChecked(), 
                             transform_dialog.rotObject.isChecked(),
                             transform_dialog.rotPoint.isChecked(),
                             transform_dialog.rotPointX.text(),
                             transform_dialog.rotPointY.text(),
                             transform_dialog.rotPointZ.text())
                self.status.addItem(obj.name + " suceeded on rotation.")
                self.drawAll()
                self.status.addItem(obj.name + " duceeded on translation.")

    def run_window(self):
        rotDialog = UiRotWin()

        if rotDialog.exec_():

            if rotDialog.rotX.text() or rotDialog.rotY.text() or rotDialog.rotZ.text():
                
                if (rotDialog.rotX.text()):
                    angX = int(rotDialog.rotX.text())
                else:
                    angX = 0

                self.windowAngle[0] -= angX
                
                if (rotDialog.rotY.text()):
                    angY = int(rotDialog.rotY.text())
                else:
                    angY = 0

                self.windowAngle[1] -= angY
                
                if (rotDialog.rotZ.text()):
                    angZ = int(rotDialog.rotZ.text())
                else:
                    angZ = 0

                self.windowAngle[2] -= angZ
                
                self.makePPCmatrix()
                self.applyPPCmatrixWindow()
                self.drawAll()

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

        if obj.type == "Point3D":
            return (obj.x, obj.y, obj.z)
        
        if obj.type == "Object3D":
            x, y, z = 0, 0, 0
            for i in obj.points:
                x += i.x
                y += i.y
                z += i.z
            x, y, z = x//len(obj.points), y//len(obj.points), z//len(obj.points)
            return(x, y, z)

    def find_window_center(self):
        x = (self.cgWindow.xMin + self.cgWindow.xMax)/2
        y = (self.cgWindow.yMin + self.cgWindow.yMax)/2

        return (x,y)

    def makePPCmatrix(self):
        width = self.cgWindow.xMax - self.cgWindow.xMin
        height = self.cgWindow.yMax - self.cgWindow.yMin
        center = self.find_window_center()
        
        #2D
        matTrans =  [   [1, 0, 0],
                        [0, 1, 0],
                        [-center[0], -center[1], 1]
                    ]

        angZ = np.deg2rad(self.windowAngle[2])
        angX = np.deg2rad(self.windowAngle[0])
        angY = np.deg2rad(self.windowAngle[1])

        matRot =    [   [np.cos(angZ), -np.sin(angZ), 0],
                        [np.sin(angZ), np.cos(angZ), 0],
                        [0, 0, 1]
                    ]
        
        matScale =  [   [2/width,   0,          0],
                        [0,         2/height,   1],
                        [0,         0,          1]

                    ]
        
        matPPC = np.dot(np.dot(matTrans, matRot), matScale)
        self.ppcMatrix = matPPC
        
        #3D
        matTrans3D =  [   [1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [-center[0], -center[1], 1, 1]
                    ]

        angZ = np.deg2rad(self.windowAngle[2])
        angX = np.deg2rad(self.windowAngle[0])
        angY = np.deg2rad(self.windowAngle[1])

        Rx = [  [1, 0, 0, 0],
                    [0, np.cos(angX), np.sin(angX), 0],
                    [0, -np.sin(angX), np.cos(angX), 0],
                    [0, 0, 0, 1],
                ]
        Ry = [  [np.cos(angY), 0, -np.sin(angY), 0],
                [0, 1, 0, 0],
                [np.sin(angY), 0, np.cos(angY), 0],
                [0, 0, 0, 1],
            ]
        Rz = [  [np.cos(angZ), np.sin(angZ), 0, 0],
                [-np.sin(angZ), np.cos(angZ), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        
        matRot3D = np.dot(np.dot(Rx, Ry), Rz)
        
        matScale3D =  [   [2/width,   0,          0, 0],
                        [0,         2/height,   0, 0],
                        [0,         0,          1, 0],
                        [0 , 0, 0 , 1]
                    ]
        
        matPPC3D = np.dot(np.dot(matTrans3D, matRot3D), matScale3D)
        self.ppcMatrix3D = matPPC3D

    def applyPPCmatrixOne(self, obj):
        if obj.type == "Point":
            P = [obj.x, obj.y, 1]
            (X,Y,W) = np.dot(P, self.ppcMatrix)
            obj.cn_x = X
            obj.cn_y = Y

        elif obj.type == "Line":
            P1 = [obj.p1.x, obj.p1.y, 1]
            P2 = [obj.p2.x, obj.p2.y, 1]
            (X1, Y1, W1) = np.dot(P1, self.ppcMatrix)
            (X2, Y2, W2) = np.dot(P2, self.ppcMatrix)
            obj.p1.cn_x = X1
            obj.p1.cn_y = Y1
            obj.p2.cn_x = X2
            obj.p2.cn_y = Y2

        elif obj.type == "Polygon" or obj.type == "Curve":
            for p in obj.points:
                P = (p.x, p.y, 1)
                (X,Y,W) = np.matmul(P, self.ppcMatrix)
                p.cn_x = X
                p.cn_y = Y

        elif obj.type == "Point3D": 
            if self.projPersp.isChecked():
                nx = obj.x/(obj.z/self.perspd)
                ny = obj.y/(obj.z/self.perspd)
                P = (nx, ny, obj.z, 1)
            else:
                P = (obj.x, obj.y, obj.z, 1)
            
            (X,Y,Z,_) = np.dot(P, self.ppcMatrix3D)
            obj.cn_x = X
            obj.cn_y = Y
            obj.cn_z = Z

        elif obj.type == "Object3D":
            for p in obj.points:
                if self.projPersp.isChecked():
                    nx = p.x/(p.z/self.perspd)
                    ny = p.y/(p.z/self.perspd)
                    P = (nx, ny, p.z, 1)
                else:
                    P = (p.x, p.y, p.z, 1)
                
                (X,Y,Z, W) = np.matmul(P, self.ppcMatrix3D)
                p.cn_x = X
                p.cn_y = Y
                p.cn_z = Z

    def applyPPCmatrixAll(self):
        for obj in self.displayFile:
            self.applyPPCmatrixOne(obj)

    def applyPPCmatrixWindow(self):
        p1 = Point(self.cgWindow.xMin, self.cgWindow.yMin)
        p2 = Point(self.cgWindow.xMin, self.cgWindow.yMax)
        p3 = Point(self.cgWindow.xMax, self.cgWindow.yMax)
        p4 = Point(self.cgWindow.xMax, self.cgWindow.yMin)
        temp = Wireframe([p1, p2, p3, p4])
        self.applyPPCmatrixOne(temp)

        xs = []
        ys = []
        for point in temp.points:
            xs.append(point.cn_x)
            ys.append(point.cn_y)

        xmin = min(xs)
        ymin = min(ys)
        xmax = max(xs)
        ymax = max(ys)

        self.cgWindowPPC.xMin = xmin
        self.cgWindowPPC.yMin = ymin
        self.cgWindowPPC.xMax = xmax
        self.cgWindowPPC.yMax = ymax


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
    
    def translation3D(self, obj, Dx, Dy, Dz):
        if obj.type == "Point3D":
            P = [obj.x, obj.y, obj.z, 1]
            T = [   [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [Dx, Dy, Dz, 1]
                ]
            (X,Y,Z, _) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
            obj.z = Z

        elif obj.type == "Object3D":
            T = [   [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [Dx, Dy, Dz, 1]
                ]
            for p in obj.points:
                P = (p.x, p.y, p.z, 1)
                (X,Y,Z, _) = np.matmul(P, T)
                p.x = X
                p.y = Y
                p.z = Z

    def escalation(self, obj, Sx, Sy):
        initial_center = self.find_center(obj)
        
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
            initial_center = self.find_center(obj)

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
        dist = (initial_center[0] - final_center[0], initial_center[1] - final_center[1])
        self.translation(obj, dist[0], dist[1])
    
    def escalonamento3D(self, obj, Sx, Sy, Sz):
        initial_center = self.find_center(obj)
        if obj.type == "Point3D":
            P = [obj.x, obj.y, obj.z, 1]
            T = [   [Sx, 0, 0, 0],
                    [0, Sy, 0, 0],
                    [0, 0, Sz, 0],
                    [0, 0, 0, 1]
                ]
            (X,Y,Z,_) = np.matmul(P, T)
            obj.x = X
            obj.y = Y
            obj.z = Z
        
        elif obj.type == "Object3D":
            initial_center = self.find_center(obj)

            T = [   [Sx, 0, 0, 0],
                    [0, Sy, 0, 0],
                    [0, 0, Sz, 0],
                    [0, 0, 0, 1]
                ]
            for p in obj.points:
                P = (p.x, p.y, p.z, 1)
                (X,Y,Z,_) = np.matmul(P, T)
                p.x = X
                p.y = Y
                p.z = Z

        final_center = self.find_center(obj)
        dist = (initial_center[0] - final_center[0], initial_center[1] - final_center[1], initial_center[2] - final_center[2])
        self.translation3D(obj, dist[0], dist[1], dist[2])

    def rotation(self, obj, degree, toOrigin, toObject, toPoint, pX, pY):
        degree = np.deg2rad(degree)
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
    
    def rotacao3D(self, obj, rotX, rotY, rotZ, toOrigin, toObject, toPoint, pX, pY, pZ):
        rotX = np.deg2rad(rotX)
        rotY = np.deg2rad(rotY)
        rotZ = np.deg2rad(rotZ)
        initial_center = self.find_center(obj)

        if toObject:
            self.translation3D(obj, -initial_center[0], -initial_center[1], -initial_center[2])
        elif toPoint:
            if not pX or not pY or not pZ:
                self.status.addItem("Error: rotation point was not set.")
                return
            self.translation(obj, -int(pX), -int(pY), -int(pZ))

        if obj.type == "Point":
            P = [obj.x, obj.y, obj.z, 1]

            Tx = [  [1, 0, 0, 0],
                    [0, np.cos(rotX), np.sin(rotX), 0],
                    [0, -np.sin(rotX), np.cos(rotX), 0],
                    [0, 0, 0, 1],
                ]
            Ty = [  [np.cos(rotY), 0, -np.sin(rotY), 0],
                    [0, 1, 0, 0],
                    [np.sin(rotY), 0, np.cos(rotY), 0],
                    [0, 0, 0, 1],
                ]
            Tz = [  [np.cos(rotZ), np.sin(rotZ), 0, 0],
                    [-np.sin(rotZ), np.cos(rotZ), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ]
            R = np.matmul(P, Tx)
            R = np.matmul(R, Ty)
            (X, Y, Z, _) = np.matmul(R, Tz)
            obj.x = X
            obj.y = Y
            obj.z = Z

        elif obj.type == "Object3D":
            Tx = [  [1, 0, 0, 0],
                    [0, np.cos(rotX), np.sin(rotX), 0],
                    [0, -np.sin(rotX), np.cos(rotX), 0],
                    [0, 0, 0, 1],
                ]
            Ty = [  [np.cos(rotY), 0, -np.sin(rotY), 0],
                    [0, 1, 0, 0],
                    [np.sin(rotY), 0, np.cos(rotY), 0],
                    [0, 0, 0, 1],
                ]
            Tz = [  [np.cos(rotZ), np.sin(rotZ), 0, 0],
                    [-np.sin(rotZ), np.cos(rotZ), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ]
            for p in obj.points:
                P = (p.x, p.y, p.z, 1)
                R = np.matmul(P, Tx)
                R = np.matmul(R, Ty)
                (X, Y, Z, _) = np.matmul(R, Tz)
                p.x = X
                p.y = Y 
                p.z = Z

        if toObject:
            self.translation3D(obj, initial_center[0], initial_center[1], initial_center[2])
        elif toPoint:
            self.translation3D(obj, int(pX), int(pY), int(pZ))

    def zoomViewportIn(self):
        if self.cgWindow.xMax - 10 > self.cgWindow.xMin + 10 and self.cgWindow.yMax - 10 > self.cgWindow.yMin + 10:
            self.cgWindow.xMax -= 10
            self.cgWindow.xMin += 10
            self.cgWindow.yMax -= 10
            self.cgWindow.yMin += 10
            self.makePPCmatrix()
            self.applyPPCmatrixWindow()
            self.drawAll()

    def zoomViewportOut(self):
        self.cgWindow.xMax += 10
        self.cgWindow.xMin -= 10
        self.cgWindow.yMax += 10
        self.cgWindow.yMin -= 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()

    def panRight(self):
        v = [1, 0]
        ang = np.deg2rad(self.windowAngle)
        x = np.cos(ang)*v[0] - np.sin(ang)*v[1]
        y = np.sin(ang)*v[0] + np.cos(ang)*v[1]
        self.cgWindow.xMax += x * 10
        self.cgWindow.xMin += x * 10
        self.cgWindow.yMax += y * 10
        self.cgWindow.yMin += y * 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()

    def panLeft(self):
        v = [-1, 0]
        ang = np.deg2rad(self.windowAngle)
        x = np.cos(ang)*v[0] - np.sin(ang)*v[1]
        y = np.sin(ang)*v[0] + np.cos(ang)*v[1]
        self.cgWindow.xMax += x * 10
        self.cgWindow.xMin += x * 10
        self.cgWindow.yMax += y * 10
        self.cgWindow.yMin += y * 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()
    
    def panUp(self):
        v = [0, 1]
        ang = np.deg2rad(self.windowAngle)
        x = np.cos(ang)*v[0] - np.sin(ang)*v[1]
        y = np.sin(ang)*v[0] + np.cos(ang)*v[1]
        self.cgWindow.xMax += x * 10
        self.cgWindow.xMin += x * 10
        self.cgWindow.yMax += y * 10
        self.cgWindow.yMin += y * 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()

    def panDown(self):
        v = [0, -1]
        ang = np.deg2rad(self.windowAngle)
        x = np.cos(ang)*v[0] - np.sin(ang)*v[1]
        y = np.sin(ang)*v[0] + np.cos(ang)*v[1]
        self.cgWindow.xMax += x * 10
        self.cgWindow.xMin += x * 10
        self.cgWindow.yMax += y * 10
        self.cgWindow.yMin += y * 10
        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
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
        
        self.windowAngle = [0, 0, 0]

        self.makePPCmatrix()
        self.applyPPCmatrixWindow()
        self.drawAll()
    
    def loadObjs(self):
        newObjs = self.descObj.load("teste.obj")
        for obj in newObjs:
            self.displayFile.append(obj)
            self.objectList.addItem(obj.name)
        self.drawAll()
    
    def perspChange(self):
        self.perspd = self.perspSlider.value()
        self.drawAll()
    