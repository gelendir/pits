PiTS
====

Piano-To-Speech

A small script I wrote under an hour for fun. Creates gibberish sentences by
converting the notes you play to random text and sends that to google's text-to-speech engine.

Prerequesites
-------------

Hardware:

 * A standard 75 key piano with support for MIDI
 * MIDI-to-USB plug, or something equivalent

Software:

 * python (2.7, 3.x)
 * mido
 * requests
 * click

dependencies can be installed with ```pip install -r requirements.txt```

Usage
-----

Start by finding out the name of your device:

    python main.py devices

Then start recording your beautiful composition:

    python main.py compose name-of-device path/to/audio.mp3

To stop recording press C8 (Highest C on a piano, the last note on the right)
