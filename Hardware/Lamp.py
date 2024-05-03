import ctypes
import os
import sys

# If you're using Python 3.7 or older change add_dll_directory to chdir
if sys.version_info < (3, 8):
    os.chdir(r"C:\Program Files\IVI Foundation\VISA\Win64\Bin")
else:
    os.add_dll_directory(r"C:\Program Files\IVI Foundation\VISA\Win64\Bin")


class Lamp:
    """
    Represents a lamp controlled by the TLDC2200 device.

    Attributes:
        library (ctypes.CDLL): The TLDC2200 library.
        dev_session (ctypes.c_int): The device session.
    """

    def __init__(self, serial_number):
        self.library = ctypes.cdll.LoadLibrary("TLDC2200_64.dll")

        # Connect to devices.
        # DC2200.
        # !!! In the USB number the serial number (M00...) needs to be changed to the one of the connected device.
        self.dev_session = ctypes.c_int()
        self.library.TLDC2200_init(serial_number, False, False, ctypes.byref(self.dev_session))
        print("Lamp connected.")

        # Constant Current (CC) mode
        # Make CC settings
        self.library.TLDC2200_setOperationMode(self.dev_session, 0)
        self.library.TLDC2200_setLedOnOff(self.dev_session, True)
        self.turn_off()
        
    def __del__(self):
        self.library.TLDC2200_setConstCurrent(self.dev_session, 0)
        self.library.TLDC2200_setLedOnOff(self.dev_session, False)
  
    def turn_on(self, led_ampere):
        """
        Turns on the lamp with the specified current.

        Args:
            led_ampere (float): The current in amperes to set for the lamp.
        """
        self.library.TLDC2200_setConstCurrent(self.dev_session, ctypes.c_float(led_ampere))
        
    def turn_off(self):
        """
        Turns off the lamp.
        """
        self.library.TLDC2200_setConstCurrent(self.dev_session, 0)
    
   