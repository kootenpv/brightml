
.. raw:: html

  <p align="center">
      <a href="#" target="_blank"><img src="./resources/logo.png"></a>
  </p>

brightml: Machine-Learned Auto brightness
=========================================

.. image:: https://img.shields.io/pypi/v/brightml.svg
    :target: https://pypi.python.org/pypi/brightml

.. image:: https://img.shields.io/pypi/l/brigtml.svg
    :target: https://pypi.python.org/pypi/brightml

.. image:: https://img.shields.io/pypi/wheel/brightml.svg
    :target: https://pypi.python.org/pypi/brightml

.. image:: https://img.shields.io/pypi/pyversions/brightml.svg
    :target: https://pypi.python.org/pypi/brightml

The goal of this package is to automatically manage brightness on laptops, with "zero config"; using machine learning.
Some do not even realise that what is "on" your screen, matters. White screens (like browser) vs coding (in black) should be accounted for.

All you have to do is to change brightness when it is not good enough yet; **brightml** learns.

It will learn to generalize based on your personal needs. To do this, it uses:

- Brightness of screen
- Ambient light sensor (if available)
- Hour of day
- whereami (indoor wifi positioning)
- Battery feature (only if discharging)
- Active application name
- Active window title

Features
--------

- Cross-OS (within Linux)
- Cross-vendor (intel, nvidia)
- Cross-hardware (with or without ambient light sensor, linux on macbook works)
- Seamless integration: No need to change key bindings as it monitors brightness change by user
- Uses asyncio, event-based (change of window immediately triggers prediction; no timer)

Goals
-----
- Provide service files to enable by startup (systemd: done)
- Add a command to show "feature importance"
- More extensibility (plugin based)
- Cross-platform (OSX)

Installation
------------

::

    pip install brightml

Bonus: set up `whereami <https://github.com/kootenpv/whereami>`_ to include indoor positioning in the predictions.

::

    pip install brightml[whereami]

Usage
-----

Eventually we need to get some service files for the different Operating Systems, so the process starts on boot.

For now, just ready for preview, run on command line:

::

    sudo brightml
