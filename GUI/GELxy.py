from tkinter.filedialog import askopenfile
from tkinter import *
from tkinter import ttk
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)).split("/GUI")[0])
from Coordinate import Coordinate
from DraggableObject import DraggableObject
from Shape import Shape, Circle


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
        
        required_defaults = {"x": 5, "y": 5, "rotation_angle": 0, "stiffness": 1, "beam_diameter": 0.1}
        if selected_shape == "Line":
            draggable_object = DraggableObject(self.canvas, Shape.Line, **required_defaults)
        elif selected_shape == "Rectangle":
            draggable_object = DraggableObject(self.canvas, Shape.Rectangle, **required_defaults)
        elif selected_shape == "Square":
            draggable_object = DraggableObject(self.canvas, Shape.Square, **required_defaults)
        elif selected_shape == "Triangle":
            draggable_object = DraggableObject(self.canvas, Shape.Triangle, **required_defaults)
        elif selected_shape == "Equilateral Triangle":
            draggable_object = DraggableObject(self.canvas, Shape.EquilateralTriangle, **required_defaults)
        elif selected_shape == "Circle":
            draggable_object = DraggableObject(self.canvas, Shape.Circle, **required_defaults)
        elif selected_shape == "Oval":
            draggable_object = DraggableObject(self.canvas, Shape.Oval, **required_defaults)
        elif selected_shape == "Sine Wave":
            draggable_object = DraggableObject(self.canvas, Shape.SineWave, **required_defaults, amplitude=1, cycles=5, cycles_per_mm=0.5)
        elif selected_shape == "Gradient":
            draggable_object = DraggableObject(self.canvas, Shape.Gradient, **required_defaults)
        elif selected_shape == "Custom Shape":
            draggable_object = DraggableObject(self.canvas, Shape.CustomShape, **required_defaults, img_file=self.custom_shape_file_name, scale_factor=1)
        elif selected_shape == "Texture":
            draggable_object = DraggableObject(self.canvas, Shape.Texture, **required_defaults, shape=Circle.Circle(diameter_mm=1, center=Coordinate(0, 0), beam_diameter=0.1, filled=False), spacing_mm=2, margins=1)

        popup.destroy()
    
    def get_file(self, selected_file_label):
        fileEvent = askopenfile(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if fileEvent:
            self.custom_shape_file_name = fileEvent.name
        
        if self.custom_shape_file_name:
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

        

app = App()
app.mainloop()