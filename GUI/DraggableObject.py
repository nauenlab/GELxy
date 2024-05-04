from tkinter import *
import math
from Coordinate import Coordinate
from ObjectMetadata import ObjectMetadata
from Shape import Shape


class DraggableObject(Tk):
    def __init__(self, canvas, shape, **kwargs):
        self.canvas = canvas
        self.selected = False
        self.handle_size = 4
        self.handles = []
        self.metadata = ObjectMetadata(shape, **kwargs)
        self.rotation_angle = self.metadata.rotation_angle
        self.custom_shape_file_name = None

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
            sp = self.metadata.shape.value(img_file=self.metadata.img_file, stiffness=self.metadata.stiffness, center=Coordinate(self.metadata.x, self.metadata.y), rotation_angle=self.metadata.rotation_angle, scale_factor=self.metadata.scale_factor, beam_diameter=self.metadata.beam_diameter)
        elif self.metadata.shape == Shape.Texture:
            sp = self.metadata.shape.value(shape=self.metadata.texture_shape, spacing_mm=self.metadata.spacing, margins=self.metadata.margins)
        
        self.item = self.canvas.create_line(self.format_xy_coordinates(sp.get_coordinates()))
        # Bind events
        self.canvas.tag_bind(self.item, "<ButtonPress-1>", self.on_button_press)
        self.canvas.tag_bind(self.item, "<B1-Motion>", self.on_move)
        self.canvas.tag_bind(self.item, "<ButtonRelease-1>", self.on_button_release)
        self.canvas.tag_bind(self.item, "<BackSpace>", self.delete_object)


    def on_button_press(self, event):
        self.drag_data = {"x": event.x, "y": event.y}
        if not self.resizing:
            self.select_object()
            self.current_handle = None
        self.canvas.focus_set()
        print("what")
        self.rotation_angle = self.getangle(event)

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
        self.rotate_handle_distance = 2*self.handle_size + (bbox[3] - bbox[1]) / 2

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
        # self.update_handles()

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

    def getangle(self, event):
        bbox = self.canvas.bbox(self.item)
        cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
        dx = self.canvas.canvasx(event.x) - cx
        dy = self.canvas.canvasy(event.y) - cy
        try:
            return complex(dx, dy) / abs(complex(dx, dy))
        except ZeroDivisionError:
            return 0.0 # cannot determine angle
        
    def rotate(self, event):
        if not self.rotating or not self.current_handle:
            return

        # # Calculate the center of the shape (rotation pivot point)
        bbox = self.canvas.bbox(self.item)
        cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2

        # if event.x - cx == 0:
        #     slope = 0
        # else:
        #     slope = (event.y - cy) / (event.x - cx)
        # new_handle_cx = cx + self.rotate_handle_distance * math.cos(math.atan(slope))
        # new_handle_cy = cy + self.rotate_handle_distance * math.sin(math.atan(slope))
        # new_handle_coords = [new_handle_cx - self.handle_size, new_handle_cy - self.handle_size, new_handle_cx + self.handle_size, new_handle_cy - self.handle_size, new_handle_cx + self.handle_size, new_handle_cy + self.handle_size, new_handle_cx - self.handle_size, new_handle_cy + self.handle_size]
        # self.canvas.coords(self.current_handle, new_handle_coords)

        angle = self.getangle(event) / self.rotation_angle
        offset = complex(cx, cy)

        new_coords = []
        origin_coords = self.canvas.coords(self.item)
        # for i in range(0, len(origin_coords), 2):
        #     new_x = fixed_x + (origin_coords[i] - fixed_x) * scale_x
        #     new_y = fixed_y + (origin_coords[i+1] - fixed_y) * scale_y
        #     new_coords.extend([new_x, new_y])

        origin_coords = self.canvas.coords(self.item)
        for i in range(0, len(origin_coords), 2):
            x, y = origin_coords[i], origin_coords[i+1]
            v = angle * (complex(x, y) - offset) + offset
            new_coords.append(v.real)
            new_coords.append(v.imag)
        self.canvas.coords(self.item, *new_coords)

        
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
