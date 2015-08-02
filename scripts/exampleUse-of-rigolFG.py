#!/usr/bin/env python2
# -*- encoding: UTF8 -*-

from pyoscilloskop import RigolFunctionGenerator, RigolError
import sys

try:
    fg = RigolFunctionGenerator()
except RigolError, e:
    print(e)
    sys.exit(1)

## Set up channel 1 to generate a sine wave with 10 Hz:
#fg.sine(10,1,1.4,-.5, 10)
## Generate an arbitrary function: a sinc function with 4000 samples
fg.arbitrary(RigolFunctionGenerator.getSinc(2**12), 100000)
## Generate an arbitrary function: a sin function with 4000 samples
#fg.arbitrary(RigolFunctionGenerator.getSin(2**12), 100000)
