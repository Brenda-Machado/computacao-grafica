"""
INE5420 - 2024/2
Brenda Silva Machado - 21101954

"""

from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
    name: str = ""
    color: tuple = (0,0,0)
    cn_x: int = 0
    cn_y: int = 0
    type: str = "Point"

@dataclass
class Line:
    p1: Point
    p2: Point
    name: str = ""
    color: tuple = (0,0,0)
    type: str = "Line"

@dataclass
class Wireframe:
    points: list[Point]
    name: str = ""
    color: tuple = (0,0,0)
    type: str = "Polygon"
    filled = False

@dataclass
class Curve2D:
    points: list[Point]
    name: str = ""
    color: tuple = (0,0,0)
    type: str = "Curve"
    filled = False

@dataclass
class BSplineCurve:
    points: list[Point]
    name: str = ""
    color: tuple = (0, 0, 0)
    type: str = "Curve"
    filled = False

@dataclass
class Point3D:
    x: int
    y: int
    z: int
    name: str = ""
    color: tuple = (0,0,0)
    cn_x: int = 0
    cn_y: int = 0
    cn_z: int = 0
    type: str = "Point3D"
    dimension: int = 3
    
@dataclass
class Object3D:
    points: list[Point]
    edges: list[int]
    name: str = ""
    color: tuple = (0,0,0)
    type: str = "Object3D"
    dimension: int = 3