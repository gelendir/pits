import click
import mido
import shutil
import logging
import pkg_resources

from pits import tts
from pits.music import NoteAccumulator, KeyMap
from pits.dictionary import Dictionary


DEFAULT_DICT = '/usr/share/hunspell/fr_CA.dic'


@click.group()
@click.option('--debug/--no-debug', default=False)
def pits(debug):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level)


@pits.command()
def devices():
    for device in mido.get_input_names():
        print(device)


@pits.command()
@click.argument('device')
@click.option('--audio', '-a', default="audio.mp3", type=click.Path(dir_okay=False, writable=True))
@click.option('--letters', '-l', type=click.Path(exists=True))
@click.option('--dictionary', '-d', default=DEFAULT_DICT, type=click.Path(exists=True))
def compose(device, audio, letters, dictionary):
    logging.debug("loading keymap")
    if letters:
        keymap = KeyMap.from_filepath(letters)
    else:
        path = pkg_resources.resource_filename('pits.assets', 'letters.txt')
        keymap = KeyMap.from_filepath(path)

    logging.debug("loading dictionary")
    dictionary = Dictionary.from_filepath(dictionary)

    with mido.open_input(device) as port:
        logging.info("recording music. Press C-8 to stop")
        score = read_score(port)

    logging.info("generating text")
    text = generate_text(score, keymap, dictionary)
    logging.debug("generated: %s", text)

    logging.info("generating tts at '%s'", audio)
    generated_path = generate_tts(text)
    shutil.move(generated_path, audio)


def read_score(port, end=108):
    score = []
    accumulator = NoteAccumulator()

    event = port.receive()
    while not should_stop(event, end):
        accumulator.read_event(event)
        if not accumulator.is_playing():
            score.append(accumulator.pop())
        event = port.receive()

    return score


def should_stop(event, end):
    return event.type == 'note_on' and event.note == end


def generate_text(score, keymap, dictionary):
    logging.debug("score: %s", score)
    words = (keymap.map_notes(note) for note in score)
    real_words = (dictionary.pick(word) for word in words)
    return " ".join(real_words)


def generate_tts(text):
    return tts.generate(text)


def main():
    pits()


if __name__ == "__main__":
    main()
