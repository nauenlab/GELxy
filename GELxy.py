from tkinter.simpledialog import askfloat
from tkinter.filedialog import askopenfile
from tkinter import *
from tkinter import ttk
import enum
import re
from Shapes import Rectangle, Square, EquilateralTriangle, Triangle, Line, Oval, Circle, SineWave, Gradient, EdgeDetection, Texture
from Coordinate import Coordinate


class Shape(enum.Enum):
    [Line, Rectangle, Square, Triangle, EquilateralTriangle, Circle, Oval, SineWave, Gradient, CustomShape, Texture] = [Line.Line, Rectangle.Rectangle, Square.Square, Triangle.Triangle, EquilateralTriangle.EquilateralTriangle, Circle.Circle, Oval.Oval, SineWave.SineWave, Gradient.Gradient, EdgeDetection.EdgeDetection, Texture.Texture]


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("GELxy GUI")
        self.geometry("800x600")
        self.frame = Frame(self)
        self.frame.pack()
        welcome_label = Label(self, text="Welcome to the GELxy GUI", font=("Arial", 25))
        subtitle_label = Label(self, text="You can model and create patterns on the hyaluronic acid gel from here", font=("Arial", 15))
        welcome_label.pack()
        subtitle_label.pack()
        
        self.create_canvas()

        # points = [(100, 100), (200, 200), (300, 100), (200, 50)]
        # self.draw_coordinates(points)
        

        self.create_options()
        # draggable_object = self.DraggableObject(self.canvas, Shape.Rectangle, 5, 5)
        # draggable_object = self.DraggableObject(self.canvas, Shape.Circle, 5, 5)
        draggable_object = self.DraggableObject(self.canvas, Shape.CustomShape, 5, 5)
        # draggable_object = self.DraggableObject(self.canvas, Shape.Triangle, 5, 5)
        # draggable_object = self.DraggableObject(self.canvas, Shape.Line, 5, 5)
        

    def create_canvas(self):
        self.canvas = Canvas(self, width=400, height=400)
        self.canvas.create_line(30, 400, 30, 0, arrow=LAST)  # y-axis
        self.canvas.create_line(0, 370, 400, 370, arrow=LAST)  # x-axis
        for i in range(1, 26):
            x = 30 + i * 13
            y = 370 - i * 13
            self.canvas.create_text(x, 390, text=str(i), font=("Arial", 10))
            self.canvas.create_line(x, 370, x, 380)
            self.canvas.create_text(10, y, text=str(i), font=("Arial", 10))
            self.canvas.create_line(20, y, 30, y)
            
        self.canvas.pack()

    def create_options(self):
        label = Label(self, text="Beam Diameter")
        label.pack()
        entry = Entry(self, width=10)
        entry.pack()
        Combo = ttk.Combobox(self.frame, values=[re.sub('(?<=.)(?=[A-Z][a-z])', r" ", i.name).split() for i in Shape], state='readonly')
        Combo.set("Pick a Shape")
        Combo.pack()
        
    
    def add_file_button(self):
        B = Button(self, text="Import Drawing", command=self.get_file)
        B.pack()
    
    def get_file(self):
        filename = askopenfile()

    def draw_coordinates(self, coordinates):
        for i in range(len(coordinates)-1):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[i+1]
            self.canvas.create_line(x1, y1, x2, y2)
      
    class DraggableObject:
        def __init__(self, canvas, shape, x, y):
            self.canvas = canvas
            self.shape = shape
            self.x = x
            self.y = y
            self.drag_data = {"x": 0, "y": 0, "item": None}
            self.create_object()

        def create_object(self):
            sp = None
            if self.shape == Shape.Line:
                sp = self.shape.value(length_mm=5, stiffness=1, center=Coordinate(self.x, self.y), rotation_angle=None, beam_diameter=1, is_horizontal=False, uses_step_coordinates=False)
            elif self.shape == Shape.Rectangle:
                sp = self.shape.value(width_mm=5, height_mm=5, stiffness=20, center=Coordinate(self.x, self.y), rotation_angle=None, beam_diameter=1, uses_step_coordinates=False, filled=False)
            elif self.shape == Shape.Square:
                sp = self.shape.value(side_length_mm=5, stiffness=20, center=Coordinate(self.x, self.y), rotation_angle=None, beam_diameter=1, uses_step_coordinates=False, filled=False)
            elif self.shape == Shape.Triangle:
                sp = self.shape.value(width_mm=5, height_mm=5, stiffness=20, center=Coordinate(self.x, self.y), rotation_angle=None, beam_diameter=1, uses_step_coordinates=False, filled=False)
            elif self.shape == Shape.EquilateralTriangle:
                sp = self.shape.value(side_length_mm=5, stiffness=20, center=Coordinate(self.x, self.y), rotation_angle=None, beam_diameter=1, uses_step_coordinates=False, filled=False)
            elif self.shape == Shape.Circle:
                sp = self.shape.value(diameter_mm=5, stiffness=20, center=Coordinate(self.x, self.y), beam_diameter=1, filled=False)
            elif self.shape == Shape.Oval:
                sp = self.shape.value(width_mm=5, height_mm=5, stiffness=20, center=Coordinate(self.x, self.y), rotation_angle=None, beam_diameter=1)
            elif self.shape == Shape.SineWave:
                sp = self.shape.value(amplitude_mm=5, cycles=5, cycles_per_mm=0.5, stiffness=20, cycle_offset=0, center=Coordinate(self.x, self.y), rotation_angle=None, beam_diameter=1)
            elif self.shape == Shape.Gradient:
                sp = self.shape.value(min_velocity=0.1, max_velocity=1.5, beam_diameter=1, is_horizontal=False, is_reversed=True)
            elif self.shape == Shape.CustomShape:
                sp = self.shape.value(img_file="test_images/2.jpg", stiffness=20, center=Coordinate(self.x, self.y), rotation_angle=0, scale_factor=1, beam_diameter=0.1)
            elif self.shape == Shape.Texture:
                sp = self.shape.value(shape=Shape.Circle.value(diameter_mm=1, stiffness=20, center=Coordinate(0, 0), beam_diameter=1, filled=False), spacing_mm=2, margins=1)
            
            self.drag_data["item"] = self.canvas.create_polygon(self.format_xy_coordinates(sp.get_coordinates()))

            self.canvas.tag_bind(self.drag_data["item"], "<ButtonPress-1>", self.on_button_press)
            self.canvas.tag_bind(self.drag_data["item"], "<B1-Motion>", self.on_move)
            self.canvas.tag_bind(self.drag_data["item"], "<ButtonRelease-1>", self.on_button_release)

        def on_button_press(self, event):
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

        def on_move(self, event):
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.drag_data["item"], dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

        def on_button_release(self, event):
            pass

        def format_xy_coordinates(self, coordinates):
            return [(30 + i.x * 13, 370 - i.y * 13) for i in coordinates if i.lp]


app = App()
app.mainloop()