



class VirtualMotor:
    def __init__(self, sleep_time, serial_no=None, acceleration=None, max_velocity=None, min_velocity=None):
        self.sleep_time = sleep_time
        self.serial_number = serial_no
        self.acceleration = acceleration if acceleration else 4.0
        self.max_velocity = max_velocity if max_velocity else 2.6
        self.min_velocity = min_velocity if min_velocity else 2.6
        self.position = 0.0
        
        
    def move_lag():
        pass


    def move_absolute(self, new_position, timeout, isFirstMove):
        if isFirstMove:
            self.setVelocityParams(acceleration=4.0, max_velocity=2.6, min_velocity=2.6)
        self.move_lag()
        
        if self.position < new_position:
            # move forwards
            
        else:
            #move reverse
        
        
        
        
        
        
        self.device.MoveTo(Decimal(absolute_position), timeout)
        if isFirstMove:
            self.setVelocityParams(acceleration=self.acceleration, max_velocity=self.max_velocity, min_velocity=self.min_velocity)


