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

# The class RigolFunctionGenerator is able to control the
# function generator Rigol DG1022. Read more on
# http://blog.philippklaus.de/2012/05/rigol-dg1022-arbitrary-waveform-function-generator/

class RigolFunctionGenerator:
    """Class to control a Rigol DS1000 series oscilloscope"""
    def __init__(self, device = None):
        if(device == None):
            listOfDevices = usbtmc.getDeviceList()
            if(len(listOfDevices) == 0):
                raise ValueError("There is no device to access")
    
            self.device = listOfDevices[0]
        else:
            self.device = device

        self.meas = usbtmc.UsbTmcDriver(self.device)
 
        self.name = self.meas.getName()
        print self.name
 
    def write(self, command):
        """Send an arbitrary command directly to the scope"""
        self.meas.write(command)
 
    def read(self, command):
        """Read an arbitrary amount of data directly from the scope"""
        return self.meas.read(command)
 
    def reset(self):
        """Reset the instrument"""
        self.meas.sendReset()
