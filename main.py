import click
import mido
import random
import string
import tts
import shutil

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


def generate_text(score):
    keymap = generate_keymap()
    words = (map_word(notes, keymap) for notes in score)
    return " ".join(words)


def generate_keymap():
    return {note: random.choice(string.ascii_lowercase)
            for note in KEYRANGE}


def map_word(notes, keymap):
    notes = list(notes)
    random.shuffle(notes)
    return "".join(keymap[note] for note in notes)


def generate_tts(text):
    return tts.generate(text)


@click.command()
def devices():
    for device in mido.get_input_names():
        print(device)


@click.command()
@click.argument('device')
@click.argument('filepath', type=click.Path(dir_okay=False, writable=True))
def compose(device, filepath):
    with mido.open_input(device) as port:
        score = read_score(port)
    text = generate_text(score)
    generated_path = generate_tts(text)
    shutil.move(generated_path, filepath)


if __name__ == "__main__":
    group = click.Group()
    group.add_command(devices)
    group.add_command(compose)
    group()
