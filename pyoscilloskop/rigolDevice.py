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

import time
import logging

logger = logging.getLogger(__name__)

class RigolDevice(object):
    """Class to control a Rigol device such as
       a DS1000 series oscilloscope
       or a DG1022 function generator."""

    def __init__(self, device):
        """ device needs to be a universal_usbtmc.Instrument """
        self.dev = device

    def write(self, *args, **kwargs):
        """Send a command directly to the device"""
        self.dev.write(*args, **kwargs)
 
    def read(self, *args, **kwargs):
        """Read text data from the device"""
        return self.dev.read(*args, **kwargs)

    def read_raw(self, *args, **kwargs):
        """Read binary data from the device"""
        return self.dev.read_raw(*args, **kwargs)

    def reset(self):
        """Reset the device"""
        self.dev.write("*RST")

class RigolError(Exception):
    pass

class RigolUsageError(RigolError):
    pass

class RigolTimeoutError(RigolError):
    pass
