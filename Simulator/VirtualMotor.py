import math
from Constants import *


class VirtualMotor:
    """
    A class representing a virtual motor.

    Attributes:
        TIME_STEP (float): The time step for each movement in seconds.
        serial_number (str): The serial number of the motor.
        acceleration (float): The acceleration of the motor.
        max_velocity (float): The maximum velocity of the motor.
        position (float): The current position of the motor.

    Methods:
        set_params(self, vmax): Sets the maximum velocity of the motor.
        get_movements(self, new_position, is_lamp_off): Calculates the movements required to reach a new position.
        get_movement_time(self, d, is_lamp_off): Calculates the time required to move a certain distance.
        get_position_change_at(self, t, is_lamp_off): Calculates the change in position at a given time.
        move_absolute(self, final_position): Moves the motor to an absolute position.
    """

    TIME_STEP = 0.01  # 0.01 seconds

    def __init__(self, serial_no=None, acceleration=None, max_velocity=None):
        """
        Initializes the VirtualMotor object.

        Args:
            serial_no (str, optional): The serial number of the motor.
            acceleration (float, optional): The acceleration of the motor.
            max_velocity (float, optional): The maximum velocity of the motor.
        """
        self.serial_number = serial_no
        self.acceleration = acceleration if acceleration else ACCELERATION
        self.max_velocity = max_velocity if max_velocity else MAXIMUM_VELOCITY
        self.position = 0.0
        
    def __del__(self):
        """
        Destructor for the VirtualMotor object.
        """
        pass

    def set_params(self, vmax):
        """
        Sets the maximum velocity of the motor.

        Args:
            vmax (float): The maximum velocity of the motor.
        """
        self.max_velocity = vmax

    def get_movements(self, new_position, is_lamp_off):
        """
        Calculates the movements required to reach a new position.

        Args:
            new_position (float): The new position to move to.
            is_lamp_off (bool): Indicates if the lamp is off.

        Returns:
            list: A list of positions representing the movements required to reach the new position.
        """
        movements = []
        ti = 0
        distance = new_position - self.position
        tf = self.get_movement_time(math.fabs(distance), is_lamp_off)
        while ti - self.TIME_STEP <= tf:
            new_pos = self.get_position_change_at(ti, is_lamp_off)
            change = new_pos if distance > 0 else -new_pos
            movements.append(self.position + change)
            ti += self.TIME_STEP
        self.position = new_position

        return movements

    def get_movement_time(self, d, is_lamp_off):
        """
        Calculates the time required to move a certain distance.

        Args:
            d (float): The distance to move.
            is_lamp_off (bool): Indicates if the lamp is off.

        Returns:
            float: The time required to move the distance.
        """
        v = MAXIMUM_VELOCITY if is_lamp_off or self.max_velocity == 0 else self.max_velocity
        a = ACCELERATION if is_lamp_off else self.acceleration

        max_time = v / a
        t1 = math.sqrt((2*d)/a)
        if t1 < max_time:
            return t1

        t2 = (d - ((a*(max_time**2)) / 2)) / v
        return max_time + t2

    def get_position_change_at(self, t, is_lamp_off):
        """
        Calculates the change in position at a given time.

        Args:
            t (float): The time.
            is_lamp_off (bool): Indicates if the lamp is off.

        Returns:
            float: The change in position at the given time.
        """
        v = MAXIMUM_VELOCITY * 1000 if is_lamp_off else self.max_velocity # MAXIMUM_VELOCITY * 1000 is a hack to make the virtual motor move faster becauase is wastes computation otherwise!
        a = ACCELERATION if is_lamp_off else self.acceleration

        max_time = v / a
        if t < max_time:
            return (a * (t ** 2)) / 2

        c = (v**2 / (2 * a)) - (v * max_time)
        return (v * t) + c

    def move_absolute(self, final_position):
        """
        Moves the motor to an absolute position.

        Args:
            final_position (float): The final position to move to.

        Raises:
            Exception: If the virtual motor takes too long to move.
        """
        original_position = self.position
        distance = final_position - self.position
        current_time = 0

        while math.fabs(self.position - original_position) < math.fabs(distance):
            current_time += self.TIME_STEP
            if current_time > 15:
                raise Exception("Virtual Motor will take too long to move")

            new_pos = self.get_position_change_at(current_time, not final_position.lp)
            self.position += new_pos if distance > 0 else -new_pos
            print(self.position)


