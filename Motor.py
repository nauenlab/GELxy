import clr
import time

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
    def __init__(self, sleep_time, serial_no, acceleration=None, max_velocity=None, min_velocity=None):
        self.acceleration = acceleration
        self.max_velocity = max_velocity
        self.min_velocity = min_velocity
        self.sleep_time = sleep_time
        self.serial_number = serial_no
        serial_no = str(serial_no)  # Change to match the serial number on your KDC.
        DeviceManagerCLI.BuildDeviceList()

        self.device = KCubeDCServo.CreateKCubeDCServo(serial_no)
        # Connect, begin polling, and enable KDC.
        try:
            self.device.Connect(serial_no)
        except:
            time.sleep(1)
            self.__init__(sleep_time, serial_no, acceleration, max_velocity, min_velocity)
            return
        self.device.WaitForSettingsInitialized(250)
        # TODO: can we poll the device at a higher rate so we don't have to stop the code via sleep?
        self.device.StartPolling(250)
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
        settings.Jog.JogStopMode = JogParametersBase.StopModes.
        print(settings.Jog.JogMode)
        print(settings.Jog.JogStopMode)

        self.device.SetSettings(settings, True, False)
        print(deviceX.MotorDeviceSettings.Jog.JogStopMode)
        
        self.set_velocity_params(acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
                
        self.home()

        # self.acceleration = acceleration if acceleration else 4.0 # get max values from device.AdvanedMotorLimits
        # self.max_velocity = max_velocity if max_velocity else 2.6
        # self.min_velocity = min_velocity if min_velocity else 2.6

    def __del__(self):
        self.device.StopPolling()
        self.device.ShutDown()

    def home(self):
        print(f"homing {self.serial_number}")
        self.device.SetHomingVelocity(Decimal(2.6))
        self.device.Home(50000)

    def set_params(self, vmax):
        self.set_velocity_params(max_velocity=vmax, min_velocity=vmax)

    def set_velocity_params(self, acceleration=None, max_velocity=None, min_velocity=None):
        # Set the velocity and acceleration parameters
        vp = self.device.GetVelocityParams()
        vp.Acceleration = Decimal(acceleration) if acceleration else vp.Acceleration
        vp.MaxVelocity = Decimal(max_velocity) if max_velocity else vp.MaxVelocity
        vp.MinVelocity = Decimal(min_velocity) if min_velocity else vp.MinVelocity
        self.device.SetVelocityParams(vp)
        self.device.SetJogVelocityParams(Decimal(max_velocity), Decimal(acceleration))

    def jog_to(self, absolute_position, timeout, is_first_move):
        if is_first_move:
            self.set_velocity_params(acceleration=4.0, max_velocity=2.6, min_velocity=2.6)
        motor_position = self.device.Position
        relative_movement = absolute_position - motor_position
        self.device.SetJogStepSize(Decimal(0.01))
        if relative_movement > 0:
            self.device.MoveJog(MotorDirection.Forward, timeout)
        elif relative_movement < 0:
            self.device.MoveJog(MotorDirection.Backward, timeout)
        while not self.device.Status.IsInMotion:
            continue
        while (self.device.Position - motor_position) <= Decimal(relative_movement) <= (self.device.Position - motor_position):
            continue
        self.device.StopImmediate()
        if is_first_move:
            self.set_velocity_params(acceleration=self.acceleration, max_velocity=self.max_velocity, min_velocity=self.min_velocity)


    def move_absolute(self, absolute_position, timeout, is_first_move=False):
        if is_first_move:
            self.set_velocity_params(acceleration=4.0, max_velocity=2.6, min_velocity=2.6)
        self.device.MoveTo(Decimal(absolute_position), timeout)
        if is_first_move:
            self.set_velocity_params(acceleration=self.acceleration, max_velocity=self.max_velocity, min_velocity=self.min_velocity)



