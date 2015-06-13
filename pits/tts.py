import requests
import subprocess
import os
import uuid
import tempfile
import textwrap

GOOGLE_URL = "http://translate.google.com/translate_tts"


class ConversionError(Exception):
    pass


def generate(sentence, language='fr'):
    lines = textwrap.wrap(sentence, 100)
    files = [generate_chunk(l, language) for l in lines]

    if len(files) == 1:
        return files[0]

    filepath = merge_files(files)

    for path in files:
        os.unlink(path)

    return filepath


def generate_chunk(line, language):
    filepath = unique_filepath('mp3')

    params = {'ie': 'UTF-8', 'tl': language, 'q': line.encode('utf8')}
    response = requests.get(GOOGLE_URL, params=params, stream=True)

    if response.status_code != 200:
        raise ConversionError("google translate responded with {}".format(response.status_code))

    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(2 * 1024 * 1024):
            f.write(chunk)

    return filepath


def unique_filepath(extension):
    name = "{}.{}".format(uuid.uuid4(), extension)
    return os.path.join(tempfile.gettempdir(), name)


def merge_files(files):
    filepath = unique_filepath('mp3')
    cmd = ['sox'] + files + ['-C', '32', filepath]
    subprocess.check_call(cmd)
    return filepath
