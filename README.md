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


Generating stats on note frequencies
====================================

As part of my ongoing exploration on how to make the sounds produced by PiTS
more interesting, I have written small utilities to help me analyze the
frequencies of notes played on a piano. Here I briefly explain what to do if you
would like to reproduce my results

Main steps to follow:

1. Find a catalog of piano scores to analyze
2. Download all scores
3. Generate statistics on note frequencies for each score
4. Combine all statistics together

There are 2 scripts for accomplishing these steps: ```pits_scrape``` and ```pits_stats```

Finding a catalog
-----------------

First, you need to create somehow a catalog of scores to download and analyze.
For now, ```pits_scrape``` only understands how to produce and download catalogs
from [The Mutopia Project](http://www.mutopiaproject.org). 

Start by [Searching](http://www.mutopiaproject.org/advsearch.html) for the
scores you want and download the resulting HTML page to a file. After that
you can use ```pits_scrape``` to automatically generate a JSON catalog:

    #make a directory that will contain the catalog and all the scores
    mkdir mutopia
    pits_scrape scrape search.html -o mutopia/catalog.json

Download all scores
-------------------

***WARNING: In an effort to conserve the limited bandwidth of the Mutopia 
Project, consider using a mirror to download scores instead of scraping the 
main website***

Download the catalog with the following command:

    pits_scrape download mutopia/catalog.json -o mutopia

Generate statistics
-------------------

Once everything has been downloaded, use ```pits_stats``` to generate
statistics for all the scores:

    pits_stats scan mutopia

This will produce a file ```stats.json``` inside the directory for each score.

Combine statistics
------------------

Finally, you can sum up all the stats produced into a single file:

    pits_stats combine mutopia

This will produce a file named ```totalstats.json``` inside the catalog folder.

What about a bit of data vizualisation ?
----------------------------------------

If you have [matplotlib](http://matplotlib.org) installed, copy/paste this
snippet of code in a python shell:

    import json
    import pylab as pl

    with open('totalstats.json') as f:
        stats = json.loads(f.read())

    samples = []
    for key, count in stats.items():
        samples.extend([int(key)] * count)

    pl.hist(samples, bins=88)
    pl.show()
