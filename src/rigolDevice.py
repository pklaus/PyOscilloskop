# -*- encoding: UTF8 -*-
#
# pyOscilloskop
#
# Copyright (2012) Philipp Klaus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import usbtmc
import time
import errno

class RigolDevice(object):
    ## defaults for device dependent settings
    SLEEP_AFTER_WRITE = 0.01 # ← needed to give the device some time to commit changes
    SLEEP_MS_PER_CHAR = 0.2 # ← needed for long commands

    ## min debug level to print debug information:
    DEBUG_CATEGORIES = {
      "RIGOL_WRITE": 4,
      "RIGOL_READ" : 4
    }

    debugLevel = 1

    """Class to control a Rigol device such as
       a DS1000 series oscilloscope
       or a DG1022 function generator."""
    def __init__(self, device = None):
        if device:
            self.device = device
        else:
            listOfDevices = usbtmc.getDeviceList()
            if(len(listOfDevices) == 0):
                raise RigolError("There is no USBTMC device to access. Make sure " \
                  "the device is connected and switched on. You can check if the " \
                  "operating system detected it by running `dmesg`.")
            self.device = listOfDevices[0]
        try:
            self.dev = usbtmc.UsbTmcDriver(self.device)
        except usbtmc.PermissionError:
            raise RigolError( "Please adjust the permissions of the file " \
              "%s to allow regular users to read and write to it ('chmod 777 %s') " \
              "or run this software as superuser (not recommended)." % (self.device, self.device) )
        except usbtmc.NoSuchFileError:
            raise RigolError( "You tried to access the USBTMC device %s which doesn't "\
              "exist in your system. Make sure it's plugged in and detected by your " \
              "operating sytem by running `dmesg`." % self.device )

    def debug(self, message, debugClass):
        if self.debugLevel >= self.DEBUG_CATEGORIES[debugClass]:
            if len(message) < 60: print message
            else: print message[0:50], " ... ", message[-10:]
 
    def write(self, command):
        """Send a command directly to the device"""
        self.debug(command, "RIGOL_WRITE")
        self.dev.write(command)
        time.sleep( self.SLEEP_AFTER_WRITE )
        if len(command) > 20:
            time.sleep( self.SLEEP_MS_PER_CHAR * 0.001 * len(command) )
 
    def read(self, length = 4000):
        """Read a from the device"""
        try:
            response = self.dev.read(length)
        except OSError, e:
            if e.errno == errno.ETIMEDOUT: raise RigolTimeoutError()
            else: raise e
        self.debug(response, "RIGOL_READ")
        return response

    def reset(self):
        """Reset the device"""
        self.dev.sendReset()

class RigolError(Exception):
    pass

class RigolUsageError(RigolError):
    pass

class RigolTimeoutError(RigolError):
    pass
