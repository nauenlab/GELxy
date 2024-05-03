import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from VirtualMotor import VirtualMotor
from VirtualLamp import VirtualLamp
from Simulator.Canvas import Canvas

class VirtualManager:
    """
    The VirtualManager class represents a virtual manager for controlling motors and lamps in a simulation.

    Attributes:
        canvas (Canvas): The canvas object representing the simulation environment.
        x (VirtualMotor): The virtual motor controlling the x-axis movement.
        y (VirtualMotor): The virtual motor controlling the y-axis movement.
        lamp (VirtualLamp): The virtual lamp used for curing.
        beam_diameter (float): The diameter of the curing beam.

    Methods:
        motors(): Returns the x and y virtual motors.
        move(position): Moves the motors and controls the lamp based on the given position.
    """

    def __init__(self, canvas_dimensions_mm, acceleration=None, max_velocity=None, beam_diameter=None):
        """
        Initializes a new instance of the VirtualManager class.

        Args:
            canvas_dimensions_mm (tuple): The dimensions of the canvas in millimeters (width, height).
            acceleration (float, optional): The acceleration of the virtual motors. Defaults to None.
            max_velocity (float, optional): The maximum velocity of the virtual motors. Defaults to None.
            beam_diameter (float, optional): The diameter of the curing beam. Defaults to None.
        """
        self.canvas = Canvas(dimensions_mm=canvas_dimensions_mm)
        self.x = VirtualMotor(acceleration=acceleration, max_velocity=max_velocity)
        self.y = VirtualMotor(acceleration=acceleration, max_velocity=max_velocity)
        self.lamp = VirtualLamp(canvas=self.canvas)
        self.beam_diameter = beam_diameter

    def motors(self):
        """
        Returns the x and y virtual motors.

        Returns:
            tuple: The x and y virtual motors.
        """
        return self.x, self.y

    def move(self, position):
        """
        Moves the virtual motors and controls the lamp based on the given position.

        Args:
            position (Position): The position object containing the motor and lamp parameters.
        """
        is_lamp_on = position.lp
        if is_lamp_on:
            self.x.set_params(position.v[0])
            self.y.set_params(position.v[1])
        x_mvts = self.x.get_movements(position.x, not is_lamp_on)
        y_mvts = self.y.get_movements(position.y, not is_lamp_on)
        for i in range(max(len(x_mvts), len(y_mvts))):
            x_i = i if i < len(x_mvts) else len(x_mvts) - 1
            y_i = i if i < len(y_mvts) else len(y_mvts) - 1
            x_pos = x_mvts[x_i]
            y_pos = y_mvts[y_i]
            if is_lamp_on:
                self.lamp.cure(x_pos, y_pos, self.beam_diameter, position.a)

    def __del__(self):
        """
        Cleans up the virtual motors and lamp when the VirtualManager object is deleted.
        """
        self.x.__del__()
        self.y.__del__()
        self.lamp.__del__()
