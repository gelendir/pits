import Levenshtein as levenshtein
import re
import random
import logging

from pits import bktree

logger = logging.getLogger(__name__)

MAX_DEPTH = 10

WORD = re.compile(r"^(\w+)[/ ]", re.UNICODE)
NUMBER = re.compile(r"\d", re.UNICODE)


def filter_words(lines):
    for line in lines:
        match = WORD.match(line)
        if match:
            word = match.group(1)
            if not word.isupper() and not NUMBER.search(word):
                yield word.lower()


class Dictionary(object):

    @classmethod
    def from_filepath(cls, filepath):
        with open(filepath, encoding='utf-8') as f:
            return cls.from_file(f)

    @classmethod
    def from_file(cls, reader):
        return cls(filter_words(reader))

    def __init__(self, words, max_depth=MAX_DEPTH):
        self.tree = bktree.BKTree(levenshtein.distance, words)
        self.max_depth = max_depth

    def pick(self, word):
        for depth in range(1, self.max_depth + 1):
            choices = self.tree.query(word, depth)
            if choices:
                choice = random.choice(choices)
                logger.debug("'%s' found '%s'", word, choice)
                return choice[1]
        logger.debug("'%s' found nothing", word)
        return word
