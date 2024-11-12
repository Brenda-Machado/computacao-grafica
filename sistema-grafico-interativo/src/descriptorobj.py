"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

import pathlib
from object import Point3D, Object3D

class DescriptorOBJ:
    def __init__(self):
        pass

    def load(self, file_path):
        sequence = self.parseObj(file_path)
        return self.processObjects(sequence)

    def parseObj(self, file_path):
        path = str(pathlib.Path().absolute() / "obj" / file_path)
        sequence = []
        with open(path) as file:
            for line in file.readlines():
                split = line.split()
                try:
                    type = split[0]
                    args = split[1:]
                    sequence.append((type, args))
                except IndexError:
                    pass
        return sequence
    
    def parseMtl(self, file_path):
        sequence = []
        with open(file_path) as file:
            for line in file.readlines():
                split = line.split()
                try:
                    type = split[0]
                    args = split[1:]
                    sequence.append((type, args))
                except IndexError:
                    pass
        
        colors = {}
        currentMtl = ""
        for e in sequence:
            if e[0] == "newmtl":
                colors[e[1][0]] = None
                currentMtl = e[1][0]
            elif e[0] == "Kd":
                r, g, b = e[1]
                r = round(float(r) * 255)
                g = round(float(g) * 255)
                b = round(float(b) * 255)
                colors[currentMtl] = (r,g,b)
        return colors

    def processObjects(self, sequence):
        verts = []
        objIndex = -1
        preobjects = []
        colors = None

        for e in sequence:
            if e[0] == "v":
                (x, y, z) = e[1]
                newVert = Point3D(int(float(x)), int(float(y)), int(float(z)))
                verts.append(newVert)
            
            elif e[0] == "o":
                objIndex += 1
                newObj = PreObject(e[1])
                newObj.name = newObj.name[0]
                preobjects.append(newObj)
                print(newObj.name)

            elif e[0] == "usemtl":
               cor = colors[e[1][0]]
               preobjects[objIndex].color = cor

            elif e[0] == "mtlib":
                file = e[1][0]
                file_path = str(pathlib.Path().absolute() / "obj" / file)
                colors = self.parseMtl(file_path)
                print(colors)

            elif e[0] == "p":
                index = int(e[1][0])
                newPoint = verts[index-1]
                newPoint.color = preobjects[objIndex].color
                preobjects[objIndex].points.append(newPoint)
                preobjects[objIndex].edges.append((len(preobjects[objIndex].points)-1, len(preobjects[objIndex].points)-1))

            elif e[0] == "l":
                points = e[1]
                p1 = verts[int(points[0])-1]
                p2 = verts[int(points[1])-1]
                points = [p1, p2]
                preobjects[objIndex].points.append(p1)
                preobjects[objIndex].points.append(p2)
                preobjects[objIndex].edges.append((len(preobjects[objIndex].points)-2, len(preobjects[objIndex].points)-1))

            elif e[0] == "f":
                print(e[1])
                points = e[1]
                pointList = []
                listIndex = len(preobjects[objIndex].points)
                for p in points:
                    realPoint = verts[int(p)-1]
                    pointList.append(realPoint)
                    preobjects[objIndex].points.append(realPoint)
                for i in range(listIndex + 1, listIndex + len(pointList)):
                    preobjects[objIndex].edges.append((i - 1, i))
                preobjects[objIndex].edges.append((listIndex + len(pointList) - 1, listIndex))
                

            else:
                print("Error: command not recognized")
        
        objects = []
        for pre in preobjects:
            realObj = Object3D(pre.points, pre.edges, pre.name, pre.color)
            objects.append(realObj)
            print(pre.color)
            
        return objects


