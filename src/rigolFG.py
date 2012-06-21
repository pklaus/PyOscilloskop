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
import re
from math import sin
from rigolDevice import RigolDevice, RigolError, RigolUsageError, RigolTimeoutError

# The class RigolFunctionGenerator is able to control the
# function generator Rigol DG1022. Read more on
# http://goo.gl/byJvk

class RigolFunctionGenerator(RigolDevice):
    ### device dependent constatants:
    SLEEP_AFTER_WRITE = 0.01 # ← needed to give the device some time to commit changes
    SLEEP_MS_PER_CHAR = 0.2 # ← needed for long commands such as DATA:DAC VOLATILE,...
    FUNCTIONS = {"SIN": "SINusoid", "SQU": "SQUare", "RAMP": "RAMP", "PULS": "PULSe", "NOIS": "NOISe", "DC": "DC", "USER": "USER"}
    DAC_MIN = 0
    DAC_MAX = 2**14-1 # 14 bit precision: 0-16383
    MAX_DAC_VALUES = 2**12
    MAX_DAC_VALUES_AT_ONCE = 512

    ## valid responses for commands sent to the function generator:
    VALID_RESPONSES = {
      '*IDN?': {
        'full': r'(?P<manufacturer>[a-zA-Z0-9 ]+),(?P<model>[a-zA-Z0-9 ]+),(?P<serial>[A-Z0-9]+),(),(?P<edition>[0-9\.]+)',
        'groups' : {
          'manufacturer' : 'RIGOL TECHNOLOGIES',
          'model' : 'DG1022 '
        }
      },
      'SYSTem:ERRor?': {
        'full': r'(?P<errno>[+-][0-9]+),"(?P<errdesc>[a-zA-Z0-9 ]+)"'
      }
    }

    """Class to control a Rigol DS1000 series oscilloscope"""
    def __init__(self, device = None):
        RigolDevice.__init__(self, device)
        
        # check identification
        idn = self.dev.getIDN()
        info = RigolFunctionGenerator.validate('*IDN?', idn)
        print("Discovered a %s from %s." % (info["model"], info["manufacturer"]))
        self.lock()

    def __del__(self):
        try:
            if self.debugLevel > 0:
                ## Get errors from the device and print them before quitting the program.
                errors = self.clearErrors()
                if errors:
                    print('The DG1022 reported problems:')
                    for error in errors: print('"%s" (error number %d)' % (error[1], error[0]))
            self.unlock()
        except:
            pass

    def lock(self):
        ## Lock the front panel knobs and illuminate "Local" knob (manual p. 2-65)
        #self.write("SYSTem:RWLock") # ← also lock the "Local" knob
        self.write("SYSTem:REMote") # ← don't lock the "Local" knob

    def unlock(self):
        ## reactivate the front panel knobs (manual p. 2-65)
        self.write("SYSTem:LOCal")

    def clearError(self):
        """ Fetches error messages from the device and clears them from the queue.

          Some known error messages:
          +0,"No Error"                        Returned when everything is fine.
          -116,"Program mnemonic too long"
          -113,"Parameter not allowed"         Happens when sending more than 2^12 DAC values.
        """
        self.write("SYSTem:ERRor?")
        try:
            response = self.read()[:-1] # the subselection removes the trailing newline char
        except RigolTimeoutError:
            # a timeout seems to happen when the error queue just got empty
            return None
        if response == '+0,"No Error"': return None
        response = RigolFunctionGenerator.validate("SYSTem:ERRor?", response)
        return (int(response['errno']), response['errdesc'])

    def clearErrors(self):
        error = self.clearError()
        if not error: return None
        errors = []
        while error:
            errors.append(error)
            error = self.clearError()
        return errors

    def setDisplayLuminance(self, luminance = 5):
        ## Display backlight brightness (manual p. 2-69)
        ## The manual says the values can be between 0 and 31, but 0 seems to be invalid.
        if luminance not in range(1,32):
            raise RigolUsageError("The display luminance has to be in the limits of 1-31!")
        self.write("DISPlay:LUMInance %d" % luminance)

    def setDisplayContrast(self, contrast = 5):
        ## Display contrast (manual p. 2-69)
        if contrast not in range(0,32):
            raise RigolUsageError("The display contrast has to be in the limits of 0-31!")
        self.write("DISPlay:CONTRAST %d" % contrast)

    def setClockSource(self, internal = True):
        """ Set the clock source of the function generator
          either to internal or to external.
          When setting to the external source,
          the back 10MHz connector has to be used. (p.2-66 of the manual) """
        self.write("SYSTem:CLKSRC " + ("INT" if internal else "EXT") )

    def activate(self, channel=1):
        channel = self.validateChannelNumber(channel)
        self.write("OUTP%s ON" % channel)

    def arbitrary(self, sequence, frequency, channel=1, voltage_high=4, voltage_low=-4):
        if len(sequence) > self.MAX_DAC_VALUES:
            raise RigolUsageError("Only %d samples possible on the DG1022. Tried %d." %
              (self.MAX_DAC_VALUES, len(sequence) ) )
        sequence = RigolFunctionGenerator.rescale(sequence, self.DAC_MIN, self.DAC_MAX)
        if min([type(item) is int for item in sequence]) == False:
            raise RigolUsageError('The sequence must contain integers only.')
        if min(sequence) < self.DAC_MIN or max(sequence) > self.DAC_MAX:
            raise RigolUsageError('The sequence must contain integers between 0 and 16383.')
        self.write("OUTP OFF")
        self.write("FUNC USER")
        self.write("FREQ %d" % frequency)
        self.write("VOLT:UNIT VPP")
        #self.write("VOLT %.3f" % voltage)
        #self.write("VOLT:OFFS %.3f" % offset)
        self.write("VOLT:HIGH %.1f" % voltage_high)
        self.write("VOLTage:LOW %.1f" % voltage_low)
        self.write("DATA:DELete VOLATILE")
        #MAX = self.MAX_DAC_VALUES_AT_ONCE
        #for i in range(0, len(sequence)/MAX + ( 1 if len(sequence) % MAX > 0 else 0)):
        #    self.write("DATA:DAC VOLATILE,%s" % ",".join([str(item) for item in sequence[i * MAX : i*MAX+MAX]]))
        self.write("DATA:DAC VOLATILE,%s" % ",".join([str(item) for item in sequence]))
        self.write("FUNC:USER VOLATILE")
        self.activate(channel)

    def sine(self, frequency, channel=1, voltage=1, offset=0, phase=0):
        self.write("FUNC SIN")
        self.write("FREQ %d" % frequency)
        self.write("VOLT:UNIT VPP")
        self.write("VOLT %.3f" % voltage)
        self.write("VOLT:OFFS %.3f" % offset)
        self.write("PHAS %d" % phase)
        self.activate(channel)

    @staticmethod
    def validate(request, response):
        m = re.match( RigolFunctionGenerator.VALID_RESPONSES[request]['full'], response)
        if not m:
            raise RigolError('Response "%s" for the request "%s" was not expected and may be invalid.' % (response, request) )
        if not 'groups' in RigolFunctionGenerator.VALID_RESPONSES[request].keys(): return m.groupdict()
        for group in RigolFunctionGenerator.VALID_RESPONSES[request]['groups'].keys():
            matched_string = m.groupdict()[group]
            g = re.match( RigolFunctionGenerator.VALID_RESPONSES[request]['groups'][group], matched_string )
            if not g:
                raise RigolError('This software does not yet support products with %s as %s name so far.' % (matched_string, group) )
        return m.groupdict()

    def validateChannelNumber(self, channel):
        if channel not in [1,2]:
            raise RigolUsageError("Only channels 1 and 2 are valid")
        return ":CH2" if channel == 2 else ""

    @staticmethod
    def rescale(seq, low, high):
        cur_low = min(seq)
        # shift the sequence to positive values
        if cur_low < 0.0: seq = [val - cur_low for val in seq]
        cur_low = min(seq)
        cur_high = max(seq)
        ## rescale the values (multiplication with 0.999 seems to be necessary due to float inaccuracies).
        seq = [int(val*(high-low)*0.999/(cur_high-cur_low)) for val in seq]
        if min(seq) < low or max(seq) > high:
            print(seq)
            raise NameError("Something went wrong when rescaling values: min: %d, max: %d." % (min(seq), max(seq)))
        return seq

    @staticmethod
    def getSin(samples, periods = 1):
        ## create a list containing  0, 1, 2, ... , samples-1
        sequence = range(0,samples)
        ## rescale the list to values from 0 to 1
        sequence = [x/float(samples) for x in sequence]
        ## create a sine function
        sequence = [sin(x*2*3.14*periods) for x in sequence]
        return sequence
    
    @staticmethod
    def getSinc(samples, periods = 10):
        ## create a list containing  -samples/2, -samples/2+1, ..., -1, 0, 1, ... , samples/2-2, samples/2-1
        sequence = range(-samples/2,samples/2)
        ## rescale the list to values from -0.5 to .5
        sequence = [x/float(samples) for x in sequence]
        ## protect against division by 0 and scale to periods:
        sequence = [(x+0.0001/float(samples))*2*3.14*periods for x in sequence]
        ## calculate sin(x)/x
        sequence = [sin(x)/x for x in sequence]
        return sequence


