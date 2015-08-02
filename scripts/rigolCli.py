#!/usr/bin/env python
# -*- encoding: UTF8 -*-

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

import sys
import argparse
from time import strftime
import logging

import matplotlib.pyplot as plot

from pyoscilloskop import rigolScope
from pyoscilloskop import RigolDevice, RigolError, RigolUsageError, RigolTimeoutError

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--plot", "-p", action="store_false", help="Shows the window with the plot")
parser.add_argument("--hideChannel1", "-1", action="store_true", default=False, help="Hides Channel 1 in the plot")
parser.add_argument("--hideChannel2", "-2", action="store_true", default=False, help="Hides Channel 2 in the plot")
parser.add_argument("--informations", "-i", action="store_true", default=False, help="Prints scope informations")
parser.add_argument("--savePlot", "-s", metavar="filename", help="Saves the plot into a image")
parser.add_argument("--title", "-t", metavar="title", help="Set the title of the plot")
parser.add_argument("--hideDate", "-d", action="store_true", default=False, help="Hides the date in the plot")
parser.add_argument("--restart", "-r", action="store_true", default=False, help="Restart require after plot")
parser.add_argument("device", default="/dev/usbtmc0", nargs="?", help="The usbtmc device to connect to.")

args = parser.parse_args()

"""Initialize our scope"""

try:
    scope = rigolScope.RigolScope(args.device)
except RigolError as e:
    print(e)
    sys.exit(1)


if args.informations:
    print("Device: ", choosenDevice)
    print("Name: ", scope.getName())
    
    print("Channel 1 - Active: ", scope.getChannel1().isChannelActive())
    print("Channel 1 - Voltage scale: ", scope.getChannel1().getVoltageScale(), "V/div")
    print("Channel 1 - Voltage offset: ", scope.getChannel1().getVoltageOffset(), "V")
    
    print("Channel 2 - Active: ", scope.getChannel2().isChannelActive())
    print("Channel 2 - Voltage scale: ", scope.getChannel2().getVoltageScale(), "V/div")
    print("Channel 2 - Voltage offset: ", scope.getChannel2().getVoltageOffset(), "V")
    
    print("Timescale: ", scope.getTimeScale(), "sec/div")
    print("Timescale offset: ", scope.getTimescaleOffset(), "sec")

"""You have to reactivate the keys on the scope after every access over the usb interface"""
scope.reactivateControlButtons()

def fillPlot(options):
    channel1Data = scope.getChannel1().getData();
    channel1Data = channel1Data[0:600:1]
    
    channel2Data = scope.getChannel2().getData();
    channel2Data = channel2Data[0:600:1]

    time = scope.getTimeAxis();
    
    timeAxis = time.getTimeAxis()
    
    if (not(options.hideChannel1) and scope.getChannel1().isChannelActive()):
        plot.plot(timeAxis, channel1Data)
    if (not(options.hideChannel2) and scope.getChannel2().isChannelActive()):
        plot.plot(timeAxis, channel2Data)
    title = "Oscilloskop"
    if options.title != None:
        title = options.title
    if options.hideDate == False:
        title = title + " (" + strftime("%Y-%m-%d %H:%M:%S") + ")"
    plot.title(title)
    plot.ylabel("Voltage (V)")
    plot.xlabel("Time (" + time.getUnit() + ")")
    plot.xlim(timeAxis[0], timeAxis[599])

if args.savePlot != None or args.plot != None:
    fillPlot(args)
    
if args.restart:
    scope.run()
    
scope.reactivateControlButtons()

if args.savePlot != None:
    print("Save plot to: ", args.savePlot)
    plot.draw()
    plot.savefig(args.savePlot)

if args.plot != None:
        """Plot the data"""
        plot.show()
