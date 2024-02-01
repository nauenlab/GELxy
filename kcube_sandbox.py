import ctypes
import sys
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

# for jogmodes
from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import *
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

# Connect, begin polling, and enable KDC. 
def connect(serial_number):
    DeviceManagerCLI.BuildDeviceList()
    motor = KCubeDCServo.CreateKCubeDCServo(serial_number)
    try:
        motor.Connect(serial_number)
        motor.StartPolling(1)
        motor.EnableDevice()
    except DeviceNotReadyException:
        print(f"unable to connect to {serial_number}, trying again")
        time.sleep(1)
        connect(serial_number)
    return motor

DeviceManagerCLI.BuildDeviceList()
deviceX = connect(serial_no1)
deviceY = connect(serial_no2)


if not deviceY.IsSettingsInitialized():
    deviceY.WaitForSettingsInitialized(10000)  # 10 second timeout
    assert deviceY.IsSettingsInitialized() is True
    
if not deviceX.IsSettingsInitialized():
    deviceX.WaitForSettingsInitialized(10000)  # 10 second timeout
    assert deviceX.IsSettingsInitialized() is True

# Before homing or moving device, ensure the motor's configuration is loaded
m_config = deviceY.LoadMotorConfiguration(serial_no1, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)
m_config = deviceX.LoadMotorConfiguration(serial_no2, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

m_config.DeviceSettingsName = "Z825B" # Chnage to whatever stage you are using. 

m_config.UpdateCurrentConfiguration()

deviceY.SetSettings(deviceY.MotorDeviceSettings, True, False)
deviceX.SetSettings(deviceX.MotorDeviceSettings, True, False)



vs = deviceX.GetVelocityParams()
print(vs.Acceleration)
print(vs.MaxVelocity)
vs.Acceleration = Decimal(4.0)
vs.MaxVelocity = Decimal(2.6)
vs.MinVelocity = Decimal(2.6)
deviceX.SetVelocityParams(vs)
deviceX.SetBacklash(Decimal(0))
vs = deviceX.GetVelocityParams()
#print(MotorDeviceSettings)
print(vs.Acceleration)
print(vs.MaxVelocity)
# print(dir(deviceX.AdvancedMotorLimits)) # use this!!!
print(deviceX.DevicePosition)
print(deviceX.Position)
print(deviceX)



settings = deviceX.MotorDeviceSettings
"""
for i in range(100):
    print(i)
    settings.JogMode = i
    print(settings.Jog.JogMode)

"""
deviceX.Home(50000)
deviceY.Home(50000)

settings.Jog.JogMode = JogParametersBase.JogModes.ContinuousHeld
settings.Jog.JogStopMode = JogParametersBase.StopModes.Immediate
print(settings.Jog.JogMode)
print(settings.Jog.JogStopMode)

deviceX.SetSettings(settings, True, False)
print(deviceX.MotorDeviceSettings.Jog.JogStopMode)
#print(deviceX.GetVelocityParams())
#deviceX.MoveTo(Decimal(10), 10000)
deviceX.SetJogStepSize(Decimal(1))
deviceX.SetJogVelocityParams(Decimal(2.6), Decimal(4))

print("checkpoint")
for i in [5, -3, 5, -2, 0.5, 0.1, -3, 0.02, 0.01, 0.03, 0.01, -2]:
    initial = deviceX.Position
    deviceX.SetJogStepSize(Decimal(i))
    print(deviceX.GetJogStepSize())

    print(deviceX.Status.IsJogging)
    print(deviceX.Status.IsMoving)
    isForward = True
    # try:
    #     deviceX.MoveJog(MotorDirection.Forward, 0)
    # except MoveToInvalidPositionException:
    #     deviceX.MoveJog(MotorDirection.Backward, 0)
    #     isForward = False
    
    relative_movement = Decimal(i)
    if relative_movement > Decimal(0):
        deviceX.MoveJog(MotorDirection.Forward, 0)
    elif relative_movement < Decimal(0):
        deviceX.MoveJog(MotorDirection.Backward, 0)
        isForward = False

    while not deviceX.Status.IsJogging:
        continue
    while deviceX.Status.IsJogging:
        travel = deviceX.Position - initial
        if isForward and travel >= relative_movement or not travel <= relative_movement:
        # if (deviceX.Position - initial) >= Decimal(i) or (deviceX.Position - initial) <= Decimal(-i):
            deviceX.StopImmediate()
            print("BROKEN")
            break
        continue
    while deviceX.Status.IsJogging:
        continue
    
    # print(deviceX.Position - initial)
    # print(deviceX.Position)



print("complete")
sys.exit()







# time.sleep(0.25)
# deviceY.StartPolling(250)
# deviceX.StartPolling(250)
# time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device
# deviceY.EnableDevice()
# deviceX.EnableDevice()
# time.sleep(0.25)  # Wait for device to enable

# if not deviceY.IsSettingsInitialized():
#     deviceY.WaitForSettingsInitialized(10000)  # 10 second timeout
#     assert deviceY.IsSettingsInitialized() is True
    
# if not deviceX.IsSettingsInitialized():
#     deviceX.WaitForSettingsInitialized(10000)  # 10 second timeout
#     assert deviceX.IsSettingsInitialized() is True

# # Before homing or moving device, ensure the motor's configuration is loaded
# m_config = deviceY.LoadMotorConfiguration(serial_no1,
# DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)
# m_config = deviceX.LoadMotorConfiguration(serial_no2,
# DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

# m_config = deviceY.LoadMotorConfiguration(serial_no1, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)
# m_config = deviceX.LoadMotorConfiguration(serial_no2, DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

# m_config.DeviceSettingsName = "Z825B" # Chnage to whatever stage you are using. 

# m_config.UpdateCurrentConfiguration()

# deviceY.SetSettings(deviceY.MotorDeviceSettings, True, False)
# deviceX.SetSettings(deviceX.MotorDeviceSettings, True, False)

# Set step size and velocity for jog for stage/motor (decimal max velocity, decimal acceleration)
# deviceY.SetJogStepSize(Decimal(.01))
# deviceY.SetJogVelocityParams(Decimal(0.1), Decimal(0.2))
# deviceX.SetJogStepSize(Decimal(.01))
# deviceX.SetJogVelocityParams(Decimal(0.1), Decimal(0.2))

#ORIGINAL VALUES 
# deviceY.SetJogStepSize(Decimal(1))
# deviceY.SetJogVelocityParams(Decimal(0.5), Decimal(1.0))
# deviceX.SetJogStepSize(Decimal(1))
# deviceX.SetJogVelocityParams(Decimal(0.5), Decimal(1.0))

#declare motor thread sleep 
ms = float(.4)

#declare LED ampere 
b = float(.01)

x_pos0 = math.sin(math.radians(0))
y_pos0 = math.sin(math.radians(90))


# Create sine wave
for i in range(360):
    x_pos = math.sin(math.radians(i))
    y_pos = math.sin(math.radians(i+90))
    
    if i == 0:
        x_pos1 = x_pos
        y_pos1 = y_pos
    
        
    
    x_pos2 = abs(x_pos-x_pos1)*2
    deviceX.SetJogStepSize(Decimal(x_pos2))
    deviceX.SetJogVelocityParams(Decimal(2.6), Decimal(4))
    y_pos2 = abs(y_pos-y_pos1)*2
    deviceY.SetJogStepSize(Decimal(y_pos2))
    print(x_pos, y_pos)
    deviceY.SetJogVelocityParams(Decimal(2.6), Decimal(4))
    if x_pos > 0:
        deviceX.MoveJog(MotorDirection.Forward, 0)     
    else:
        deviceX.MoveJog(MotorDirection.Backward, 0)
    if y_pos > 0:
        deviceY.MoveJog(MotorDirection.Forward, 0)
    else:
        deviceY.MoveJog(MotorDirection.Backward, 0)
     
    # time.sleep(3)
          #Get LED ready 
    
    print(x_pos2, y_pos2)    
    
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
            library.TLDC2200_setConstCurrent(devSession, ctypes.c_float(b))
     
     
      #Turn off LED
    library.TLDC2200_setLedOnOff(devSession, False)
    
    time.sleep(3)
    x_pos1 = x_pos
    y_pos1 = y_pos

    # else:
    #     deviceX.MoveJog(MotorDirection.Backward, 0)
    # if y_pos > 0:
    #     deviceY.MoveJog(MotorDirection.Forward, 0)
    # else:
    #     deviceY.MoveJog(MotorDirection.Backward, 0)
    
    # time.sleep(3)



