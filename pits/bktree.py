"""

This module implements Burkhard-Keller Trees (bk-tree).  bk-trees
allow fast lookup of words that lie within a specified distance of a
query word.  For example, this might be used by a spell checker to
find near matches to a mispelled word.

The implementation is based on the description in this article:

http://blog.notdot.net/2007/4/Damn-Cool-Algorithms-Part-1-BK-Trees

Licensed under the PSF license: http://www.python.org/psf/license/

- Adam Hupp <adam@hupp.org>

Modified for python3 compatibility by Gregory Eric Sanderson
[gregory dot eric dot sanderson at gmail dot com]

"""


class BKTree(object):

    def __init__(self, distfn, words):
        """
        Create a new BK-tree from the given distance function and
        words.

        Arguments:

        distfn: a binary function that returns the distance between
        two words.  Return value is a non-negative integer.  the
        distance function must be a metric space.

        words: an iterable.  produces values that can be passed to
        distfn

        """
        self.distfn = distfn

        it = iter(words)
        root = next(it)
        self.tree = (root, {})

        for i in it:
            self._add_word(self.tree, i)

    def _add_word(self, parent, word):
        pword, children = parent
        d = self.distfn(word, pword)
        if d in children:
            self._add_word(children[d], word)
        else:
            children[d] = (word, {})

    def query(self, word, n):
        """
        Return all words in the tree that are within a distance of `n'
        from `word`.

        Arguments:

        word: a word to query on

        n: a non-negative integer that specifies the allowed distance
        from the query word.

        Return value is a list of tuples (distance, word), sorted in
        ascending order of distance.

        """
        def rec(parent):
            pword, children = parent
            d = self.distfn(word, pword)
            results = []
            if d <= n:
                results.append((d, pword))

            for i in range(d - n, d + n + 1):
                child = children.get(i)
                if child is not None:
                    results.extend(rec(child))
            return results

        # sort by distance
        return sorted(rec(self.tree))
