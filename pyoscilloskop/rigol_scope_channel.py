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
    
    def __init__(self, scope, channel_name):
        self.scope = scope
        self.channel_name = channel_name
        
    def get_voltage_scale(self):
        return self.scope.get_scope_information_float(self.channel_name, self.scope.GET_SCALE)
        
    def get_voltage_offset(self):
        return self.scope.get_scope_information_float(self.channel_name, self.scope.GET_OFFSET)
    
    def is_channel_active(self):
        return self.scope.get_scope_information_integer(self.channel_name, self.scope.GET_DISPLAY_ACTIVE) == 1

    def capture(self):

        voltscale = self.get_voltage_scale()
        voltoffset = self.get_voltage_offset()

        self.scope.strategy.get_data(self.scope, self.channel_name)
        rawdata = self.scope.read_raw(9000, timeout=14.)
        time.sleep(50E-3)
        # remove first 10 bytes
        rawdata = rawdata[10:]
        data = numpy.frombuffer(rawdata, 'B')
        #assert data.min() >= 15 and data.max() <= 240
        data = (240. - data) * voltscale / 25 - voltoffset - voltscale * 4.6

        ret = {}
        ret['volt_samples'] = data
        ret['volt_offset'] = voltoffset
        ret['volt_scale'] = voltscale

        return ret

    def get_data(self):
        return self.capture()['volt_samples']
