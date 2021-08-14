import re
import pathlib

class IllegalIDException(Exception):
    pass

class RichID:
    def __init__(self, id_seq):
        flat_words = flatten_id(id_seq)
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

    @classMethod
    from_string(cls, string):
        if len(string) < 1:
            throw IllegalIDException()
        words = string.split("/")
        return cls(words)

    @classMethod
    from_path(cls, path):
        words = path.parts()
        if len(words) < 1:
            throw IllegalIDException()
        return cls(words)

def flatten_id(*args):
    return list(_pathify_generator(args))

def _pathify_generator(args):
    for element in args:
        if isinstance(element, str):
            yield element
        else:
            yield from _pathify_generator(element)


