#  py-mcsv - A MetaCSV library for Python
#      Copyright (C) 2020 J. Férard <https://github.com/jferard>
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
#
#   This file is part of ColumnDet.
#
#   ColumnDet is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   ColumnDet is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import csv
import io
import typing
from pathlib import Path
from typing import Tuple, Optional, Union


class FieldDescription:
    @staticmethod
    def _none_to_empty(value):
        return "" if value is None else value


class MetaCSVData:
    def __init__(self, path: Path, encoding: str, dialect: csv.Dialect,
                 header: Tuple[str],
                 field_descriptions: Tuple[FieldDescription]):
        self.path = path
        self.encoding = encoding
        self.dialect = dialect
        self.header = header
        self.field_descriptions = list(field_descriptions)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.field_descriptions[key] = value
        else:
            try:
                i = self.header.index(key)
            except ValueError:
                pass
            else:
                self.field_descriptions[i] = value

    def write(self, path: Optional[Union[
        str, Path, typing.TextIO, typing.BinaryIO]] = None, minimal=True):
        if isinstance(path, io.TextIOBase):
            self._write(path, minimal)
        elif isinstance(path, (io.RawIOBase, io.BufferedIOBase)):
            self._write(io.TextIOWrapper(path, encoding="utf-8", newline="\r\n"
                                         ), minimal)
        else:
            if path is None:
                path = self.path.with_suffix(".mcsv")
            elif isinstance(path, str):
                path = Path(path)

            with path.open("w", newline="\r\n") as dest:
                self._write(dest, minimal)

    def _write(self, dest, minimal):
        writer = csv.writer(dest)
        writer.writerow(["domain", "key", "value"])
        if not minimal or self.encoding.casefold() != "utf-8":
            writer.writerow(["file", "encoding", self.encoding])
        if not minimal or self.dialect.lineterminator != "\r\n":
            writer.writerow(
                ["file", "line_terminator", self.dialect.lineterminator])
        if not minimal or self.dialect.delimiter != ",":
            writer.writerow(["csv", "delimiter", self.dialect.delimiter])
        if not minimal or not self.dialect.doublequote:
            writer.writerow(["csv", "double_quote", str(
                bool(self.dialect.skipinitialspace)).lower()])
        if not minimal or self.dialect.escapechar:
            writer.writerow(["csv", "escape_char", self.dialect.escapechar])
        if not minimal or self.dialect.quotechar != '"':
            writer.writerow(["csv", "quote_char", self.dialect.quotechar])
        if not minimal or self.dialect.skipinitialspace:
            writer.writerow(["csv", "skip_initial_space", str(
                bool(self.dialect.skipinitialspace)).lower()])
        for i, description in enumerate(self.field_descriptions):
            if not minimal or not isinstance(description, TextDescription):
                writer.writerow(["data", f"col/{i}/type", str(description)])


class BooleanDescription(FieldDescription):
    def __init__(self, true_word: str, false_word: str):
        self._true_word = true_word
        self._false_word = false_word

    def __repr__(self):
        return (f"BooleanDescription({repr(self._true_word)}, "
                f"{repr(self._false_word)})")

    def __str__(self):
        return f"boolean/{self._true_word}/{self._false_word}"


class CurrencyDescription(FieldDescription):
    def __init__(self, pre: Optional[bool], currency: Optional[str],
                 float_description: FieldDescription):
        self._pre = pre
        self._currency = currency
        self._float_description = float_description

    def __repr__(self):
        return (f"CurrencyDescription({repr(self._pre)}, "
                f"{repr(self._currency)}, "
                f"{repr(self._float_description)})")

    def __str__(self):
        pre = self._none_to_empty("pre" if self._pre else "post")
        return (f"currency/{pre}/{self._none_to_empty(self._currency)}/"
                f"{self._float_description}")


class DateDescription(FieldDescription):
    def __init__(self, date_format: str, locale_name: Optional[str] = None):
        self._date_format = date_format
        self._locale_name = locale_name

    def __repr__(self):
        if self._locale_name is None:
            return f"DateDescription({repr(self._date_format)})"
        else:
            return (f"DateDescription({repr(self._date_format)}, "
                    f"{repr(self._locale_name)})")

    def __str__(self):
        if self._locale_name is None:
            return f"date/{self._date_format}"
        else:
            return f"date/{self._date_format}/{self._locale_name}"


class DatetimeDescription(FieldDescription):
    def __init__(self, date_format: str, locale_name: Optional[str] = None):
        self._date_format = date_format
        self._locale_name = locale_name

    def __repr__(self):
        if self._locale_name is None:
            return f"DatetimeDescription({repr(self._date_format)})"
        else:
            return (f"DatetimeDescription({repr(self._date_format)}, "
                    f"{repr(self._locale_name)})")

    def __str__(self):
        if self._locale_name is None:
            return f"datetime/{self._date_format}"
        else:
            return f"datetime/{self._date_format}/{self._locale_name}"


class FloatDescription(FieldDescription):
    def __init__(self, thousand_sep: Optional[str], decimal_sep: str):
        self._thousand_sep = thousand_sep
        self._decimal_sep = decimal_sep

    def __repr__(self):
        return (f"FloatDescription({repr(self._thousand_sep)}, "
                f"{repr(self._decimal_sep)})")

    def __str__(self):
        return (f"float/{self._none_to_empty(self._thousand_sep)}/"
                f"{self._decimal_sep}")


class IntegerDescription(FieldDescription):
    def __init__(self, thousand_sep: Optional[str] = None):
        self._thousand_sep = thousand_sep

    def __repr__(self):
        if self._thousand_sep is None:
            return "IntegerDescription.INSTANCE"
        else:
            return f"IntegerDescription({repr(self._thousand_sep)}"

    def __str__(self):
        if self._thousand_sep is None:
            return f"integer"
        else:
            return f"integer/{self._none_to_empty(self._thousand_sep)}"


IntegerDescription.INSTANCE = IntegerDescription()


class PercentageDescription(FieldDescription):
    def __init__(self, pre: bool, sign: Optional[str],
                 float_description: FieldDescription):
        self._pre = pre
        self._sign = sign
        self._float_description = float_description

    def __repr__(self):
        return (f"PercentageDescription({repr(self._pre)}, "
                f"{repr(self._sign)}, "
                f"{repr(self._float_description)})")

    def __str__(self):
        pre = "pre" if self._pre else "post"
        return (f"percentage/{pre}/{self._none_to_empty(self._sign)}/"
                f"{self._float_description}")


class TextDescription(FieldDescription):
    INSTANCE = None

    def __repr__(self):
        return "TextDescription.INSTANCE"

    def __str__(self):
        return "text"


TextDescription.INSTANCE = TextDescription()
