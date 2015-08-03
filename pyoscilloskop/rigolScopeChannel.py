# -*- encoding: UTF8 -*-
#
# pyOscilloskop
#
# Copyright (19.2.2011) Sascha Brinkmann
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

import numpy
import time

#This class has function to get informations about one channel. Instances of these class could be accessed by the class Rigol scope
class RigolScopeChannel:
    
    def __init__(self, rigolScope, channelName):
        self.rigolScope = rigolScope
        self.channelName = channelName
        
    def getVoltageScale(self):
        return self.rigolScope.getScopeInformationFloat(self.channelName, self.rigolScope.GET_SCALE)
        
    def getVoltageOffset(self):
        return self.rigolScope.getScopeInformationFloat(self.channelName, self.rigolScope.GET_OFFSET)
    
    def isChannelActive(self):
        return self.rigolScope.getScopeInformationInteger(self.channelName, self.rigolScope.GET_DISPLAY_ACTIVE) == 1

    def capture(self):
        self.rigolScope.strategy.getData(self.rigolScope, self.channelName)
        rawdata = self.rigolScope.read_raw(9000, wait_long=14.)
        time.sleep(50E-3)
        # remove first 10 bytes
        rawdata = rawdata[10:]
        data = numpy.frombuffer(rawdata, 'B')
        #assert data.min() >= 15 and data.max() <= 240
        voltscale = self.getVoltageScale()
        voltoffset = self.getVoltageOffset()
        data = (240. - data) * voltscale / 25 - voltoffset - voltscale * 4.6
        ret = {}
        ret['volt_samples'] = data
        ret['volt_offset'] = voltoffset
        ret['volt_scale'] = voltscale
        return ret

    def getData(self):
        return self.capture()['volt_samples']
