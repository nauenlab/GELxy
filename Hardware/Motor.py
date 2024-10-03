import clr
import time
from Constants import *

# Add .NET libraries by writing in the full file path to the dll.
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.DCServoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.DCServoCLI import *
from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import *
from System import Decimal


class Motor:
    """
    Represents a motor controller for a KCube DC Servo motor.

    Args:
        serial_no (int): The serial number of the motor.
        acceleration (float, optional): The acceleration value in mm/s^2. Defaults to None.
        max_velocity (float, optional): The maximum velocity value in mm/s. Defaults to None.
    """

    # documented min step size 0.001
    MINIMUM_STEP_SIZE = Decimal(0.001)

    def __init__(self, serial_no, acceleration=None, max_velocity=None):
        """
        Initializes a new instance of the Motor class.

        Args:
            serial_no (int): The serial number of the motor.
            acceleration (float, optional): The acceleration value in mm/s^2. Defaults to None.
            max_velocity (float, optional): The maximum velocity value in mm/s. Defaults to None.
        """
        self.acceleration = acceleration
        self.max_velocity = max_velocity
        self.serial_number = serial_no
        serial_no = str(serial_no)  # Change to match the serial number on your KDC.
        DeviceManagerCLI.BuildDeviceList()

        self.device = KCubeDCServo.CreateKCubeDCServo(serial_no)
        if self.device is None:
            raise Exception(f"Device {serial_no} not found.")
        
        # Connect KDC.
        try:
            self.device.Connect(serial_no)
        except:
            time.sleep(1)
            print(f"Failed to connect to motor {serial_no}. Retrying...")
            self.__init__(serial_no, acceleration, max_velocity)
            return

        # Wait for the device settings to initialize, if they are not already initialized.
        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.device.IsSettingsInitialized() is True

        self.device.StartPolling(20)  # Poll at 2 ms intervals
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
        self.device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable
        print(f"Motor connected {serial_no}.")

        # Before homing or moving device, ensure the motor's configuration is loaded
        m_config = self.device.LoadMotorConfiguration(serial_no, DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings)
        m_config.DeviceSettingsName = "Z825"  # Change to whatever stage you are using.
        m_config.UpdateCurrentConfiguration()

        settings = self.device.MotorDeviceSettings
        settings.Jog.JogMode = JogParametersBase.JogModes.ContinuousHeld
        settings.Jog.JogStopMode = JogParametersBase.StopModes.Immediate

        self.device.SetSettings(settings, True, False)
        
        self.set_velocity_params(acceleration=acceleration, max_velocity=max_velocity)

    def __del__(self):
        """
        Cleans up the resources used by the Motor instance.
        """
        try:
            self.device.StopPolling()
        except:
            pass
        try:
            self.device.ShutDown()
        except:
            pass

    def home(self):
        """
        Homes the motor to the reference position.
        """
        print(f"homing motor id {self.serial_number}")
        self.device.SetHomingVelocity(Decimal(2.6))
        self.device.Home(50000)

    def set_params(self, velocity):
        """
        Sets the velocity parameters of the motor.

        Args:
            velocity (float): The maximum velocity value in mm/s.
        """
        self.set_velocity_params(max_velocity=velocity)

    def set_velocity_params(self, acceleration=None, max_velocity=None):
        """
        Sets the velocity and acceleration parameters of the motor.

        Args:
            acceleration (float, optional): The acceleration value in mm/s^2. Defaults to None.
            max_velocity (float, optional): The maximum velocity value in mm/s. Defaults to None.
        """
        # Set the velocity and acceleration parameters
        vp = self.device.GetJogParams().VelocityParams
        vp.Acceleration = Decimal(acceleration) if acceleration else vp.Acceleration
        vp.MaxVelocity = Decimal(max_velocity) if max_velocity else vp.MaxVelocity

        self.device.SetJogVelocityParams(vp.MaxVelocity, vp.Acceleration)
        self.device.SetVelocityParams(vp)

    def jog_to(self, absolute_position):
        """
        Moves the motor to the specified absolute position using jogging.

        Args:
            absolute_position (float): The absolute position to move the motor to in mm.
        """
        # To make more accurate, reduce the polling frequency in the initializer

        motor_position = self.device.Position
        relative_movement = Decimal(float(absolute_position)) - motor_position

        zero = Decimal(0)
        movement_expected = True
        isForward = True

        try:
            if relative_movement > zero and relative_movement > self.MINIMUM_STEP_SIZE:
                self.device.MoveJog(MotorDirection.Forward, 0)
            elif relative_movement < zero and relative_movement < -self.MINIMUM_STEP_SIZE:
                self.device.MoveJog(MotorDirection.Backward, 0)
                isForward = False
            else:
                movement_expected = False
        except Exception as e:
            print(e)
            print(self.serial_number)

        if movement_expected:
            travel = self.device.Position - motor_position
            while not (isForward and travel >= relative_movement or not isForward and travel <= relative_movement):
                travel = self.device.Position - motor_position
                continue
            self.device.StopImmediate()

            while self.device.Status.IsJogging:
                continue

    def move_absolute(self, absolute_position):
        """
        Moves the motor to the specified absolute position.

        Args:
            absolute_position (Decimal): The absolute position to move the motor to in mm.
        """
        self.set_velocity_params(acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY)
        self.device.MoveTo(Decimal(float(absolute_position)), 30000)
        self.set_velocity_params(acceleration=self.acceleration, max_velocity=self.max_velocity)



