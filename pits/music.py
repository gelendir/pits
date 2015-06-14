import itertools
import bisect
import random
from mido import MetaMessage


class NoteAccumulator(object):

    def __init__(self):
        self.active = set()
        self.notes = set()

    def read_event(self, event):
        if not isinstance(event, MetaMessage):
            if event.type == 'note_on':
                if event.velocity == 0:
                    self.release(event.note)
                else:
                    self.play(event.note)
            elif event.type == 'note_off':
                self.release(event.note)

    def play(self, note):
        self.active.add(note)
        self.notes.add(note)

    def release(self, note):
        self.active.remove(note)

    def pop(self):
        notes = self.notes
        self.notes = set()
        return notes

    def pop_active(self):
        active = self.active
        self.active = set()
        return active

    def is_playing(self):
        return len(self.active) > 0

    def is_polyphonic(self):
        return len(self.active) > 1


class KeyMap(object):

    KEYRANGE = range(21, 108)

    @classmethod
    def from_filepath(cls, filepath):
        with open(filepath, encoding="utf-8") as f:
            return cls.from_file(f)

    @classmethod
    def from_file(cls, reader):
        lines = (l.split(" ") for l in reader)
        letters = {l[0]: int(l[1]) for l in lines}
        return cls(letters)

    def __init__(self, letters):
        self.generate_weights(letters)
        self.shuffle_keys()

    def generate_weights(self, mapping):
        pairs = mapping.items()
        letters = tuple(p[0] for p in pairs)
        weights = itertools.accumulate(tuple(p[1] for p in pairs))

        self.weights = tuple(zip(weights, letters))
        self.total = sum(mapping.values())

    def shuffle_keys(self):
        self.keymap = {}
        for note in self.KEYRANGE:
            rand = random.randint(0, self.total - 1)
            choice = bisect.bisect(self.weights, (rand, None))
            self.keymap[note] = self.weights[choice][1]

    def map_notes(self, notes):
        return "".join(self.keymap[n] for n in notes)
