import clr
import time

# Add .NET libraries by writing in the full file path to the dll.
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.DCServoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.DCServoCLI import *
from System import Decimal


class Motor:
    def __init__(self, sleep_time, serial_no, acceleration=None, max_velocity=None, min_velocity=None):
        self.sleep_time = sleep_time
        self.serial_number = serial_no
        serial_no = str(serial_no)  # Change to match the serial number on your KDC.
        DeviceManagerCLI.BuildDeviceList()

        self.device = KCubeDCServo.CreateKCubeDCServo(serial_no)
        # Connect, begin polling, and enable KDC.
        self.device.Connect(serial_no)
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
        m_config.DeviceSettingsName = "Z825B"  # Chnage to whatever stage you are using.
        m_config.UpdateCurrentConfiguration()

        self.device.SetSettings(self.device.MotorDeviceSettings, True, False)

        # Set the velocity and acceleration parameters
        vp = self.device.GetVelocityParams()
        vp.Acceleration = Decimal(acceleration) if acceleration else vp.Acceleration
        vp.MaxVelocity = Decimal(max_velocity) if max_velocity else vp.MaxVelocity
        vp.MinVelocity = Decimal(min_velocity) if min_velocity else vp.MinVelocity
        self.device.SetVelocityParams(vp)
                
        self.home()

        # self.acceleration = acceleration if acceleration else 4.0 # get max values from device.AdvanedMotorLimits
        # self.max_velocity = max_velocity if max_velocity else 2.6
        # self.min_velocity = min_velocity if min_velocity else 2.6

    def __del__(self):
        self.device.stopPolling()
        self.device.shutDown()
        
        
    def home(self):
        print(f"homing {serial_no}")
        self.device.SetHomingVelocity(Decimal(2.6))
        self.device.Home(50000)

    # def move_relative(self, relative_position):
    # NOT FINIISHED
    #     self.device.SetJogStepSize(Decimal(relative_position))
    #     if relative_position > 0:
    #         self.device.MoveJog(MotorDirection.Forward, 0)
    #     elif relative_position < 0:
    #         self.device.MoveJog(MotorDirection.Backward, 0)

    def move_absolute(self, absolute_position):
        self.device.MoveTo(Decimal(absolute_position), 10000)



