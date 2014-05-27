sound4python
============

A simple wrapper to play sounds from Python.

Current dependencies:
Python 2.6 or greater and
sox

This is a very simple wrapper to play audio by wrapping the sox binary.  Currently, audio playback of a 1D NumPy array and a list of numbers is supported.  This wrapper, in conjunction with a wrapped audio binary, fills a hole in the NumPy/SciPy suite to enable playback of a NumPy vector.  With minimal work, it also can play audio from a list/tuple of numbers.  This fact is why the project is called "sound4python" and not "sound4numpy".

The wrapper works by creating a wave file, and then playing that wave file via a command line subprocess.  The only tricky thing is that the wave file is stored in memory (RAM) using Python's tempfile.SpooledTemporaryFile so the data is never written to disk.  The current command line process is "sox - -d", which reads from its stdin, and writes to the default audio device.

This wrapper is released under a permissive license, though sox is released under a combination of GPL and LGPL depending upon the parts used.  I believe sound4python is wrapping a GPL portion of sox.  A different audio player could be used in place of sox fairly easily, but sox was chosen given it's relatively easy installation on Windows, Linux, and OS X.  See LICENSE.md for License for actual license.


Usage
=====

This version wraps the original code into a class that holds all information about the file to be played back. The playback is done in a separate thread. This allows to play, pause, stop and seek comfortably.

Basic usage
###########

Loading wav file and starting playback:

    from sound4python import sound4python as S4P
    wavPath = 'some.wav'
    s4p = S4P.Sound4Python()
    s4p.loadWav(wavPath)

    s4p.play()
    
Pause running playback:

    s4p.pause()
    
Resume playback from paused position:

    s4p.play()
    
Stop playback (reseting position to beginning):

    s4p.stop()
    
    
Seek in wavfile (seconds):

    s4p.seek(sec)

    
A word of warning:  **none of the internal operations are explictely threadsafe**. I intend to make it saver later.
