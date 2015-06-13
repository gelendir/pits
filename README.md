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
 * python-levenshtein

dependencies can be installed with ```pip install -r requirements.txt```

Installation
------------

Install with setup.py:

    python setup.py install

Usage
-----

Start by finding out the name of your device:

    pits devices

Then start recording your beautiful composition:

    pits compose name-of-device

To stop recording press C8 (Highest C on a piano, the last note on the right)

By default, audio will be saved to ```audio.mp3```. You can change name of the
file with ```--audio=filepath```
