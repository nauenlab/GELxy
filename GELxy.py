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
        self.frame.pack(padx=20, pady=20, side=LEFT)
        self.frame.pack(side=LEFT)
        self.canvas.pack(side=LEFT)

        # points = [(100, 100), (200, 200), (300, 100), (200, 50)]
        # self.draw_coordinates(points)
        
        self.create_options()
        # draggable_object = self.DraggableObject(self.canvas, Shape.Rectangle, 5, 5)
        # draggable_object = self.DraggableObject(self.canvas, Shape.Circle, 5, 5)
        # draggable_object = self.DraggableObject(self.canvas, Shape.CustomShape, 5, 5)
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
        option_frame = Frame(self)
        option_frame.pack()

        buffer_view = Label(option_frame, height=5)
        buffer_view.pack()

        add_shape_button = Button(option_frame, text="Add Shape", command=lambda: self.create_add_shape_popup())
        add_shape_button.pack()
        
        buffer_view = Label(option_frame, height=5)
        buffer_view.pack()
        
        label = Label(option_frame, text="Beam Diameter")
        label.pack()
        
        entry = Entry(option_frame, width=10)
        entry.pack()

        center_label = Label(option_frame, text="Center")
        center_label.pack()

        self.add_coordinate_entry(option_frame)

        rotation_label = Label(option_frame, text="Rotation Angle:")
        rotation_label.pack()

        self.add_rotation_entry(option_frame)

        fill_var = BooleanVar()
        fill_checkbutton = Checkbutton(option_frame, text="Fill Shape", variable=fill_var)
        fill_checkbutton.pack()

        
    def add_coordinate_entry(self, option_frame):
        center_frame = Frame(option_frame)
        center_frame.pack()

        x_label = Label(center_frame, text="X:")
        x_label.pack(side=LEFT)

        x_entry = Entry(center_frame, width=5)
        x_entry.pack(side=LEFT)

        y_label = Label(center_frame, text="Y:")
        y_label.pack(side=LEFT)

        y_entry = Entry(center_frame, width=5)
        y_entry.pack(side=LEFT)

    def add_rotation_entry(self, option_frame):
        rotation_frame = Frame(option_frame)
        rotation_frame.pack()

        rotation_entry = Entry(rotation_frame, width=5)
        rotation_entry.pack(side=LEFT)

        degrees_label = Label(rotation_frame, text="degrees")
        degrees_label.pack(side=LEFT)
    

    def create_add_shape_popup(self):
        popup = Toplevel(self)
        popup.title("Add Shape")
        popup.geometry("400x300")

        Combo = ttk.Combobox(popup, values=[re.sub('(?<=.)(?=[A-Z][a-z])', r" ", i.name).split() for i in Shape], state='readonly')
        Combo.set("Pick a Shape")
        Combo.pack()

        add_button = Button(popup, text=f"Add", command=lambda: self.add_shape_to_canvas(Combo, popup))
        select_file_frame = Frame(popup)
        select_file_frame.pack()

        selected_file_label = Label(select_file_frame, text="No file selected")
        select_file_button = Button(select_file_frame, text="Select File", command=lambda: self.get_file(selected_file_label))
        def on_combo_select(event):
            selected_shape = Combo.get()
            add_button.config(text=f"Add {selected_shape}")
            select_file_button.pack_forget()
            selected_file_label.pack_forget()
            if selected_shape == "Gradient":
                pass
            elif selected_shape == "Custom Shape":
                select_file_button.pack()  
                selected_file_label.config(text="No file selected")
                selected_file_label.pack()      
                pass
            elif selected_shape == "Texture":
                pass

        Combo.bind("<<ComboboxSelected>>", on_combo_select)

        add_button.pack()

        popup.mainloop()

    def add_shape_to_canvas(self, Combo, popup):
        selected_shape = Combo.get()
        if selected_shape == "Pick a Shape":
            return
        
        if selected_shape == "Line":
            draggable_object = self.DraggableObject(self.canvas, Shape.Line, 5, 5, 0, 1)
        elif selected_shape == "Rectangle":
            draggable_object = self.DraggableObject(self.canvas, Shape.Rectangle, 5, 5, 0, 1)
        elif selected_shape == "Square":
            draggable_object = self.DraggableObject(self.canvas, Shape.Square, 5, 5, 0, 1)
        elif selected_shape == "Triangle":
            draggable_object = self.DraggableObject(self.canvas, Shape.Triangle, 5, 5, 0, 1)
        elif selected_shape == "Equilateral Triangle":
            draggable_object = self.DraggableObject(self.canvas, Shape.EquilateralTriangle, 5, 5, 0, 1)
        elif selected_shape == "Circle":
            draggable_object = self.DraggableObject(self.canvas, Shape.Circle, 5, 5, 0, 1)
        elif selected_shape == "Oval":
            draggable_object = self.DraggableObject(self.canvas, Shape.Oval, 5, 5, 0, 1)
        elif selected_shape == "Sine Wave":
            draggable_object = self.DraggableObject(self.canvas, Shape.SineWave, 5, 5, 0, 1, amplitude=1, cycles=5, cycles_per_mm=0.5)
        elif selected_shape == "Gradient":
            draggable_object = self.DraggableObject(self.canvas, Shape.Gradient, 5, 5, 0, 1)
        elif selected_shape == "Custom Shape":
            draggable_object = self.DraggableObject(self.canvas, Shape.CustomShape, 5, 5, 0, 1, img_file=self.custom_shape_file_name, scale_factor=1)
        elif selected_shape == "Texture":
            draggable_object = self.DraggableObject(self.canvas, Shape.Texture, 5, 5, 0, 1, shape=Circle.Circle(diameter_mm=1, center=Coordinate(0, 0), beam_diameter=0.1, filled=False), spacing_mm=2, margins=1)

        popup.destroy()
    
    def get_file(self, selected_file_label):
        self.custom_shape_file_name = askopenfile(filetypes=[("Image Files", "*.png *.jpg *.jpeg")]).name
        selected_file_label.config(text=self.custom_shape_file_name.split("/")[-1])

    def draw_coordinates(self, coordinates):
        for i in range(len(coordinates)-1):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[i+1]
            self.canvas.create_line(x1, y1, x2, y2)


    class DraggableObject:
        def __init__(self, canvas, shape, x, y, rotation_angle, stiffness, **kwargs):
            self.canvas = canvas
            self.shape = shape
            self.x = x
            self.y = y
            self.rotation_angle = rotation_angle
            self.stiffness = stiffness
            self.selected = False
            self.handle_size = 4
            self.handles = []

            if kwargs:
                for key, value in kwargs.items():
                    setattr(self, key, value)
            self.create_object()

            self.current_handle = None


        @property
        def resizing(self):
            self.current_handle = self.canvas.find_withtag(CURRENT)[0]
            return f"handle_{self.item}" in self.canvas.gettags(CURRENT)
        

        def create_object(self):
            # Create the shape based on type and additional parameters
            sp = None
            if self.shape == Shape.Line:
                sp = self.shape.value(length_mm=5, stiffness=self.stiffness, center=Coordinate(self.x, self.y), rotation_angle=self.rotation_angle, beam_diameter=1, is_horizontal=False, uses_step_coordinates=True)
            elif self.shape == Shape.Rectangle:
                sp = self.shape.value(width_mm=5, height_mm=5, stiffness=self.stiffness, center=Coordinate(self.x, self.y), rotation_angle=self.rotation_angle, beam_diameter=0.1, uses_step_coordinates=True, filled=False)
            elif self.shape == Shape.Square:
                sp = self.shape.value(side_length_mm=5, stiffness=self.stiffness, center=Coordinate(self.x, self.y), rotation_angle=self.rotation_angle, beam_diameter=1, uses_step_coordinates=True, filled=False)
            elif self.shape == Shape.Triangle:
                sp = self.shape.value(width_mm=5, height_mm=5, stiffness=self.stiffness, center=Coordinate(self.x, self.y), rotation_angle=self.rotation_angle, beam_diameter=1, uses_step_coordinates=True, filled=False)
            elif self.shape == Shape.EquilateralTriangle:
                sp = self.shape.value(side_length_mm=5, stiffness=self.stiffness, center=Coordinate(self.x, self.y), rotation_angle=self.rotation_angle, beam_diameter=1, uses_step_coordinates=True, filled=False)
            elif self.shape == Shape.Circle:
                sp = self.shape.value(diameter_mm=5, stiffness=self.stiffness, center=Coordinate(self.x, self.y), beam_diameter=1, filled=False)
            elif self.shape == Shape.Oval:
                sp = self.shape.value(width_mm=5, height_mm=5, stiffness=self.stiffness, center=Coordinate(self.x, self.y), rotation_angle=self.rotation_angle, beam_diameter=1)
            elif self.shape == Shape.SineWave:
                sp = self.shape.value(amplitude_mm=self.amplitude, cycles=self.cycles, cycles_per_mm=self.cycles_per_mm, stiffness=self.stiffness, rotation_angle=self.rotation_angle, center=Coordinate(self.x, self.y), beam_diameter=1)
            elif self.shape == Shape.Gradient:
                sp = self.shape.value(min_velocity=0.1, max_velocity=1.5, stiffness=self.stiffness, rotation_angle=self.rotation_angle, beam_diameter=1, is_horizontal=False, is_reversed=True)
            elif self.shape == Shape.CustomShape:
                sp = self.shape.value(img_file=self.img_file, stiffness=self.stiffness, center=Coordinate(self.x, self.y), rotation_angle=self.rotation_angle, scale_factor=self.scale_factor, beam_diameter=1)
            elif self.shape == Shape.Texture:
                sp = self.shape.value(shape=self.texture_shape, spacing_mm=self.spacing, margins=self.margins)
            
            self.item = self.canvas.create_polygon(self.format_xy_coordinates(sp.get_coordinates()))
            # Bind events
            self.canvas.tag_bind(self.item, "<ButtonPress-1>", self.on_button_press)
            self.canvas.tag_bind(self.item, "<B1-Motion>", self.on_move)
            self.canvas.tag_bind(self.item, "<ButtonRelease-1>", self.on_button_release)

        def on_button_press(self, event):
            self.drag_data = {"x": event.x, "y": event.y}
            if not self.resizing:
                self.select_object()
                self.current_handle = None

        def on_move(self, event):
            if not self.selected:
                return
            if self.resizing and self.current_handle:
                self.resize(event)
            else:
                dx = event.x - self.drag_data["x"]
                dy = event.y - self.drag_data["y"]
                new_coords = [coord + (dx if i % 2 == 0 else dy) for i, coord in enumerate(self.canvas.coords(self.item))]
                self.canvas.coords(self.item, *new_coords)
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                self.update_handles()

        def on_button_release(self, event):
            self.drag_data = None
            self.current_handle = None
            self.drag_data = None

        def show_handles(self):
            bbox = self.canvas.bbox(self.item)
            cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
            
            self.handles = [
                self.canvas.create_rectangle(bbox[0] - self.handle_size, bbox[1] - self.handle_size, bbox[0] + self.handle_size, bbox[1] + self.handle_size, outline="red", fill="blue", tags=f"handle_{self.item}"),  # top_left
                self.canvas.create_rectangle(cx - self.handle_size, bbox[1] - self.handle_size, cx + self.handle_size, bbox[1] + self.handle_size, outline="orange", fill="blue", tags=f"handle_{self.item}"),  # top_middle
                self.canvas.create_rectangle(bbox[2] - self.handle_size, bbox[1] - self.handle_size, bbox[2] + self.handle_size, bbox[1] + self.handle_size, outline="green", fill="blue", tags=f"handle_{self.item}"),  # top_right
                self.canvas.create_rectangle(bbox[0] - self.handle_size, cy - self.handle_size, bbox[0] + self.handle_size, cy + self.handle_size, outline="blue", fill="blue", tags=f"handle_{self.item}"),  # middle_left
                self.canvas.create_rectangle(bbox[2] - self.handle_size, cy - self.handle_size, bbox[2] + self.handle_size, cy + self.handle_size, outline="purple", fill="blue", tags=f"handle_{self.item}"),  # middle_right
                self.canvas.create_rectangle(bbox[0] - self.handle_size, bbox[3] - self.handle_size, bbox[0] + self.handle_size, bbox[3] + self.handle_size, outline="blue", fill="blue", tags=f"handle_{self.item}"),  # bottom_left
                self.canvas.create_rectangle(cx - self.handle_size, bbox[3] - self.handle_size, cx + self.handle_size, bbox[3] + self.handle_size, outline="blue", fill="blue", tags=f"handle_{self.item}"),  # bottom_middle
                self.canvas.create_rectangle(bbox[2] - self.handle_size, bbox[3] - self.handle_size, bbox[2] + self.handle_size, bbox[3] + self.handle_size, outline="blue", fill="blue", tags=f"handle_{self.item}")  # bottom_right
            ]
            for handle in self.handles:
                self.canvas.tag_bind(handle, "<ButtonPress-1>", self.on_button_press)
                self.canvas.tag_bind(handle, "<B1-Motion>", self.on_move)

        def hide_handles(self):
            for handle in self.handles:
                self.canvas.delete(handle)
            self.handles = []
        
        def resize(self, event):
            if not self.resizing or not self.current_handle:
                return

            # Get current bounding box of the item
            bbox = self.canvas.bbox(self.item)
            x0, y0, x1, y1 = bbox  # Coordinates of the bounding box corners
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2  # Center of the bounding box

            # Determine which handle is being used
            if self.current_handle == self.handles[0]:  # Top-left handle
                fixed_x, fixed_y = x1, y1 
                opposite_corner_x, opposite_corner_y = x0, y0
            elif self.current_handle == self.handles[1]:  # Top-middle handle handle
                fixed_x, fixed_y = cx, y1 
                opposite_corner_x, opposite_corner_y = cx, y0
            elif self.current_handle == self.handles[2]:  # Top-right handle
                fixed_x, fixed_y = x0, y1 
                opposite_corner_x, opposite_corner_y = x1, y0
            elif self.current_handle == self.handles[3]:  # Middle-left handle
                fixed_x, fixed_y = x1, cy
                opposite_corner_x, opposite_corner_y = x0, cy
            elif self.current_handle == self.handles[4]:  # Middle-right handle
                fixed_x, fixed_y = x0, cy 
                opposite_corner_x, opposite_corner_y = x1, cy
            elif self.current_handle == self.handles[5]:  # Bottom-left handle
                fixed_x, fixed_y = x1, y0
                opposite_corner_x, opposite_corner_y = x0, y1
            elif self.current_handle == self.handles[6]:  # Bottom-middle handle
                fixed_x, fixed_y = cx, y0
                opposite_corner_x, opposite_corner_y = cx, y1
            elif self.current_handle == self.handles[7]:  # Bottom-right handle
                fixed_x, fixed_y = x0, y0
                opposite_corner_x, opposite_corner_y = x1, y1

            # Calculate scaling factors based on the fixed point
            try:
                scale_x = (event.x - fixed_x) / (opposite_corner_x - fixed_x) if cx != fixed_x else 1
            except ZeroDivisionError:
                scale_x = 1  # Prevent division by zero if dragging directly over the fixed point

            try:
                scale_y = (event.y - fixed_y) / (opposite_corner_y - fixed_y) if cy != fixed_y else 1
            except ZeroDivisionError:
                scale_y = 1 

            print(scale_x, scale_y)

            # Apply scaling to each coordinate
            new_coords = []
            origin_coords = self.canvas.coords(self.item)
            for i in range(0, len(origin_coords), 2):
                new_x = fixed_x + (origin_coords[i] - fixed_x) * scale_x
                new_y = fixed_y + (origin_coords[i+1] - fixed_y) * scale_y
                new_coords.extend([new_x, new_y])

            self.canvas.coords(self.item, *new_coords)
            self.update_handles()


        def update_handles(self):
            bbox = self.canvas.bbox(self.item)
            cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
            self.canvas.coords(self.handles[0], bbox[0] - self.handle_size, bbox[1] - self.handle_size, bbox[0] + self.handle_size, bbox[1] + self.handle_size)  # top_left
            self.canvas.coords(self.handles[1], cx - self.handle_size, bbox[1] - self.handle_size, cx + self.handle_size, bbox[1] + self.handle_size)  # top_middle
            self.canvas.coords(self.handles[2], bbox[2] - self.handle_size, bbox[1] - self.handle_size, bbox[2] + self.handle_size, bbox[1] + self.handle_size)  # top_right
            self.canvas.coords(self.handles[3], bbox[0] - self.handle_size, cy - self.handle_size, bbox[0] + self.handle_size, cy + self.handle_size)  # middle_left
            self.canvas.coords(self.handles[4], bbox[2] - self.handle_size, cy - self.handle_size, bbox[2] + self.handle_size, cy + self.handle_size)  # middle_right
            self.canvas.coords(self.handles[5], bbox[0] - self.handle_size, bbox[3] - self.handle_size, bbox[0] + self.handle_size, bbox[3] + self.handle_size)  # bottom_left
            self.canvas.coords(self.handles[6], cx - self.handle_size, bbox[3] - self.handle_size, cx + self.handle_size, bbox[3] + self.handle_size)  # bottom_middle
            self.canvas.coords(self.handles[7], bbox[2] - self.handle_size, bbox[3] - self.handle_size, bbox[2] + self.handle_size, bbox[3] + self.handle_size)  # bottom_right


        def select_object(self):
            # self.selected = not self.selected
            
            if not self.selected:
                self.selected = True
                self.show_handles()

            # if self.selected:
            #     self.show_handles()
            # else:
                # self.hide_handles()
        
        def format_xy_coordinates(self, coordinates):
            return [(30 + i.x * 13, 370 - i.y * 13) for i in coordinates if i.lp]      


app = App()
app.mainloop()