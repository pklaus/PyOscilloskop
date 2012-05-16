# pyOscilloskop
#
# Copyright (19.2.2011) Sascha Brinkmann
#           (2012) Philipp Klaus
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

import os
import errno

class UsbTmcDriver:
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""
 
    def __init__(self, device):
        self.device = device
        try:
            self.FILE = os.open(device, os.O_RDWR)
        except OSError, e:
            if e.errno == errno.EACCES: raise PermissionError()
            if e.errno == errno.ENOENT: raise NoSuchFileError()
            raise UsbTmcError("unknown error: could not open the file %s: %s" % (device, e))
 
        # TODO: Test that the file opened
 
    def write(self, command):
        os.write(self.FILE, command);
 
    def read(self, length = 4000):
        return os.read(self.FILE, length)
 
    def getName(self):
        self.write("*IDN?")
        return self.read(300)
 
    def sendReset(self):
        self.write("*RST")

def getDeviceList():
    dirList=os.listdir("/dev")
    result=list()

    for fname in dirList:
        if(fname.startswith("usbtmc")):
            result.append("/dev/" + fname)

    return result

class UsbTmcError(Exception):
    pass

class PermissionError(UsbTmcError):
    pass

class NoSuchFileError(UsbTmcError):
    pass
