# pyOscilloskop
# -*- encoding: UTF8 -*-
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

import usbtmc
import rigolScopeChannel
import timeAxis
from rigolDevice import RigolDevice, RigolError, RigolUsageError
        
class RigolScope(RigolDevice):
    CHANNEL1 = "CHAN1"
    CHANNEL2 = "CHAN2"
    GET_TIME_SCALE = "TIM"
    GET_SCALE = "SCAL?"
    GET_OFFSET = "OFFS?"
    GET_DISPLAY_ACTIVE = "DISPlay?"

    """Class to control a Rigol DS1000 series oscilloscope"""
    def __init__(self, device = None):
        RigolDevice.__init__(self, device)

        self.channel1 = rigolScopeChannel.RigolScopeChannel(self, self.CHANNEL1);
        self.channel2 = rigolScopeChannel.RigolScopeChannel(self, self.CHANNEL2);        
        
    def getName(self):
        return self.dev.getIDN()

    def getDevice(self):
        return self.device
        
    def run(self):
        self.write(":RUN")
        
    def stop(self):
        self.write(":STOP")
        
    def reactivateControlButtons(self):
        self.write(":KEY:FORC")
    
    def getScopeInformation(self, channel, command, readBytes):
        self.write(":" + channel + ":" + command)
        return self.read(readBytes)
        
    def getScopeInformationFloat(self, channel, command):
        rawScopeInformation = self.getScopeInformation(channel, command, 20)
        floatScopeInformation = float(rawScopeInformation)
        return floatScopeInformation
    
    def getScopeInformationInteger(self, channel, command):
        rawScopeInformation = self.getScopeInformation(channel, command, 20)
        floatScopeInformation = int(rawScopeInformation)
        return floatScopeInformation
    
    def getScopeInformationString(self, channel, command, readBytes):
        return self.getScopeInformation(channel, command, readBytes)
        
    def getChannel1(self):
        return self.channel1
        
    def getChannel2(self):
        return self.channel2
        
    def getTimeScale(self):
        return self.getScopeInformationFloat(self.GET_TIME_SCALE, self.GET_SCALE)
        
    def getTimescaleOffset(self):
        return self.getScopeInformationFloat(self.GET_TIME_SCALE, self.GET_OFFSET)
        
    def getTimeAxis(self):
        return timeAxis.TimeAxis(self.getTimeScale())
