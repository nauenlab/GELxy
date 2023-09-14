import ctypes
import clr
import os
import time
import sys
import math

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
serial_no1 = str("27264864") #Change to match the serial number on your KDC. 
serial_no2 = str("27602218")
DeviceManagerCLI.BuildDeviceList()

deviceY = KCubeDCServo.CreateKCubeDCServo(serial_no1)
deviceX = KCubeDCServo.CreateKCubeDCServo(serial_no2)
print(DeviceManagerCLI.GetDeviceList())
# Connect, begin polling, and enable KDC. 
deviceX.Connect(serial_no1)
deviceY.Connect(serial_no2)
time.sleep(0.25)
deviceY.StartPolling(250)
deviceX.StartPolling(250)
time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
deviceY.EnableDevice()
deviceX.EnableDevice()
time.sleep(0.25)  # Wait for device to enable

if not deviceY.IsSettingsInitialized():
    deviceY.WaitForSettingsInitialized(10000)  # 10 second timeout
    assert deviceY.IsSettingsInitialized() is True
    
if not deviceX.IsSettingsInitialized():
    deviceX.WaitForSettingsInitialized(10000)  # 10 second timeout
    assert deviceX.IsSettingsInitialized() is True

# Before homing or moving device, ensure the motor's configuration is loaded
m_config = deviceY.LoadMotorConfiguration(serial_no1,
DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)
m_config = deviceX.LoadMotorConfiguration(serial_no2,
DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

m_config = deviceY.LoadMotorConfiguration(serial_no1, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)
m_config = deviceX.LoadMotorConfiguration(serial_no2, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

m_config.DeviceSettingsName = "Z825B" # Chnage to whatever stage you are using. 

m_config.UpdateCurrentConfiguration()

deviceY.SetSettings(deviceY.MotorDeviceSettings, True, False)
deviceX.SetSettings(deviceX.MotorDeviceSettings, True, False)

# Set step size and velocity for jog for stage/motor (decimal max velocity, decimal acceleration)
deviceY.SetJogStepSize(Decimal(.01))
deviceY.SetJogVelocityParams(Decimal(0.1), Decimal(0.2))
deviceX.SetJogStepSize(Decimal(.01))
deviceX.SetJogVelocityParams(Decimal(0.1), Decimal(0.2))

#ORIGINAL VALUES 
# deviceY.SetJogStepSize(Decimal(1))
# deviceY.SetJogVelocityParams(Decimal(0.5), Decimal(1.0))
# deviceX.SetJogStepSize(Decimal(1))
# deviceX.SetJogVelocityParams(Decimal(0.5), Decimal(1.0))

#declare motor thread sleep 
ms = float(.4)

#declare LED ampere 
b = float(.01)


# Create sine wave
# Create sine wave
for i in range(90):
    x_pos = math.sin(math.radians(i))
    y_pos = math.sin(math.radians(i+90))
    
    # Move motors by an amount proportional to the calculated positions
    deviceX.MoveJog(MotorDirection.Forward if x_pos > 0 else MotorDirection.Backward, abs(x_pos))
    deviceY.MoveJog(MotorDirection.Forward if y_pos > 0 else MotorDirection.Backward, abs(y_pos))
   

     
    # time.sleep(3)
          #Get LED ready 
    
    print(x_pos, y_pos)    
    
    #Get LED ready 
    library.TLDC2200_setLedOnOff(devSession, True)
     
      #Allow time for motor threads to start moving
    time.sleep(ms)
     
      #while loop for setting LED current to a specific ampere w.r.t to motor motion 
   
    while    (deviceX.Status.IsInMotion == True): 
            library.TLDC2200_setConstCurrent(devSession, ctypes.c_float(b))
            print ("LED on")
    else:
            print ("LED off")
            library.TLDC2200_setConstCurrent(devSession, ctypes.c_float(0.000))
     
     
      #Turn off LED
    library.TLDC2200_setLedOnOff(devSession, False)
    
    time.sleep(3)

    # else:
    #     deviceX.MoveJog(MotorDirection.Backward, 0)
    # if y_pos > 0:
    #     deviceY.MoveJog(MotorDirection.Forward, 0)
    # else:
    #     deviceY.MoveJog(MotorDirection.Backward, 0)
    
    # time.sleep(3)



