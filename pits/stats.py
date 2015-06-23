import mido
import click
import json
import os
import fnmatch
import logging

from collections import Counter
from contextlib import contextmanager
from zipfile import ZipFile
from tempfile import TemporaryDirectory

from pits.music import NoteAccumulator
from pits.pprint import pnote


def note_messages(track):
    for message in track:
        if not isinstance(message, mido.MetaMessage):
            yield message


class TrackAnalyzer(object):

    PIANO_PROGRAMS = range(1, 9)

    def __init__(self, track):
        self.track = track

    def has_instrument(self):
        for message in self.find_by_type('program_change'):
            if message.program in self.PIANO_PROGRAMS:
                return True
        return False

    def has_polyphony(self):
        return len(self.find_polyphony()) > 0

    def find_by_type(self, type_):
        for message in note_messages(self.track):
            if message.type == type_:
                yield message

    def find_polyphony(self):
        accumulator = NoteAccumulator()
        for message in note_messages(self.track):
            accumulator.read_event(message)
            if accumulator.is_polyphonic():
                return accumulator.pop_active()
        return set()


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
def pprint(filepath):
    mid = mido.MidiFile(filepath)
    mid.print_tracks()


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def catalog(directory):
    catalog_path = os.path.join(directory, 'catalog.json')
    with open(catalog_path) as f:
        catalog = json.loads(f.read())

    for piece in catalog['catalog']:
        piece_path = os.path.join(directory, piece['short_author'], piece['short_title'])
        search = (piece['instrument'] not in catalog['whitelist'])
        analyze_piece(piece, piece_path, search)


@cli.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--search/--no-search', default=False)
@click.option('--output', '-o', type=click.Path(), default='stats.json')
def analyze(filepath, search, output):
    stats = analyze_file(filepath, search)
    print_stats(stats)

    with open(output, 'w', encoding="utf-8") as f:
        f.write(json.dumps(stats))


@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), default='combined.json')
def combine(directory, output):
    total = Counter()
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, 'stats.json'):
            filepath = os.path.join(root, filename)
            logging.debug("reading %s", filepath)
            with open(filepath) as f:
                stats = {int(key): value for key, value in json.loads(f.read()).items()}
                total += Counter(stats)

    print_stats(total)
    with open(output, 'w') as f:
        f.write(json.dumps(total))


def analyze_piece(piece, path, search):
    logging.info("analyzing %s", path)

    stat_path = os.path.join(path, 'stats.json')
    if os.path.exists(stat_path):
        logging.debug("stats already generated. skipping.")
        return

    with extract_midi_files(piece, path) as midi_files:
        total = Counter()
        stats = (analyze_file(midi_file, search) for midi_file in midi_files)
        for count in stats:
            total += count

        with open(stat_path, 'w') as f:
            f.write(json.dumps(total))


def analyze_file(filepath, search):
    logging.debug("analyzing file %s. search: %s", filepath, search)

    mid = mido.MidiFile(filepath)

    if search:
        tracks = find_piano_tracks(mid.tracks)
    else:
        tracks = mid.tracks

    return count_notes(tracks)


@contextmanager
def extract_midi_files(piece, path):
    filename = os.path.basename(piece['midi'])
    filepath = os.path.join(path, filename)

    if filepath.endswith('mid'):
        yield [filepath]
    else:
        with ZipFile(filepath) as zipfile, TemporaryDirectory() as directory:
            logging.debug("extracting %s to %s", filepath, directory)
            zipfile.extractall(directory)
            yield [os.path.join(directory, name)
                   for name in zipfile.namelist()]


def find_piano_tracks(tracks):
    analyzers = [TrackAnalyzer(t) for t in tracks]
    pianos = [a.track for a in analyzers if a.has_instrument()]
    polyphonic = (a.track for a in analyzers if a.has_polyphony())

    if pianos:
        logging.debug("search found tracks marked as a piano instrument")
        yield from pianos
    else:
        logging.debug("search found polyphonic tracks")
        yield from polyphonic


def count_notes(tracks):
    total = Counter()
    for track in tracks:
        counter = Counter(m.note
                          for m in note_messages(track)
                          if m.type == 'note_on')
        total += counter
    return total


def print_stats(note_count):
    sorted_notes = sorted(note_count.items(), key=lambda x: x[1], reverse=True)
    for note, count in sorted_notes:
        print("{}: {}".format(pnote(note), count))


def main():
    cli()


if __name__ == "__main__":
    main()
