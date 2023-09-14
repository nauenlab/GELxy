#Import the necessary libraries to Python.
import ctypes
import clr
import os
import time
import sys

# Add .NET libraries by writing in the full file path to the dll. 
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.DCServoCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.DCServoCLI import *
from System import Decimal

# If you're using Python 3.7 or older change add_dll_directory to chdir
if sys.version_info < (3, 8):
    os.chdir(r"C:\Program Files\IVI Foundation\VISA\Win64\Bin")
else:
    os.add_dll_directory(r"C:\Program Files\IVI Foundation\VISA\Win64\Bin")

#Load C++ library for DC2200
#os.add_dll_directory("C:\Program Files\IVI Foundation\VISA\Win64\Bin")
library=ctypes.cdll.LoadLibrary("TLDC2200_64.dll")

#Connect to devices.
# DC2200.
# !!! In the USB number the serial number (M00...) needs to be changed to the one of the connected device.
devSession = ctypes.c_int()
library.TLDC2200_init(b"USB0::0x1313::0x80C8::M00607903::INSTR",False,False,ctypes.byref(devSession))
print("Device connected.")

#Constant Current (CC) mode
# Make CC settings
library.TLDC2200_setOperationMode(devSession, 0)
library.TLDC2200_setConstCurrent(devSession, ctypes.c_float(0.01))

#KDC101. 
serial_no = str("27264864") #Change to match the serial number on your KDC. 
DeviceManagerCLI.BuildDeviceList()

device = KCubeDCServo.CreateKCubeDCServo(serial_no)
print(DeviceManagerCLI.GetDeviceList())
# Connect, begin polling, and enable KDC. 
device.Connect(serial_no)
time.sleep(0.25)
device.StartPolling(250)
time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
device.EnableDevice()
time.sleep(0.25)  # Wait for device to enable

if not device.IsSettingsInitialized():
    device.WaitForSettingsInitialized(10000)  # 10 second timeout
    assert device.IsSettingsInitialized() is True

    # Before homing or moving device, ensure the motor's configuration is loaded
    m_config = device.LoadMotorConfiguration(serial_no,
    DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

m_config = device.LoadMotorConfiguration(serial_no, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

m_config.DeviceSettingsName = "Z825B" # Chnage to whatever stage you are using. 

m_config.UpdateCurrentConfiguration()

device.SetSettings(device.MotorDeviceSettings, True, False)

#zz=device.RequestVelocityParams()
#GetMoveAbsolutePosition ()
xx=device.DevicePosition
yy=1

zz=device.GetMoveAbsolutePosition ()

# device.Home(60000)



#device.MoveRelative(Forward, 1, 0) 

# device.MoveRelative(Forward,  
#   1,  
#   0    
#  ) 

# device.MoveRelative(MotorDirection.Forward,  
#    1,  
#   0  
#  ) 

#ww = Decimal.ToInt64(2)

# device.SetMoveAbsolutePosition(Decimal(2.0))
# device.MoveAbsolute(0) 

# device.Home(20)

# Set step size and velocity for jog for stage/motor (decimal max velocity, decimal acceleration)
device.SetJogStepSize(Decimal(5.0))
device.SetJogVelocityParams(Decimal(1.0), Decimal(1.0))



#Switch LED on and Jog motor.
library.TLDC2200_setLedOnOff(devSession, True)
# time.sleep(1)
device.MoveJog(MotorDirection.Forward, 0) # (Direction of jog either .forward or .backward, int wait timeout)
#Measure applied LED current
# current = ctypes.c_double()
# library.TLDC2200_get_led_current_measurement(devSession, ctypes.byref(current))
# print("Applied LED current: ", current.value)
# time.sleep(1)
#Change LED current

device.SetMoveAbsolutePosition_DeviceUnit(Decimal(10.0))


library.TLDC2200_setConstCurrent(devSession, ctypes.c_float(1.000))
# time.sleep(5)
# library.TLDC2200_get_led_current_measurement(devSession, ctypes.byref(current))
# print("Applied LED current: ", current.value)
# time.sleep(20)
library.TLDC2200_setLedOnOff(devSession, False)

#Pulse Width Modulation (PWM) mode
#Make PWM settings
# library.TLDC2200_setOperationMode(devSession, 1)
# library.TLDC2200_setPWMCounts(devSession, 20)
# library.TLDC2200_setPWMCurrent(devSession, ctypes.c_float(0.01))
# library.TLDC2200_setPWMDutyCycle(devSession, 50)
# library.TLDC2200_setPWMFrequency(devSession, 10)
#Switch LED on
# library.TLDC2200_setLedOnOff(devSession, True)
#Measure applied LED current 10 times
# for x in range(0, 10):
#     library.TLDC2200_get_led_current_measurement(devSession, ctypes.byref(current))
#     print("Applied current: ", current.value)

# library.TLDC2200_setLedOnOff(devSession, False)

#Close device connection
library.TLDC2200_close(devSession)
# device.Disconnect()

# if __name__ == "__main__":
#     main()
