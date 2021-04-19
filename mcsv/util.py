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
import csv
from contextlib import contextmanager
from decimal import Decimal
from io import TextIOBase, IOBase, TextIOWrapper
from locale import getlocale, LC_TIME, setlocale
from pathlib import Path
from typing import TextIO, TypeVar, Union, BinaryIO

T = TypeVar('T')


def split_parameters(parameters):
    """
    >>> split_parameters("date/dd\\\\/MM\\\\/yyyy")
    ['date', 'dd/MM/yyyy']

    :param parameters:
    :return:
    """
    # Avoid split("/") because of escaped slashes
    new_parameters = []
    start = 0
    backslash = False
    cur = ""
    for j, c in enumerate(parameters):
        if j < start:  # never happens
            pass
        elif c == "\\":
            backslash = True
        elif c == "/":
            if backslash:
                cur += c
                backslash = False
            else:
                new_parameters.append(cur)
                cur = ""
                start = j + 1
        else:
            if backslash:  # let's not forget the \
                cur += "\\"
            cur += c
            backslash = False

    new_parameters.append(cur)
    return new_parameters


def render(out: TextIO, *values: str):
    last = len(values) - 1
    while last > 0 and values[last] == "":
        last -= 1
    if last < 0:
        return
    for i in range(0, last):
        render_escaped(out, values[i])
        out.write("/")
    out.write(values[last])


def render_escaped(out, value: str):
    for c in value:
        if c == "/" or c == "\\":
            out.write("\\")
        out.write(c)


def none_to_empty(value):
    return "" if value is None else value


def format_decimal(value: Decimal, thousand_separator: str,
                   decimal_separator: str) -> str:
    """
    >>> from decimal import Decimal
    >>> format_decimal(Decimal("-12345678"), "~", ";")
    '-12~345~678'
    >>> format_decimal(Decimal("-12345678.9101112"), "~", ";")
    '-12~345~678;9101112'
    >>> format_decimal(Decimal("-12.345678"), "~", ";")
    '-12;345678'
    """
    default_ts = thousand_separator is None or thousand_separator == ""
    default_ds = decimal_separator is None or decimal_separator == "."
    if default_ds and default_ts:
        return str(value)
    text = str(value)
    sep_index = text.find(".")
    if sep_index == -1:
        return format_integer(value, thousand_separator)
    else:
        return (format_integer(int(value), thousand_separator)
                + decimal_separator
                + text[sep_index + 1:])


def format_float(value, thousand_separator, decimal_separator):
    """
    >>> format_float(-12345678, "~", ";")
    '-12~345~678'
    >>> format_float(-12.345678, "~", ";")
    '-12;345678'
    >>> format_float(12345678, "~", ";")
    '12~345~678'
    >>> format_float(-12345678.9101112, "~", ";")
    '-12~345~678;9101112'
    """
    text = str(value)
    default_ts = thousand_separator is None or thousand_separator == ""
    default_ds = decimal_separator is None or decimal_separator == "."
    if default_ds and default_ts:
        return str(value)
    sep_index = text.find(".")
    if sep_index == -1:
        return format_integer(value, thousand_separator)
    else:
        return (format_integer(int(value), thousand_separator)
                + decimal_separator + text[sep_index + 1:])


def format_integer(value, thousand_separator):
    """
    >>> format_integer(-12345678, "~")
    '-12~345~678'
    >>> format_integer(12345678, "~")
    '12~345~678'
    >>> format_integer(-11, "~")
    '-11'

    :param value:
    :param thousand_separator:
    :return:
    """
    text = str(value)
    size = len(text)
    if value < 0:
        start = 1
    else:
        start = 0

    i = (size - start) % 3 + start
    if i == start:
        i += 3
    s = text[0:i]
    while i < size:
        s += thousand_separator + text[i:i + 3]
        i += 3
    return s


@contextmanager
def time_locale(locale_name):
    """
    >>> from datetime import date
    >>> with time_locale("fr_FR.UTF8"):
    ...     print(date(2020, 1, 1).strftime("%B"))
    janvier

    :param locale_name:
    :return:
    """
    oldlocale = getlocale(LC_TIME)
    setlocale(LC_TIME, locale_name)
    try:
        yield None
    finally:
        if oldlocale is not None:
            setlocale(LC_TIME, oldlocale)


class rfc4180_dialect(csv.Dialect):
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = 0


RFC4180_DIALECT = rfc4180_dialect()
csv.register_dialect("RFC4180_DIALECT", RFC4180_DIALECT)


def to_meta_path(path: Union[str, Path]) -> Path:
    if isinstance(path, Path):
        pass
    elif isinstance(path, str):
        path = Path(path)
    else:
        raise ValueError("Can't find the MetaCSV file")
    return path.with_suffix(".mcsv")


FileLike = Union[str, Path, BinaryIO, TextIO]


@contextmanager
def open_file_like(file: FileLike, mode: str = "r",
                   encoding: str = "utf-8", *args, **kwargs) -> TextIO:
    """
    Open a source of characters with a contexte manager
    :param file: a file name, file source, text io or binary io
    :param mode: r or w
    :param encoding: optional encoding
    """
    if isinstance(file, (str, Path)):
        with open(file, mode, encoding=encoding, *args, **kwargs) as f:
            yield f
    elif isinstance(file, (TextIO, TextIOBase)):
        yield file
        if not file.closed:
            file.flush()
    elif isinstance(file, (BinaryIO, IOBase)):
        ret = TextIOWrapper(file, encoding=encoding)
        yield ret
        if not ret.closed:
            ret.flush()
    else:
        raise ValueError(file)


def escape_line_terminator(lt):
    """

    >>> escape_line_terminator("\\n")
    '\\\\n'

    :param lt: the line terminator
    :return: the escaped line terminator
    """
    if lt == "\n":
        return "\\n"
    elif lt == "\r\n":
        return "\\r\\n"
    elif lt == "\r":
        return "\\r"
    else:
        return lt


def unescape_line_terminator(elt):
    """

    >>> unescape_line_terminator("\\\\n")
    '\\n'

    :param elt: the escaped line terminator
    :return: the line terminator
    """
    if elt == "\\n":
        return "\n"
    elif elt == "\\r\\n":
        return "\r\n"
    elif elt == "\\r":
        return "\r"
    else:
        return elt
