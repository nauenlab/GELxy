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
    # documented min step size 0.00003
    MINIMUM_STEP_SIZE = Decimal(0.001)

    def __init__(self, serial_no, acceleration=None, max_velocity=None):
        self.acceleration = acceleration
        self.max_velocity = max_velocity
        self.serial_number = serial_no
        serial_no = str(serial_no)  # Change to match the serial number on your KDC.
        DeviceManagerCLI.BuildDeviceList()

        self.device = KCubeDCServo.CreateKCubeDCServo(serial_no)
        # Connect, begin polling, and enable KDC.
        try:
            self.device.Connect(serial_no)
        except:
            time.sleep(1)
            self.__init__(serial_no, acceleration, max_velocity)
            return
        self.device.WaitForSettingsInitialized(250)
        # TODO: can we poll the device at a higher rate so we don't have to stop the code via sleep?
        self.device.StartPolling(1)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
        self.device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable

        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.device.IsSettingsInitialized() is True

        # Before homing or moving device, ensure the motor's configuration is loaded
        m_config = self.device.LoadMotorConfiguration(serial_no, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)
        m_config.DeviceSettingsName = "Z825B"  # Change to whatever stage you are using.
        m_config.UpdateCurrentConfiguration()

        settings = self.device.MotorDeviceSettings
        settings.Jog.JogMode = JogParametersBase.JogModes.ContinuousHeld
        settings.Jog.JogStopMode = JogParametersBase.StopModes.Immediate

        self.device.SetSettings(settings, True, False)
        
        self.set_velocity_params(acceleration=acceleration, max_velocity=max_velocity)
                
        # self.home()

        # self.acceleration = acceleration if acceleration else ACCELERATION # get max values from device.AdvanedMotorLimits
        # self.max_velocity = max_velocity if max_velocity else MAXIMUM_VELOCITY

    def __del__(self):
        try:
            self.device.StopPolling()
        except:
            pass
        try:
            self.device.ShutDown()
        except:
            pass

    def home(self):
        print(f"homing motor id {self.serial_number}")
        self.device.SetHomingVelocity(Decimal(2.6))
        self.device.Home(50000)

    def set_params(self, vmax):
        # print("Velocity: ", vmax, "mm/s")
        self.set_velocity_params(max_velocity=vmax)

    def set_velocity_params(self, acceleration=None, max_velocity=None):
        # Set the velocity and acceleration parameters
        vp = self.device.GetJogParams().VelocityParams
        vp.Acceleration = Decimal(acceleration) if acceleration else vp.Acceleration
        vp.MaxVelocity = Decimal(max_velocity) if max_velocity else vp.MaxVelocity

        self.device.SetJogVelocityParams(vp.MaxVelocity, vp.Acceleration)
        self.device.SetVelocityParams(vp)

    def jog_to(self, absolute_position):
        # To make more accurate, reduce the polling frequency in the initializer

        motor_position = self.device.Position
        relative_movement = Decimal(absolute_position) - motor_position
        # print("relative movement:", relative_movement)
        # self.device.SetJogStepSize(relative_movement)

        zero = Decimal(0)
        movement_expected = True
        isForward = True

        if relative_movement > zero and relative_movement > self.MINIMUM_STEP_SIZE:
            self.device.MoveJog(MotorDirection.Forward, 0)
        elif relative_movement < zero and relative_movement < -self.MINIMUM_STEP_SIZE:
            self.device.MoveJog(MotorDirection.Backward, 0)
            isForward = False
        else:
            # print("no move necessary")
            movement_expected = False
        
        if movement_expected:
            travel = self.device.Position - motor_position
            while not (isForward and travel >= relative_movement or not isForward and travel <= relative_movement):
                travel = self.device.Position - motor_position
                continue
            self.device.StopImmediate()

            while self.device.Status.IsJogging:
                continue

            error = self.device.Position - motor_position - relative_movement
            # print(f"new position: {self.device.Position}")
            # print(f"error: {error}")

    def move_absolute(self, absolute_position):
        self.set_velocity_params(acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY)
        self.device.MoveTo(Decimal(absolute_position), 15000)
        self.set_velocity_params(acceleration=self.acceleration, max_velocity=self.max_velocity)



