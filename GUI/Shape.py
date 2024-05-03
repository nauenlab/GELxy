
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)).split("/GUI")[0])
from Shapes import Rectangle, Square, EquilateralTriangle, Triangle, Line, Oval, Circle, SineWave, Gradient, EdgeDetection, Texture
import enum


class Shape(enum.Enum):
    [Line, Rectangle, Square, Triangle, EquilateralTriangle, Circle, Oval, SineWave, Gradient, CustomShape, Texture] = [Line.Line, Rectangle.Rectangle, Square.Square, Triangle.Triangle, EquilateralTriangle.EquilateralTriangle, Circle.Circle, Oval.Oval, SineWave.SineWave, Gradient.Gradient, EdgeDetection.EdgeDetection, Texture.Texture]