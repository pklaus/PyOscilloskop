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

import time

from . import rigol_scope_channel
from . import time_axis
from .rigol_device import RigolDevice, RigolError, RigolUsageError
        
class ScopeStrategy:
    pass

class DS1000Strategy(ScopeStrategy):
    def getData(self, scope, channel):
        scope.write(":WAV:POIN:MODE NOR")
        scope.write(":WAV:DATA? " + channel)

class DS2000Strategy(ScopeStrategy):
    def getData(self, scope, channel):
        scope.write(":WAV:POIN:MODE MAX")
        scope.write(":WAV:SOUR " + channel)
        scope.write(":WAV:DATA?")

class RigolScope(RigolDevice):
    """Class to control a Rigol DS1000/DS2000 series oscilloscope"""

    CHANNEL1 = "CHAN1"
    CHANNEL2 = "CHAN2"
    GET_TIME_SCALE = "TIM"
    GET_SCALE = "SCAL?"
    GET_OFFSET = "OFFS?"
    GET_DISPLAY_ACTIVE = "DISPlay?"
    strategies = {}
    strategies["DS1"] = DS1000Strategy()
    strategies["DS2"] = DS2000Strategy()

    def __init__(self, device = None):

        RigolDevice.__init__(self, device)
        try:
            device.message_delay = 0.02
        except:
            pass
        self.strategy = RigolScope.strategies[self.getModel()[:3]]
        self.channel1 = rigol_scope_channel.RigolScopeChannel(self, self.CHANNEL1);
        self.channel2 = rigol_scope_channel.RigolScopeChannel(self, self.CHANNEL2);        
        
    def get_name(self):
        return self.dev.idn

    def get_model(self):
        return self.get_name().split(",")[1]

    def get_device(self):
        return self.device
        
    def run(self):
        self.write(":RUN")
        
    def stop(self):
        self.write(":STOP")
        
    def reactivate_control_buttons(self):
        self.write(":KEY:FORC")
    
    def get_scope_information(self, channel, command, read_bytes):
        self.write(":" + channel + ":" + command)
        return self.read(read_bytes)
        
    def get_scope_information_float(self, channel, command):
        raw_scope_information = self.get_scope_information(channel, command, 30)
        float_scope_information = float(raw_scope_information)
        return float_scope_information
    
    def get_scope_information_integer(self, channel, command):
        raw_scope_information = self.get_scope_information(channel, command, 30)
        int_scope_information = int(raw_scope_information)
        return int_scope_information
    
    def get_scope_information_string(self, channel, command, readBytes):
        return self.get_scope_information(channel, command, readBytes)
        
    def get_channel_1(self):
        return self.channel1
        
    def get_channel_2(self):
        return self.channel2
        
    def get_time_scale(self):
        return self.get_scope_information_float(self.GET_TIME_SCALE, self.GET_SCALE)
        
    def get_timescale_offset(self):
        return self.get_scope_information_float(self.GET_TIME_SCALE, self.GET_OFFSET)
        
    def get_time_axis(self):
        return time_axis.TimeAxis(self.get_time_scale())
