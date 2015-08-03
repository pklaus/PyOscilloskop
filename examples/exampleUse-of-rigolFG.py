#!/usr/bin/env python2
# -*- encoding: UTF8 -*-

import sys
import logging

from pyoscilloskop import RigolFunctionGenerator

## To get more debug output, do:
#logging.basicConfig(level=logging.DEBUG)

from universal_usbtmc.backends.linux_kernel import Instrument
dev_name = '/dev/usbtmc0'
device = Instrument(dev_name)

fg = RigolFunctionGenerator(device)

## Set up channel 1 to generate a sine wave with 10 Hz:
#fg.sine(10,1,1.4,-.5, 10)
## Generate an arbitrary function: a sinc function with 4000 samples
fg.arbitrary(RigolFunctionGenerator.getSinc(2**12), 100000)
## Generate an arbitrary function: a sin function with 4000 samples
#fg.arbitrary(RigolFunctionGenerator.getSin(2**12), 100000)
