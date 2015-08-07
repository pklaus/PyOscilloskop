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

import matplotlib.pyplot as plt

from pyoscilloskop import rigolScope
from pyoscilloskop import RigolDevice, RigolError, RigolUsageError, RigolTimeoutError

from universal_usbtmc import import_backend
from universal_usbtmc import UsbtmcError, UsbtmcPermissionError, UsbtmcNoSuchFileError

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("--hide-plot", "-p", action="store_true", help="Don't show the window with the plot")
parser.add_argument("--hide-channel-1", "-1", action="store_true", default=False, help="Hides Channel 1 in the plot")
parser.add_argument("--hide-channel-2", "-2", action="store_true", default=False, help="Hides Channel 2 in the plot")
parser.add_argument("--information", "-i", action="store_true", default=False, help="Prints scope information")
parser.add_argument("--save-plot", "-s", metavar="filename", help="Saves the plot into a image")
parser.add_argument("--title", "-t", metavar="title", help="Set the title of the plot")
parser.add_argument("--hide-date", "-d", action="store_true", default=False, help="Hides the date in the plot")
parser.add_argument("--restart", "-r", action="store_true", default=False, help="Restart require after plot")
parser.add_argument("--debug", action="store_true", help="Enable debugging output")
parser.add_argument("--backend", default="linux_kernel", help="The universal_usbtmc backend to use.")
parser.add_argument("device", default="/dev/usbtmc0", nargs="?", help="The usbtmc device to connect to.")

args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)

"""Initialize our scope"""

backend = import_backend(args.backend)

try:
    device = backend.Instrument(args.device)
except UsbtmcError as e:
    print('{0} {1}'.format(e.__class__.__name__, e))
    sys.exit(1)

try:
    scope = rigolScope.RigolScope(device)
except RigolError as e:
    print(e)
    sys.exit(1)


if args.information:
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

def fill_plot(options):
    channel_1_data = scope.get_channel_1().get_data();
    channel_2_data = scope.get_channel_2().get_data();
    time = scope.get_time_axis();
    time_axis = time.get_time_axis()
    
    if (not(options.hide_channel_1) and scope.get_channel_1().is_channel_active()):
        plt.plot(time_axis, channel_1_data)
    if (not(options.hide_channel_2) and scope.get_channel_2().is_channel_active()):
        plt.plot(time_axis, channel_2_data)
    title = "Oscilloskop"
    if options.title != None:
        title = options.title
    if options.hide_date == False:
        title = title + " (" + strftime("%Y-%m-%d %H:%M:%S") + ")"
    plt.title(title)
    plt.ylabel("Voltage (V)")
    plt.xlabel("Time (" + time.get_unit() + ")")
    plt.xlim(time_axis[0], time_axis[599])

if args.save_plot or not args.hide_plot:
    fill_plot(args)
    
if args.restart:
    scope.run()
    
scope.reactivate_control_buttons()

if args.save_plot != None:
    print("Save plot to: ", args.save_plot)
    plt.draw()
    plt.savefig(args.save_plot)

if not args.hide_plot:
        """Plot the data"""
        plt.show()
