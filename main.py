import click
import mido
import random
import bisect
import tts
import shutil
import itertools

KEYRANGE = range(21, 108)


class NoteAccumulator(object):

    def __init__(self):
        self.active = set()
        self.notes = set()

    def read_event(self, event):
        if event.type == 'note_on':
            self.play(event.note)
        elif event.type == 'note_off':
            self.release(event.note)

    def play(self, note):
        self.active.add(note)
        self.notes.add(note)

    def release(self, note):
        self.active.remove(note)

    def pop_notes(self):
        notes = self.notes
        self.notes = set()
        return notes

    def is_playing(self):
        return len(self.active) > 0


@click.command()
def devices():
    for device in mido.get_input_names():
        print(device)


@click.command()
@click.argument('device')
@click.option('--filepath', '-f', default="audio.mp3", type=click.Path(dir_okay=False, writable=True))
@click.option('--lettermap', '-l', default="letters.txt", type=click.Path(exists=True))
def compose(device, filepath, lettermap):
    letters = load_letters(lettermap)
    keymap = generate_keymap(letters, KEYRANGE)

    with mido.open_input(device) as port:
        score = read_score(port)

    text = generate_text(score, keymap)
    generated_path = generate_tts(text)
    shutil.move(generated_path, filepath)


def load_letters(filepath):
    with open(filepath, encoding="utf-8") as f:
        lines = (l.split(" ") for l in f)
        return {l[0]: int(l[1]) for l in lines}


def generate_keymap(letters, keyrange):
    keymap = {}
    total = sum(letters.values())
    weights = generate_weights(letters)
    for note in keyrange:
        rand = random.randint(0, total - 1)
        choice = bisect.bisect(weights, (rand, None))
        keymap[note] = weights[choice][1]
    return keymap


def generate_weights(letters):
    pairs = letters.items()
    letters = tuple(l[0] for l in pairs)
    weights = itertools.accumulate(tuple(l[1] for l in pairs))
    return tuple(zip(weights, letters))


def read_score(port, end=108):
    score = []
    accumulator = NoteAccumulator()

    event = port.receive()
    while not should_stop(event, end):
        accumulator.read_event(event)
        if not accumulator.is_playing():
            score.append(accumulator.pop_notes())
        event = port.receive()

    return score


def should_stop(event, end):
    return event.type == 'note_on' and event.note == end


def generate_text(score, keymap):
    words = (map_word(notes, keymap) for notes in score)
    return " ".join(words)


def map_word(notes, keymap):
    notes = list(notes)
    random.shuffle(notes)
    return "".join(keymap[note] for note in notes)


def generate_tts(text):
    return tts.generate(text)


if __name__ == "__main__":
    group = click.Group()
    group.add_command(devices)
    group.add_command(compose)
    group()
