import math
from Constants import MAXIMUM_VELOCITY

class EstimatedCompletionTime:
    def __init__(self, coordinates) -> None:
        self.coordinates = coordinates

    def movement_time(self, _from, to):
        """
        Calculates the time required to move from this coordinate to another coordinate with a given velocity.

        Args:
            _from (Coordinate): The starting coordinate.
            to (Coordinate): The destination coordinate.

        Returns:
            float: The time duration for the movement.
        """
        x_velocity, y_velocity = to.v if to.v else (MAXIMUM_VELOCITY, MAXIMUM_VELOCITY)
        xi, yi = _from.x, _from.y
        xf, yf = to.x, to.y
        
        a = 4.0
        v = 0
        if x_velocity != 0:
            d = math.fabs(xf - xi)
            v = x_velocity
        if y_velocity != 0:
            d = math.fabs(yf - yi) 
            v = y_velocity
            
        t = (v**2 + 2 * a * d) / (2 * a * v)
        return t

    def get_completion_time(self):
        seconds = 0
        prev = None
        for i in self.coordinates:
            if prev:
                seconds += self.movement_time(prev, i)
            
            prev = i
        
        # offset for downtime between movements
        seconds += len(self.coordinates) * 0.205

        return seconds