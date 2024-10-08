from Constants import MAXIMUM_CURRENT


class VirtualLamp:
    """
    Represents a virtual lamp used for curing in a simulator.

    Attributes:
        canvas (Canvas): The virtual canvas object on which the curing is performed.
        is_on (bool): Indicates whether the lamp is turned on or off.
    
    Methods:
        turn_on(_): Turns on the virtual lamp.
        cure(x, y, beam_diameter, curing_rate): Performs curing on the specified coordinates.
        turn_off(): Turns off the virtual lamp.
    """

    def __init__(self, time_step, canvas):
        """
        Initializes a new instance of the VirtualLamp class.

        Args:
            canvas (object): The canvas object on which the curing is performed.
        """
        self.time_step = time_step
        self.canvas = canvas
        self.is_on = False

    def __del__(self):
        """
        Placeholder destructor for the VirtualLamp class.
        """
        pass

    def turn_on(self, _):
        """
        Turns on the virtual lamp.
        """
        self.is_on = True

    def cure(self, x, y, beam_diameter, curing_rate):
        """
        Performs curing on the specified coordinates.

        Args:
            x (float): The x-coordinate of the curing location.
            y (float): The y-coordinate of the curing location.
            beam_diameter (float): The diameter of the curing beam.
            curing_rate (float): The rate of curing.

        """
        curing_percentage = (curing_rate / MAXIMUM_CURRENT) * 1000 * self.time_step
        self.canvas.cure(x, y, beam_diameter, curing_percentage)

    def turn_off(self):
        """
        Turns off the virtual lamp.
        """
        self.is_on = False
