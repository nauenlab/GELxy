from tkinter.filedialog import askopenfile
from tkinter import *
from tkinter import ttk
import enum
import re
from Shapes import Rectangle, Square, EquilateralTriangle, Triangle, Line, Oval, Circle, SineWave, Gradient, EdgeDetection, Texture
from Coordinate import Coordinate
import math


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
        self.create_options()
        
    def create_canvas(self):
        self.canvas = Canvas(self, width=400, height=400, highlightthickness=0)
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
        entry.bind("<KeyPress>", self.allow_only_decimal)
        entry.pack()

        dimensions_label = Label(option_frame, text="Dimensions")
        dimensions_label.pack()

        self.add_height_width_entry(option_frame)

        center_label = Label(option_frame, text="Center")
        center_label.pack()

        self.add_coordinate_entry(option_frame)

        rotation_label = Label(option_frame, text="Rotation Angle:")
        rotation_label.pack()

        self.add_rotation_entry(option_frame)

        fill_var = BooleanVar()
        fill_checkbutton = Checkbutton(option_frame, text="Fill Shape", variable=fill_var)
        fill_checkbutton.pack()

    def add_height_width_entry(self, option_frame):
        height_width_frame = Frame(option_frame)
        height_width_frame.pack()

        height_label = Label(height_width_frame, text="Height:")
        height_label.pack(side=LEFT)

        height_entry = Entry(height_width_frame, width=5)
        height_entry.bind("<KeyPress>", self.allow_only_decimal)
        height_entry.pack(side=LEFT)

        width_label = Label(height_width_frame, text="Width:")
        width_label.pack(side=LEFT)

        width_entry = Entry(height_width_frame, width=5)
        width_entry.bind("<KeyPress>", self.allow_only_decimal)
        width_entry.pack(side=LEFT)
        
    def add_coordinate_entry(self, option_frame):
        center_frame = Frame(option_frame)
        center_frame.pack()

        x_label = Label(center_frame, text="X:")
        x_label.pack(side=LEFT)

        x_entry = Entry(center_frame, width=5)
        x_entry.bind("<KeyPress>", self.allow_only_decimal)
        x_entry.pack(side=LEFT)

        y_label = Label(center_frame, text="Y:")
        y_label.pack(side=LEFT)

        y_entry = Entry(center_frame, width=5)
        y_entry.bind("<KeyPress>", self.allow_only_decimal)
        y_entry.pack(side=LEFT)

    def add_rotation_entry(self, option_frame):
        rotation_frame = Frame(option_frame)
        rotation_frame.pack()

        rotation_entry = Entry(rotation_frame, width=5)
        rotation_entry.bind("<KeyPress>", self.allow_only_decimal)
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
            draggable_object = self.DraggableObject(self.canvas, Shape.Line, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1)
        elif selected_shape == "Rectangle":
            draggable_object = self.DraggableObject(self.canvas, Shape.Rectangle, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1)
        elif selected_shape == "Square":
            draggable_object = self.DraggableObject(self.canvas, Shape.Square, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1)
        elif selected_shape == "Triangle":
            draggable_object = self.DraggableObject(self.canvas, Shape.Triangle, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1)
        elif selected_shape == "Equilateral Triangle":
            draggable_object = self.DraggableObject(self.canvas, Shape.EquilateralTriangle, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1)
        elif selected_shape == "Circle":
            draggable_object = self.DraggableObject(self.canvas, Shape.Circle, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1)
        elif selected_shape == "Oval":
            draggable_object = self.DraggableObject(self.canvas, Shape.Oval, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1)
        elif selected_shape == "Sine Wave":
            draggable_object = self.DraggableObject(self.canvas, Shape.SineWave, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1, amplitude=1, cycles=5, cycles_per_mm=0.5)
        elif selected_shape == "Gradient":
            draggable_object = self.DraggableObject(self.canvas, Shape.Gradient, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1)
        elif selected_shape == "Custom Shape":
            draggable_object = self.DraggableObject(self.canvas, Shape.CustomShape, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1, img_file=self.custom_shape_file_name, scale_factor=1)
        elif selected_shape == "Texture":
            draggable_object = self.DraggableObject(self.canvas, Shape.Texture, x=5, y=5, rotation_angle=0, stiffness=1, beam_diameter=1, shape=Circle.Circle(diameter_mm=1, center=Coordinate(0, 0), beam_diameter=0.1, filled=False), spacing_mm=2, margins=1)

        popup.destroy()
    
    def get_file(self, selected_file_label):
        self.custom_shape_file_name = askopenfile(filetypes=[("Image Files", "*.png *.jpg *.jpeg")]).name
        selected_file_label.config(text=self.custom_shape_file_name.split("/")[-1])

    def draw_coordinates(self, coordinates):
        for i in range(len(coordinates)-1):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[i+1]
            self.canvas.create_line(x1, y1, x2, y2)

    def allow_only_decimal(self, event):
        # Get the current content of the entry widget
        current_text = self.focus_get().get()
        
        # Attempt to reconstruct the text only with valid decimal characters
        if event.char.isdigit() or (event.char == '.' and '.' not in current_text) or event.keysym == "BackSpace" or event.keysym == "Delete" or \
            event.keysym == "Left" or event.keysym == "Right" or event.keysym == "Shift_L" or event.keysym == "Shift_R" or event.keysym == "Control_L" or \
            event.keysym == "Control_R" or event.keysym == "Return" or ((event.state == 4 or event.state == 8) and event.keysym in ('c', 'x', 'v', 'a')):
            # Allow the event if it's a digit or a single '.'
            if len(event.char) > 0 and len(current_text) >= 10:
                return "break"
            return
        else:
            # Prevent the insertion of invalid characters
            return "break"


    class DraggableObject:
        def __init__(self, canvas, shape, **kwargs):
            self.canvas = canvas
            self.selected = False
            self.handle_size = 4
            self.handles = []
            self.metadata = App.ObjectMetadata(shape, **kwargs)
            self.rotation_angle = self.metadata.rotation_angle

            self.create_object()

            self.current_handle = None

        @property
        def resizing(self):
            self.current_handle = self.canvas.find_withtag(CURRENT)[0]
            return f"handle_{self.item}" in self.canvas.gettags(CURRENT)
        
        @property
        def rotating(self):
            self.current_handle = self.canvas.find_withtag(CURRENT)[0]
            return f"rotate_handle_{self.item}" in self.canvas.gettags(CURRENT)

        def create_object(self):
            # Create the shape based on type and additional parameters
            sp = None
            if self.metadata.shape == Shape.Line:
                sp = self.metadata.shape.value(length_mm=5, stiffness=self.metadata.stiffness, center=Coordinate(self.metadata.x, self.metadata.y), rotation_angle=self.metadata.rotation_angle, beam_diameter=self.metadata.beam_diameter, is_horizontal=False, uses_step_coordinates=True)
            elif self.metadata.shape == Shape.Rectangle:
                sp = self.metadata.shape.value(width_mm=5, height_mm=7, stiffness=self.metadata.stiffness, center=Coordinate(self.metadata.x, self.metadata.y), rotation_angle=self.metadata.rotation_angle, beam_diameter=self.metadata.beam_diameter, uses_step_coordinates=True, filled=False)
            elif self.metadata.shape == Shape.Square:
                sp = self.metadata.shape.value(side_length_mm=5, stiffness=self.metadata.stiffness, center=Coordinate(self.metadata.x, self.metadata.y), rotation_angle=self.metadata.rotation_angle, beam_diameter=self.metadata.beam_diameter, uses_step_coordinates=True, filled=False)
            elif self.metadata.shape == Shape.Triangle:
                sp = self.metadata.shape.value(width_mm=5, height_mm=7, stiffness=self.metadata.stiffness, center=Coordinate(self.metadata.x, self.metadata.y), rotation_angle=self.metadata.rotation_angle, beam_diameter=self.metadata.beam_diameter, uses_step_coordinates=True, filled=False)
            elif self.metadata.shape == Shape.EquilateralTriangle:
                sp = self.metadata.shape.value(side_length_mm=5, stiffness=self.metadata.stiffness, center=Coordinate(self.metadata.x, self.metadata.y), rotation_angle=self.metadata.rotation_angle, beam_diameter=self.metadata.beam_diameter, uses_step_coordinates=True, filled=False)
            elif self.metadata.shape == Shape.Circle:
                sp = self.metadata.shape.value(diameter_mm=5, stiffness=self.metadata.stiffness, center=Coordinate(self.metadata.x, self.metadata.y), beam_diameter=self.metadata.beam_diameter, filled=False)
            elif self.metadata.shape == Shape.Oval:
                sp = self.metadata.shape.value(width_mm=5, height_mm=10, stiffness=self.metadata.stiffness, center=Coordinate(self.metadata.x, self.metadata.y), rotation_angle=self.metadata.rotation_angle, beam_diameter=self.metadata.beam_diameter)
            elif self.metadata.shape == Shape.SineWave:
                sp = self.metadata.shape.value(amplitude_mm=self.metadata.amplitude, cycles=self.metadata.cycles, cycles_per_mm=self.metadata.cycles_per_mm, stiffness=self.metadata.stiffness, rotation_angle=self.metadata.rotation_angle, center=Coordinate(self.metadata.x, self.metadata.y), beam_diameter=self.metadata.beam_diameter)
            elif self.metadata.shape == Shape.Gradient:
                sp = self.metadata.shape.value(min_velocity=0.1, max_velocity=1.5, stiffness=self.metadata.stiffness, rotation_angle=self.metadata.rotation_angle, beam_diameter=self.metadata.beam_diameter, is_horizontal=False, is_reversed=True)
            elif self.metadata.shape == Shape.CustomShape:
                sp = self.metadata.shape.value(img_file=self.img_file, stiffness=self.metadata.stiffness, center=Coordinate(self.metadata.x, self.metadata.y), rotation_angle=self.metadata.rotation_angle, scale_factor=self.scale_factor, beam_diameter=self.metadata.beam_diameter)
            elif self.metadata.shape == Shape.Texture:
                sp = self.metadata.shape.value(shape=self.metadata.texture_shape, spacing_mm=self.metadata.spacing, margins=self.metadata.margins)
            
            self.item = self.canvas.create_line(self.format_xy_coordinates(sp.get_coordinates()))
            # Bind events
            self.canvas.tag_bind(self.item, "<ButtonPress-1>", self.on_button_press)
            self.canvas.tag_bind(self.item, "<B1-Motion>", self.on_move)
            self.canvas.tag_bind(self.item, "<ButtonRelease-1>", self.on_button_release)
            self.canvas.bind("<BackSpace>", self.delete_object)


        def on_button_press(self, event):
            self.drag_data = {"x": event.x, "y": event.y}
            if not self.resizing:
                self.select_object()
                self.current_handle = None
            self.canvas.focus_set()

        def delete_object(self, event):
            if self.selected:
                self.canvas.delete(self.item)
                self.selected = False
                self.handles = []

        def on_move(self, event):
            if not self.selected:
                return
            if self.resizing and self.current_handle:
                self.resize(event)
            elif self.rotating and self.current_handle:
                self.rotate(event)
            else:
                dx = event.x - self.drag_data["x"]
                dy = event.y - self.drag_data["y"]
                new_coords = [coord + (dx if i % 2 == 0 else dy) for i, coord in enumerate(self.canvas.coords(self.item))]
                self.canvas.coords(self.item, *new_coords)
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                # self.update_handles()
                for handle in self.handles:
                    handle_coords = self.canvas.coords(handle)
                    new_handle_coords = [coord + (dx if i % 2 == 0 else dy) for i, coord in enumerate(handle_coords)]
                    self.canvas.coords(handle, *new_handle_coords)

        def on_button_release(self, event):
            self.drag_data = None
            self.current_handle = None
            self.drag_data = None

        def show_handles(self):
            bbox = self.canvas.bbox(self.item)
            cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
            
            self.handles = [
                self.canvas.create_polygon(bbox[0] - self.handle_size, bbox[1] - self.handle_size, bbox[0] + self.handle_size, bbox[1] - self.handle_size, bbox[0] + self.handle_size, bbox[1] + self.handle_size, bbox[0] - self.handle_size, bbox[1] + self.handle_size, fill="blue", tags=f"handle_{self.item}"), # top_left
                self.canvas.create_polygon(cx - self.handle_size, bbox[1] - self.handle_size, cx + self.handle_size, bbox[1] - self.handle_size, cx + self.handle_size, bbox[1] + self.handle_size, cx - self.handle_size, bbox[1] + self.handle_size, fill="blue", tags=f"handle_{self.item}"),  # top_middle
                self.canvas.create_polygon(bbox[2] - self.handle_size, bbox[1] - self.handle_size, bbox[2] + self.handle_size, bbox[1] - self.handle_size, bbox[2] + self.handle_size, bbox[1] + self.handle_size, bbox[2] - self.handle_size, bbox[1] + self.handle_size, fill="blue", tags=f"handle_{self.item}"),  # top_right
                self.canvas.create_polygon(bbox[0] - self.handle_size, cy - self.handle_size, bbox[0] + self.handle_size, cy - self.handle_size, bbox[0] + self.handle_size, cy + self.handle_size, bbox[0] - self.handle_size, cy + self.handle_size, fill="blue", tags=f"handle_{self.item}"),  # middle_left
                self.canvas.create_polygon(bbox[2] - self.handle_size, cy - self.handle_size, bbox[2] + self.handle_size, cy - self.handle_size, bbox[2] + self.handle_size, cy + self.handle_size, bbox[2] - self.handle_size, cy + self.handle_size, fill="blue", tags=f"handle_{self.item}"),  # middle_right
                self.canvas.create_polygon(bbox[0] - self.handle_size, bbox[3] - self.handle_size, bbox[0] + self.handle_size, bbox[3] - self.handle_size, bbox[0] + self.handle_size, bbox[3] + self.handle_size, bbox[0] - self.handle_size, bbox[3] + self.handle_size, fill="blue", tags=f"handle_{self.item}"),  # bottom_left
                self.canvas.create_polygon(cx - self.handle_size, bbox[3] - self.handle_size, cx + self.handle_size, bbox[3] - self.handle_size, cx + self.handle_size, bbox[3] + self.handle_size, cx - self.handle_size, bbox[3] + self.handle_size, fill="blue", tags=f"handle_{self.item}"),  # bottom_middle
                self.canvas.create_polygon(bbox[2] - self.handle_size, bbox[3] - self.handle_size, bbox[2] + self.handle_size, bbox[3] - self.handle_size, bbox[2] + self.handle_size, bbox[3] + self.handle_size, bbox[2] - self.handle_size, bbox[3] + self.handle_size, fill="blue", tags=f"handle_{self.item}"),  # bottom_right
                self.canvas.create_polygon(cx - self.handle_size, bbox[1] - 4*self.handle_size, cx + self.handle_size, bbox[1] - 4*self.handle_size, cx + self.handle_size, bbox[1] - 2*self.handle_size, cx - self.handle_size, bbox[1] - 2*self.handle_size, fill="blue", tags=f"rotate_handle_{self.item}"),  # rotation_handle
            ]

            for handle in self.handles:
                self.canvas.tag_bind(handle, "<ButtonPress-1>", self.on_button_press)
                self.canvas.tag_bind(handle, "<B1-Motion>", self.on_move)
                

        def delete_object(self, event):
            if self.selected:
                self.hide_handles()
                self.canvas.delete(self.item)

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

            # Apply scaling to each coordinate
            new_coords = []
            origin_coords = self.canvas.coords(self.item)
            for i in range(0, len(origin_coords), 2):
                new_x = fixed_x + (origin_coords[i] - fixed_x) * scale_x
                new_y = fixed_y + (origin_coords[i+1] - fixed_y) * scale_y
                new_coords.extend([new_x, new_y])

            self.canvas.coords(self.item, *new_coords)
            self.update_handles()

            # Moves the handles, using a similar approach
            # for handle in self.handles:
            #     handle_coords = self.canvas.coords(handle)
            #     new_handle_coords = []
            #     for i in range(0, len(handle_coords), 2):
            #         hx, hy = handle_coords[i], handle_coords[i+1]
            #         new_hx = fixed_x + (hx - fixed_x) * scale_x
            #         new_hy = fixed_y + (hy - fixed_y) * scale_y
            #         new_handle_coords.extend([new_hx, new_hy])
            
            # for handle in self.handles:
            #     handle_coords = self.canvas.coords(handle)
            #     new_handle_coords = []
            #     for i in range(0, len(handle_coords), 2):
            #         hx, hy = handle_coords[i], handle_coords[i+1]
            #         new_hx = fixed_x + (hx - fixed_x) * scale_x
            #         new_hy = fixed_y + (hy - fixed_y) * scale_y
            #         new_handle_coords.extend([new_hx, new_hy])
                    
                
            #     self.canvas.coords(handle, *new_handle_coords)
            
            # rotate_handle = self.handles[-1]
            # rotate_handle_coords = self.canvas.coords(rotate_handle)
            # new_rotate_handle_coords = [rotate_handle_coords[0], fixed_y - 4*self.handle_size, rotate_handle_coords[2], fixed_y - 2*self.handle_size]
            # self.canvas.coords(rotate_handle, new_rotate_handle_coords)

        def rotate(self, event):
            if not self.rotating or not self.current_handle:
                return

            # Calculate the center of the shape (rotation pivot point)
            bbox = self.canvas.bbox(self.item)
            cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2

            # Determine initial and current angles to calculate the rotation angle
            origin_x, origin_y = self.canvas.coords(self.current_handle)[:2]  # Using the handle's initial position
            initial_angle = math.atan2(origin_y - cy, origin_x - cx)
            self.rotation_angle = math.atan2(event.y - cy, event.x - cx)
            angle = self.rotation_angle - initial_angle
            print(self.rotation_angle*10)

            # Rotate the shape
            new_coords = []
            origin_coords = self.canvas.coords(self.item)
            for i in range(0, len(origin_coords), 2):
                x, y = origin_coords[i], origin_coords[i+1]
                new_x = cx + (x - cx) * math.cos(angle) - (y - cy) * math.sin(angle)
                new_y = cy + (x - cx) * math.sin(angle) + (y - cy) * math.cos(angle)
                new_coords.extend([new_x, new_y])

            self.canvas.coords(self.item, *new_coords)

            # # Rotate the handles, using a similar approach
            # for handle in self.handles[:-1]:
            #     handle_coords = self.canvas.coords(handle)
            #     new_handle_coords = []
            #     # Assume each handle is a small square or point, and rotate its center
            #     for i in range(0, len(handle_coords), 2):
            #         hx, hy = handle_coords[i], handle_coords[i+1]
            #         new_hx = cx + (hx - cx) * math.cos(angle) - (hy - cy) * math.sin(angle)
            #         new_hy = cy + (hx - cx) * math.sin(angle) + (hy - cy) * math.cos(angle)
            #         new_handle_coords.extend([new_hx, new_hy])
                
            #     self.canvas.coords(handle, *new_handle_coords)

            # # Move, but don't rotate the rotation handle
            # rotate_handle = self.handles[-1]
            # rotate_handle_coords = self.canvas.coords(rotate_handle)
            # new_rotate_handle_coords = []
            # for i in range(0, len(rotate_handle_coords), 2):
            #     hx, hy = rotate_handle_coords[i], rotate_handle_coords[i+1]
            #     new_hx = cx + (hx - cx) - (hy - cy)
            #     new_hy = cy + (hx - cx) + (hy - cy)
            #     new_rotate_handle_coords.extend([new_hx, new_hy])
            
            # self.canvas.coords(rotate_handle, *new_rotate_handle_coords)


            # Optionally call update_handles if it performs additional necessary adjustments
            self.update_handles()
            
        def update_handles(self):
            bbox = self.canvas.bbox(self.item)
            corners_rotated = []
            for i in range(0, len(bbox), 2):
                x, y = bbox[i], bbox[i+1]
                new_x = x * math.cos(self.rotation_angle) - y * math.sin(self.rotation_angle)
                new_y = x * math.sin(self.rotation_angle) + y * math.cos(self.rotation_angle)
                corners_rotated.extend([new_x, new_y])
            
            cx, cy = (corners_rotated[0] + corners_rotated[2]) / 2, (corners_rotated[1] + corners_rotated[3]) / 2

            for i, handle in enumerate(self.handles):
                handle_center = []
                if i == 0:
                    handle_center = [corners_rotated[0], corners_rotated[1]]
                elif i == 1:
                    handle_center = [cx, corners_rotated[1]]
                elif i == 2:
                    handle_center = [corners_rotated[2], corners_rotated[1]]
                elif i == 3:
                    handle_center = [corners_rotated[0], cy]
                elif i == 4:
                    handle_center = [corners_rotated[2], cy]
                elif i == 5:
                    handle_center = [corners_rotated[0], corners_rotated[3]]
                elif i == 6:
                    handle_center = [cx, corners_rotated[3]]
                elif i == 7:
                    handle_center = [corners_rotated[2], corners_rotated[3]]
                elif i == 8:
                    handle_center = [cx, corners_rotated[1] - 4*self.handle_size]
                
                # x1, y1,...xn, yn
                new_handle_coordinates = [handle_center[0] - self.handle_size, handle_center[1] - self.handle_size, handle_center[0] + self.handle_size, handle_center[1] - self.handle_size, handle_center[0] + self.handle_size, handle_center[1] + self.handle_size, handle_center[0] - self.handle_size, handle_center[1] + self.handle_size]
                
                self.canvas.coords(handle, *new_handle_coordinates)
                
            
            


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
    

    class ObjectMetadata:
        def __init__(self, shape, **kwargs):
            self.shape = shape
            for key, value in kwargs.items():
                setattr(self, key, value)

        

app = App()
app.mainloop()