sound4python
============

A simple wrapper to play sounds from Python.

Current dependencies:
sox

This is a very simple wrapper to play audio by wrapping the sox binary.  Currently, audio playback of a 1D NumPy array and a list of numbers is supported.  

This wrapper is released under a permissive, though sox is released under a combination of GPL and LGPL depending upon the parts used.  I believe sound4python is wrapping a GPL portion of sox.  A different audio player could be used in place of sox fairly easily, but sox was chosen given it's relatively easy installation on Windows, Linux, and OS X.  See LICENSE.md for License for actual license.


