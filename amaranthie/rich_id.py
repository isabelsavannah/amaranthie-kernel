import re
import pathlib

class IllegalIDException(Exception):
    pass

class RichID:
    def __init__(self, *data):
        flat_words = list(normalizing_flatten(data))

        if not all(self._validate_word(word) for word in flat_words):
            raise IllegalIDException()
        self.id_words = flat_words
        self.str = "/".join(flat_words)

    def to_path(self):
        return pathlib.PurePath(self.id_words)

    def _validate_word(self, word):
        return re.fullmatch("[a-zA-Z0-9 #$%&-_]+")

    def __str__(self):
        return self.str

    def __truediv__(self, other):
        return RichID([self.id_words, other])

    def __iter__(self):
        yield from self.id_words

    def __hash__(self):
        return hash(self.str)

    def __eq__(self, other):
        return str(self) == str(other)
    def __le__(self, other):
        return str(self) <= str(other)
    def __ge__(self, other):
        return str(self) >= str(other)
    def __lt__(self, other):
        return str(self) < str(other)
    def __gt__(self, other):
        return str(self) > str(other)

def normalizing_flatten(args):
    for element in args:
        if isinstance(element, str):
            if len(element) < 1:
                throw IllegalIDException()
            yield from element.split("/")
        if isinstance(element, RichId):
            yield from element.id_words
        if isinstance(element, pathlib.PurePath):
            yield from element.parts
        else:
            yield from normalizing_flatten(element)


