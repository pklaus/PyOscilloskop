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
import re

# The class RigolFunctionGenerator is able to control the
# function generator Rigol DG1022. Read more on
# http://blog.philippklaus.de/2012/05/rigol-dg1022-arbitrary-waveform-function-generator/

DG1022_SLEEP_AFTER_WRITE = 0.01
VALID_RESPONSES = {
  '*IDN?' : {
    'full': r'(?P<manufacturer>[a-zA-Z0-9 ]+),(?P<model>[a-zA-Z0-9 ]+),(?P<serial>[A-Z0-9]+),(),(?P<edition>[0-9\.]+)',
    'groups' : {
      'manufacturer' : 'RIGOL TECHNOLOGIES',
      'model' : 'DG1022 '
    }
  },
  '*IDN?____' : r'(RIGOL TECHNOLOGIES),(DG1022 ),(DG1D135208595),(),(00.03.00.08.00.02.08)'
}
DEBUG = {
  'RIGOL_WRITE' : 1,
  'RIGOL_READ'  : 1,
}

class RigolFunctionGenerator:
    """Class to control a Rigol DS1000 series oscilloscope"""
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
            self.meas = usbtmc.UsbTmcDriver(self.device)
        except usbtmc.PermissionError:
            raise RigolError( "Please adjust the permissions of the file " \
              "%s to allow regular users to read and write to it ('chmod 777 %s') " \
              "or run this software as superuser (not recommended)." % (self.device, self.device) )
        except usbtmc.NoSuchFileError:
            raise RigolError( "You tried to access the USBTMC device %s which doesn't "\
              "exist in your system. Make sure it's plugged in and detected by your " \
              "operating sytem by running `dmesg`." % self.device )

        self.debugLevel = 10
 
        self.name = self.meas.getName()
        print self.name

    def debug(self, message, debugClass):
        debugLevel = DEBUG[debugClass]
        if debugLevel >= self.debugLevel:
            print message
 
    def write(self, command):
        """Send an arbitrary command directly to the scope"""
        debug(command, D_RIGOL_WRITE)
        self.meas.write(command)
        time.sleep( DG1022_SLEEP_AFTER_WRITE )
 
    def read(self, command):
        """Read an arbitrary amount of data directly from the scope"""
        return self.meas.read(command)

    def reset(self):
        """Reset the instrument"""
        self.meas.sendReset()

    def sine(self, frequency, channel=1, voltage=1, offset=0, phase=0):
        self.write("FUNC SIN")
        self.write("FREQ %d" % frequency)
        self.write("VOLT:UNIT VPP")
        self.write("VOLT %.3f" % voltage)
        self.write("VOLT:OFFS %.3f" % offset)
        self.write("PHAS %d" % phase)
        self.activate(channel)

    def activate(self, channel=1):
        channel = self.validateChannelNumber(channel)
        self.write("OUTP%s ON" % channel)

    @staticmethod
    def validate(request, response):
        m = re.match( VALID_RESPONSES[request]['full'], response)
        if not m:
            raise RigolError('Response "%s" for the request "%s" was not expected and may be invalid.' % (response, request) )
        for group in VALID_RESPONSES[request]['groups'].keys():
            matched_string = m.groupdict()[group]
            g = re.match( VALID_RESPONSES[request]['groups'][group], matched_string )
            if not g:
                raise RigolError('This software does not yet support products with %s as %s name so far.' % (matched_string, group) )
        return m.groupdict()

    def validateChannelNumber(self, channel):
        if channel not in [1,2]:
            raise RigolUsageError("Only channels 1 and 2 are valid")
        return ":CH2" if channel == 2 else ""

class RigolError(Exception):
    pass

class RigolUsageError(RigolError):
    pass

class RigolProgramming(RigolError):
    pass

