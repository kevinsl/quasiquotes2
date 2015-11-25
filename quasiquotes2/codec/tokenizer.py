from io import BytesIO
from itertools import islice
from token import (
    ERRORTOKEN,
    INDENT,
    DEDENT,
    NAME,
    NEWLINE,
    NUMBER,
    OP,
    STRING,
)
from tokenize import tokenize as default_tokenize, untokenize, NL, generate_tokens
from token import tok_name
from Queue import Queue, Empty
import collections
import itertools


class TokenInfo(collections.namedtuple('TokenInfo', 'type string start end line')):
    def __repr__(self):
        annotated_type = '%d (%s)' % (self.type, tok_name[self.type])
        return ('TokenInfo(type=%s, string=%r, start=%r, end=%r, line=%r)' %
                self._replace(type=annotated_type))


class FuzzyTokenInfo(TokenInfo):
    def __new__(cls, type, string, start=None, end=None, line=None):
        return super(FuzzyTokenInfo, cls).__new__(cls, type, string, start, end, line)

    def __eq__(self, other):
        #import pdb;pdb.set_trace()
        return self.type == other.type and self.string == other.string
    __req__ = __eq__

    def __ne__(self, other):
        return not self == other
    __rne__ = __ne__


with_tok = FuzzyTokenInfo(NAME, 'with')
dollar_tok = FuzzyTokenInfo(ERRORTOKEN, '$')
spaceerror_tok = FuzzyTokenInfo(ERRORTOKEN, ' ')
col_tok = FuzzyTokenInfo(OP, ':')
nl_tok = FuzzyTokenInfo(NEWLINE, '\n')
left_bracket_tok = FuzzyTokenInfo(OP, '[')
pipe_tok = FuzzyTokenInfo(OP, '|')
right_bracket_tok = FuzzyTokenInfo(OP, ']')


class PeekableIterator(object):
    """

        >>> pi = PeekableIterator('abc')
        >>> print pi
        1

    """

    def __init__(self, stream):
        self._stream = iter(stream)
        self._peeked = Queue()

    def __iter__(self):
        return self

    def next(self):
        try:
            return self._peeked.get_nowait()
        except Empty:
            return next(self._stream)

    def peek(self, n=1):
        peeked = tuple(islice(self, None, n))
        put = self._peeked.put_nowait
        for item in peeked:
            put(item)
        return peeked

    def lookahead_iter(self):
        while True:
            for val in self.peek(1):
                yield val
            try:
                next(self)
            except StopIteration:
                break


def quote_stmt_tokenizer(name, start, tok_stream):
    """
    Tokenizer for quote_stmt.
    called with "with" token
    DO LATER
    """
    return


def quote_expr_tokenizer(name, start, tok_stream):
    """
    Tokenizer for quote_expr.
    Called with "[" token
    Yields: the tokens needed to generate a quote_expr.
    """
    print
    print name
    print start
    print tok_stream
    print 
    ls = []
    append = ls.append
    prev_line = name.start[0] - 1
    was_pipe = False

    for u in tok_stream:
        if u == right_bracket_tok and was_pipe:
            break

        if u.start[0] > prev_line:
            prev_line = u.start[0]
            append(u.line)

        if u == pipe_tok:
            was_pipe = True
        else:
            was_pipe = False

    # remove the start and end quotes.
    ls[0] = (
        ' ' * (name.end[1] + 1) +
        ls[0].split('[$' + name.string + '|', 1)[-1]
    )
    ls[-1] = ls[-1].rsplit('|]', 1)[0]
    tok_pos = start.end[0], start.end[1] + len(name.string)

    yield name._replace(start=start.start, end=tok_pos, line='<line>')
    yield TokenInfo(type=OP, string='.', start=tok_pos, end=tok_pos, line='<line>',)
    yield TokenInfo(type=OP, string='_quote_expr', start=tok_pos, end=tok_pos, line='<line>',)
    yield TokenInfo(type=OP, string='(', start=tok_pos, end=tok_pos, line='<line>',)
    yield TokenInfo(type=NUMBER, string=str(start.start[1]), start=tok_pos, end=tok_pos, line='<line>',)
    yield TokenInfo(type=OP, string=',', start=tok_pos, end=tok_pos, line='<line>',)
    yield TokenInfo(type=STRING, string=repr(''.join(ls)), start=tok_pos, end=tok_pos, line='<line>',)
    yield TokenInfo(type=OP, string=')', start=tok_pos, end=tok_pos, line='<line>',)



def tokenize(readline):
    """
    Tokenizer for the quasiquotes language extension.
    """
    #import pdb;pdb.set_trace()
    #tokens = default_tokenize(readline, tokinfo)
    tokens = generate_tokens(readline)
    tok_stream = PeekableIterator(itertools.starmap(TokenInfo, tokens))
    for t in tok_stream:
        #t = TokenInfo(*t)
        print 'OKOKOK', t
        #print ti

        if t == with_tok:
            # DO LATER
            continue

        elif t == left_bracket_tok:
            try:
                dol, name, pipe = tok_stream.peek(3)
            except ValueError:
                continue

            if dol == dollar_tok and pipe == pipe_tok:
                tuple(islice(tok_stream, None, 3))
                for val in quote_expr_tokenizer(name, t, tok_stream):
                    yield val
                continue

        yield t
    return


def tokenize_bytes(bs):
    """
    Tokenize a bytes object.
    """
    return tokenize(BytesIO(bs).readline)


def tokenize_string(cs):
    """
    Tokenize a str object.
    """
    return tokenize_bytes(cs.encode('utf-8'))


def transform_bytes(bs):
    """
    Run bytes through the tokenizer end emit the pure python representation.
    """
    return untokenize(tokenize_bytes(bs))


def transform_string(cs):
    """
    Run a str through the tokenizer and emit the pure python representation.
    """
    return untokenize(tokenize_string(cs)).decode('utf-8')


if __name__ == '__main__':

    text = "val = [$hamlet| To Be Converted |]\r\ns = 'regular python'"
    print transform_string(text)

    pi = PeekableIterator('abc')

