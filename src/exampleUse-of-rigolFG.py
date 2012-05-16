#!/usr/bin/env python2

import rigolFG
import sys

try:
    fg = rigolFG.RigolFunctionGenerator()
except rigolFG.RigolError, e:
    print e
    sys.exit(1)

fg.sine(10,1,1.4,-.5, 10)
