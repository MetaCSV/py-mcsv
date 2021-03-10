# coding: utf-8

#  py-mcsv - A MetaCSV library for Python
#      Copyright (C) 2020-2021 J. Férard <https://github.com/jferard>
#
#   This file is part of py-mcsv.
#
#   py-mcsv is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   py-mcsv is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import collections
from enum import Enum
from typing import Iterator

ULDML_TO_C1989_BASE = {
    'G5': None,  # Era designator
    'yy': '%y',  # Year
    'yyyy': '%Y',  # Year
    'y5': '%Y',  # Year
    'YY': '%y',  # Week year
    'YYYY': '%Y',  # Week year
    'Y5': '%Y',  # Week year
    'M2': '%m',  # Month in year
    'w3': '%W',  # Week in year
    'W': None,  # Week in month
    'D3': '%j',  # Day in year
    'd2': '%d',  # Day in month
    'F': None,  # Day of week in month
    'E6': '%A',  # Day name in week
    'u': '%u',  # Day number of week (1 = Monday, ..., 7 = Sunday)
    'a4': '%p',  # Am/pm marker
    'H2': '%H',  # Hour in day (0-23)
    'k2': None,  # Hour in day (1-24)
    'K2': None,  # Hour in am/pm (0-11)
    'h2': '%I',  # Hour in am/pm (1-12)
    'm2': '%M',  # Minute in hour
    's2': '%S',  # Second in minute
    'S+': '%f',  # Millisecond
    'z4': '%Z',  # General time zone
    'Z5': '%Z',  # RFC 822 time zone
    'X5': '%Z',  # ISO 8601 time zone
}

ULDML_TO_C1989 = {}
for k, v in ULDML_TO_C1989_BASE.items():
    if len(k) == 2:
        if k[1].isdigit():
            limit = int(k[1]) + 1
        elif k[1] == '+':
            limit = 20
        else:
            limit = None

        if limit is None:
            ULDML_TO_C1989[k] = v
        else:
            for i in range(1, limit):
                new_k = k[0]*i
                if new_k not in ULDML_TO_C1989:
                    ULDML_TO_C1989[new_k] = v
    elif v is not None:
        ULDML_TO_C1989[k] = v


class State(Enum):
    START = 1
    OPEN_TEXT = 2
    IN_FIELD = 3
    IN_TEXT = 4
    MAYBE_CLOSE_TEXT = 5


class OpCode(Enum):
    TEXT = 1
    FIELD = 2


Token = collections.namedtuple('Token', ['opcode', 'text'])


class _DateFormatParser:
    @staticmethod
    def create(lex=None):
        if lex is None:
            return _DateFormatParser(_DateFormatParser.lex)
        else:
            return _DateFormatParser(lex)

    def __init__(self, lex):
        self._lex = lex

    def parse(self, uldml_date_format):
        ret = ""
        for token in self._lex(uldml_date_format):
            if token.opcode == OpCode.TEXT:
                ret += token.text.replace("%", "%%")
            else:
                ret += ULDML_TO_C1989.get(token.text, token.text)

        return ret

    @staticmethod
    def lex(text) -> Iterator[Token]:
        text = text + '\0'
        i = 0
        c = None
        state = State.START
        while i < len(text):
            previous = c
            c = text[i]
            if state == State.START:
                if c == "'":
                    state = State.OPEN_TEXT
                else:
                    state = State.IN_FIELD
                    cur = c
            elif state == State.OPEN_TEXT:
                if c == "'":
                    yield Token(OpCode.TEXT, "'")
                    state = State.START
                else:
                    state = State.IN_TEXT
                    cur = c
            elif state == State.IN_FIELD:
                if c == previous:
                    cur += c
                else:
                    if cur.isalpha():
                        yield Token(OpCode.FIELD, cur)
                    else:
                        yield Token(OpCode.TEXT, cur)
                    state = State.START
                    i -= 1
            elif state == State.IN_TEXT:
                if c == "'":
                    state = State.MAYBE_CLOSE_TEXT
                else:
                    cur += c
            elif state == State.MAYBE_CLOSE_TEXT:
                if c == "'":
                    cur += c
                else:
                    yield Token(OpCode.TEXT, cur)
                    state = State.START
                    i -= 1
            i += 1


date_parser = _DateFormatParser.create()
