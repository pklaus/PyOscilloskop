PyOscilloskop
=============

This python library/application allows to control Rigol DS1000 / DS2000 series
oscilloscopes as well as the function generator DG1022.

It uses [universal_usbtmc][] for the communication with the device.
This allows to use different backends to connect to your device:

* RS232
* USBTMC:
  * Linux Kernel Driver
  * [python-usbtmc][]
* TCP Socket (via [rpi-usbtmc-gateway][])

Installation
------------

First, install *universal_usbtmc*

    pip install https://github.com/pklaus/universal_usbtmc/archive/master.zip

Then install *PyOscilloskop*

    pip install https://github.com/pklaus/PyOscilloskop/archive/master.zip

Depending on the backend you want to use, you may have to install additional software.
Read the [universal_usbtmc README file](https://github.com/pklaus/universal_usbtmc/blob/master/README.md) for more information.

Usage
-----

You can either use the Python package to automate measurements on your own or use the tools that ship
with this software:

* `pyoscilloskop-cli` - A CLI tool for the scopes
  Captures the current waveforms and displays them
  with Matplotlib (and/or saves them to an image file.
* `pyoscilloskop-web` - A web GUI for the scopes  
  Starts a web server allowing to display waveforms
  in the browser.

Examples of how to use the different backends with the tools:

To run the CLI tool with the *linux_kernel* backend, run:

    rigolCli.py --backend linux_kernel /dev/usbtmc0

To start the web server with the *tcp_socket* backend, connecting to the host 192.168.0.21, run:

    pyoscilloskop-web --backend tcp_socket 192.168.0.21

To run the CLI tool with the *python_usbtmc* backend and enable debug mode, run:

    rigolCli.py --backend python_usbtmc "USB::0x1ab1::0x0588::INSTR" --debug

To start the web server with the *pyserial* backend, using the serial device `/dev/ttyUSB0`
(don't forget to set your scope to 38400 baud!):

    pyoscilloskop-web --backend pyserial ASRL::/dev/ttyUSB0,38400::INSTR

Author
------

This software started as a fork of [sbrinkmann / PyOscilloskop](https://github.com/sbrinkmann/PyOscilloskop).

* Philipp Klaus (2012-2015)
* Sascha Brinkmann (2011)

Resources
---------

* [Rigol DS1052E – An Inexpensive DSO](http://blog.philippklaus.de/2013/04/rigol-ds1052e-an-inexpensive-dso/)
* [Rigol DG1022 Arbitrary Waveform Function Generator](http://blog.philippklaus.de/2012/05/rigol-dg1022-arbitrary-waveform-function-generator/)

[universal_usbtmc]: https://github.com/pklaus/universal_usbtmc
[python-usbtmc]: https://github.com/python-ivi/python-usbtmc
[rpi-usbtmc-gateway]: https://github.com/pklaus/rpi-usbtmc-gateway
