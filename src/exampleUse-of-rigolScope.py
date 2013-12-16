#!/usr/bin/env python2
# -*- encoding: UTF8 -*-

from rigolScope import RigolScope
from rigolDevice import RigolError

import sys

try:
    scope = RigolScope()
except RigolError, e:
    print e
    sys.exit(1)

## To get more debug output, do:
#scope.debugLevel = 5

channel1Data = scope.getChannel1().getData();
channel2Data = scope.getChannel2().getData();
print("{0} values received for channel 1.".format(len(channel1Data)))
print("{0} values received for channel 2.".format(len(channel2Data)))

scope.reactivateControlButtons()

scope = None
