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
import errno
import logging


logger = logging.getLogger(__name__)

class RigolDevice(object):
    ## defaults for device dependent settings
    SLEEP_AFTER_WRITE = 0.01 # ← needed to give the device some time to commit changes
    SLEEP_MS_PER_CHAR = 0.2 # ← needed for long commands

    """Class to control a Rigol device such as
       a DS1000 series oscilloscope
       or a DG1022 function generator."""
    def __init__(self, device):
        """ device needs to be a universal_usbtmc.Instrument """
        self.dev = device

    def write(self, command):
        """Send a command directly to the device"""
        #logger.debug("RIGOL_WRITE " + str(command) )
        try:
            self.dev.write(command)
        except OSError as e:
            raise RigolError("Couldn't communicate with the scope: " + str(e))
        time.sleep( self.SLEEP_AFTER_WRITE )
        if len(command) > 20:
            time.sleep( self.SLEEP_MS_PER_CHAR * 0.001 * len(command) )
 
    def read(self, length = 4000):
        """Read text data from the device"""
        binary_response = self.read_raw(length)
        try:
            return binary_response.decode('ascii')
        except Exception as e:
            raise RigolError('Could not decode this message:\n' + str(e))


    def read_raw(self, length = 4000):
        """Read binary data from the device"""
        try:
            response = self.dev.read_raw(length)
        except OSError as e:
            if e.errno == errno.ETIMEDOUT: raise RigolTimeoutError()
            else: raise e
        #logger.debug("RIGOL_READ " + str(response))
        return response

    def reset(self):
        """Reset the device"""
        self.dev.sendReset()

    def __del__(self):
        try: self.dev = None
        except: pass

class RigolError(Exception):
    pass

class RigolUsageError(RigolError):
    pass

class RigolTimeoutError(RigolError):
    pass
