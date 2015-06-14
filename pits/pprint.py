NOTES = {
    0: 'C',
    1: 'C#/Db',
    2: 'D',
    3: 'D#/Eb',
    4: 'E',
    5: 'F',
    6: 'F#/Gb',
    7: 'G',
    8: 'G#/Ab',
    9: 'A',
    10: 'A#/Bb',
    11: 'B'
}


def pnotes(notes):
    return " ".join(pnote(n) for n in sorted(notes))


def pnote(note):
    octave = (note // 12) - 1
    tone = note % 12
    return "{}{}".format(NOTES[tone], octave)


def pmessage(message):
    return "{} {} ({})".format(message.type, pnote(message.note), message.time)
