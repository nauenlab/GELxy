from Coordinate import Coordinate, Coordinates
from tqdm import tqdm
from CuringCalculations import CuringCalculations
import copy

class Gradient:
    """
    Represents a gradient shape.

    Args:
        min_velocity (float): The minimum velocity of the gradient.
        max_velocity (float): The maximum velocity of the gradient.
        beam_diameter (float): The diameter of the beam.
        is_horizontal (bool, optional): Whether the gradient is horizontal. Defaults to True.
        is_reversed (bool, optional): Whether the gradient is reversed. Defaults to True.
    """

    def __init__(self, min_stiffness, max_stiffness, beam_diameter, is_horizontal=True, is_reversed=True):
        self.is_horizontal = is_horizontal
        self.min_stiffness = min_stiffness
        self.max_stiffness = max_stiffness
        self.is_reversed = is_reversed
        self.beam_diameter = beam_diameter

    def get_coordinates(self):
        """
        Generates the coordinates for the gradient shape.

        Returns:
            Coordinates: The generated coordinates.
        """
        coordinates = Coordinates()
        le = -5
        r = 15
        u = -5
        d = 15
        curing_calculations = CuringCalculations()
        iter_range = range(0, int(d * (1 / self.beam_diameter)) + 1, int(self.beam_diameter * (1 / self.beam_diameter)))
        stiffness_step = float(self.max_stiffness - self.min_stiffness)/(len(iter_range)*2)
        cur_s = self.min_stiffness
        for i in tqdm(iter_range, desc="Getting Coordinates"):
            i = float(i) / (1 / self.beam_diameter)
            temp_coords = Coordinates()
            if self.is_horizontal:
                temp_coords.append(Coordinate(i, u))
                temp_coords.append(Coordinate(i, d))
            else:
                temp_coords.append(Coordinate(le, i))
                temp_coords.append(Coordinate(r, i))
            
            configuration = curing_calculations.get_configuration(cur_s, self.beam_diameter)
            temp_coords.update_with_configuration(configuration)
            for i in temp_coords:
                print(i)
            original_coordinates = copy.deepcopy(temp_coords)
            while configuration.iterations > 1:
                temp_coords += original_coordinates
                configuration.iterations -= 1
            
            temp_coords[0].lp = False
            coordinates += temp_coords
            cur_s += stiffness_step

        
        # if self.is_reversed:
        #     coordinates.coordinates.reverse()
        
        return coordinates
