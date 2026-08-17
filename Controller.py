import signal
import sys
import os
from tqdm import tqdm

import CommonPatterns
from Shapes import *
from Coordinate import Coordinate, Coordinates
from Constants import *
from Multiprocessor import Multiprocessor
from EstimatedCompletionTime import EstimatedCompletionTime

### INSTRUCTIONS
### STEP 1: Connect the motors and LED to the computer using USB cables.
### STEP 2: Change the IS_SIMULATOR value to True if you want to run the motors in a virtual simulation. Change the IS_SIMULATOR value to False if you want to run the motors in real life.
###         It is recommended to run the motors in a virtual simulation first to see how the motors will move before running the motors in real life.
### STEP 3: Change the center_coordinate value in the main function. The center coordinate will be used to determine the center of each shape, texture, or pattern.
### STEP 4: Choose which shapes, textures, or patterns to draw and uncomment the desired shape, texture, or pattern from the list in the main function.
### STEP 5: Run the program. The motors will move to draw the shapes, textures, or patterns.
###
### IMAGE VALIDATION: `python Controller.py validate Hippocampus.png` compares the images that share that
###         base name across the "Image Validation" folders (SSIM + contour deviation) and prints the metrics.
###         Run `python Controller.py validate --help` for the options. `python Controller.py roi Hippocampus.png` lets you
###         outline the region of interest on the histology image used by pipeline 1.

IS_SIMULATOR = True

IMAGE_VALIDATION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Image Validation")

X_MOTOR_SERIAL_NUMBER = "27602218"
Y_MOTOR_SERIAL_NUMBER = "27264864"
LAMP_SERIAL_NUMBER = b"USB0::0x1313::0x80C8::M00607903::INSTR"

class Controller:

    @staticmethod
    def optimize_shape_order(coordinate_sets):
        """Reorders coordinate sets by nearest-neighbor to minimize inter-shape travel."""
        non_empty = [cs for cs in coordinate_sets if len(cs) > 0]
        if len(non_empty) <= 1:
            return non_empty

        remaining = list(range(len(non_empty)))
        ordered = []
        current_x, current_y = 0.0, 0.0

        while remaining:
            best_idx = None
            best_dist_sq = float('inf')
            for idx in remaining:
                first = non_empty[idx][0]
                dx = float(first.x) - current_x
                dy = float(first.y) - current_y
                dist_sq = dx * dx + dy * dy
                if dist_sq < best_dist_sq:
                    best_dist_sq = dist_sq
                    best_idx = idx

            remaining.remove(best_idx)
            ordered.append(non_empty[best_idx])
            last = non_empty[best_idx][-1]
            current_x = float(last.x)
            current_y = float(last.y)

        return ordered

    def main(self):
        shapes = []
        center_coordinate = Coordinate(12.5, 12.5)
        
        # Rectangle
        # shapes.append(Rectangle(width_mm=5, height_mm=3, stiffness=20000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=True))
        
        # Square
        # shapes.append(Square(side_length_mm=2, stiffness=0, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=False))
        
        # Equilateral Triangle
        # shapes.append(EquilateralTriangle(side_length_mm=2, stiffness=10000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=False))
        
        # Triangle
        # shapes.append(Triangle(width_mm=2, height_mm=2.5980762114, stiffness=10000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False, filled=True))
        
        # Line
        # shapes.append(Line(length_mm=5, stiffness=20000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True))
        
        # Oval
        # shapes.append(Oval(width_mm=2, height_mm=3, stiffness=10000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, filled=True))
        
        # Circle
        # shapes.append(Circle(diameter_mm=2, stiffness=20000, center=center_coordinate, beam_diameter=BEAM_DIAMETER, filled=True))
        
        # Sine Wave
        # shapes.append(SineWave(amplitude_mm=1, cycles=5, cycles_per_mm=0.5, stiffness=10000, cycle_offset=0, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER))
        
        # Gradient
        # shapes.append(Gradient(min_stiffness=5000, max_stiffness=20000, width_mm=3, height_mm=8, center=center_coordinate, beam_diameter=BEAM_DIAMETER, rotation_angle_degrees=0, is_reversed=True))

        # Gradient Line
        # shapes.append(GradientLine(length_mm=8, min_stiffness=500, max_stiffness=20000, center=center_coordinate, beam_diameter=BEAM_DIAMETER, rotation_angle_degrees=0, is_reversed=False, num_steps=20))

        # Custom Pattern
        # shapes.append(HistologyImage(img_file="test_images/examplehistology_adultcerebellumadditional40x.jpg", center=center_coordinate, height_mm=3, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER))
        # shapes.append(HistologyImage(img_file="test_images/examplehistology_adultvisualctx20x.png", stiffness=10000, center=center_coordinate, height_mm=3, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER))
        
        # Texture
        # texture_shape = EquilateralTriangle(side_length_mm=1, stiffness=10000, center=None, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False, filled=False)
        # shapes.append(Texture(shape=texture_shape, center=center_coordinate, rows=None, columns=None, spacing_mm=1.5, margins=11))

        # Common Patterns
        # shapes.extend(CommonPatterns.atom(width_mm=10, height_mm=4, center=center_coordinate, stiffness=50000))
        # shapes.extend(CommonPatterns.deathly_hallows(size_mm=5, center=center_coordinate, stiffness=10000))
        # shapes.extend(CommonPatterns.rounded_square(length_mm=5, center=center_coordinate, stiffness=50000))

        coordinate_sets = Multiprocessor().get_coordinate_sets(shapes)
        coordinate_sets = Controller.optimize_shape_order(coordinate_sets)

        coordinates = Coordinates()
        for i in coordinate_sets:
            coordinates += i

        # Estimated Completion Time
        completion_time = EstimatedCompletionTime(coordinates).get_completion_time()
        print(f"Estimated Completion Time: {int(completion_time // 3600)} hours {int((completion_time % 3600) // 60)} minutes {int(completion_time % 60)} seconds")

        if IS_SIMULATOR:
            from Simulator.VirtualManager import VirtualManager
            # Sets up a virtual simulation of the motors and LED
            self.manager = VirtualManager(canvas_dimensions_mm=MOTOR_MAX_TRAVEL, acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY, beam_diameter=BEAM_DIAMETER)
        else:
            from Hardware.Manager import Manager
            # Sets up the actual motors and LED
            self.manager = Manager(serial_number_x=X_MOTOR_SERIAL_NUMBER, serial_number_y=Y_MOTOR_SERIAL_NUMBER, lamp_serial_number=LAMP_SERIAL_NUMBER, acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY)
        
        if not IS_SIMULATOR:
            print("Going to Centroid of aggregated shapes.")
            center_of_shapes = coordinates.get_centroid()
            center_of_shapes.lp = False
            print("Centroid of aggregated shapes:", center_of_shapes)
            self.manager.move(center_of_shapes)
            print("First coordinate reached. Please adjust stage and gel as needed.")
            lamp_on = input("Would you like to turn the lamp on to 1 mA for calibration? (y/n):")
            if lamp_on == "y":
                self.manager.lamp.turn_on(0.001)
            
            input("Press any key to continue.")
            self.manager.lamp.turn_off()

        for coordinate in tqdm(coordinates, desc="Moving Motors", unit="coordinate"):
            self.manager.move(coordinate)

        if IS_SIMULATOR:
            self.manager.lamp.canvas.draw()
    
    @staticmethod
    def validate(argv):
        """
        Runs the image validation pipelines for a base file name, e.g. `validate Hippocampus.png`.

        Pipeline 1 compares the pc12 culture image with the original histology image; pipeline 2 compares
        the image-processing segmentation with the manual segmentation. Both report structural similarity
        (SSIM) and contour deviation error and print them to the CLI.
        """
        import argparse
        parser = argparse.ArgumentParser(prog="Controller.py validate",
                                         description="Image validation: SSIM + contour deviation metrics.")
        parser.add_argument("base_name", help="base image file name shared across the Image Validation folders, e.g. Hippocampus.png")
        parser.add_argument("--pipeline", choices=["pc12", "segmentation", "both"], default="both",
                            help="which pipeline to run (default: both)")
        parser.add_argument("--mm-height", type=float, default=None,
                            help="physical height of the reference image in mm; adds mm units to distances")
        parser.add_argument("--alignment", choices=["auto", "full-frame", "content-crop"], default="auto",
                            help="pipeline 2 field-of-view handling (default: auto)")
        parser.add_argument("--register", choices=["translation", "rigid", "none"], default="translation",
                            help="align the second image to the reference before measuring: rigid = rotation+"
                                 "translation for pipeline 1 (pipeline 2 uses translation), translation, or none (default: translation)")
        parser.add_argument("--roi", choices=["auto", "none"], default="auto",
                            help="pipeline 1 region of interest: auto = use Image Validation/ROI/<name>.png if it exists "
                                 "(draw it with `Controller.py roi <name>`), else histology structures touched by the cells; "
                                 "none = compare all structures")
        parser.add_argument("--verbose", "-v", action="store_true", help="print the full diagnostics instead of the compact summary")
        parser.add_argument("--no-save", action="store_true",
                            help="do not write standardized images / heat maps under Image Validation/Standardized/")
        args = parser.parse_args(argv)

        sys.path.insert(0, IMAGE_VALIDATION_DIR)
        from validation import run_validation
        return run_validation(args.base_name, pipeline=args.pipeline, mm_height=args.mm_height,
                              save=not args.no_save, register=args.register, alignment=args.alignment,
                              roi=args.roi, verbose=args.verbose)

    @staticmethod
    def draw_roi(argv):
        """
        Opens an interactive window to outline the region of interest on the histology image for pipeline 1,
        e.g. `python Controller.py roi Hippocampus.png`. The mask is saved to Image Validation/ROI/<name>.png.
        """
        import argparse
        parser = argparse.ArgumentParser(prog="Controller.py roi",
                                         description="Draw the pipeline-1 region of interest on the histology image.")
        parser.add_argument("base_name", help="base image file name, e.g. Hippocampus.png")
        args = parser.parse_args(argv)
        sys.path.insert(0, IMAGE_VALIDATION_DIR)
        from validation.roi import draw_roi
        saved = draw_roi(args.base_name)
        print(f"ROI saved to {saved}" if saved else "No ROI drawn; nothing saved.")

    def __del__(self):
        """
        Cleans up the resources used by the Controller instance.
        """
        try:
            self.manager.__del__()
        except:
            pass


controller = Controller()

def exit_handler(*args):
    print("Cleaning Up!")
    controller.__del__()
    os.environ["current_time"] = "0"
    sys.exit(0)


signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        Controller.validate(sys.argv[2:])
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "roi":
        Controller.draw_roi(sys.argv[2:])
        sys.exit(0)
    controller.main()
    exit_handler()