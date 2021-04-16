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
import logging
from typing import (List, Optional, Callable, Tuple)

from mcsv.col_type_parser import ColTypeParser
from mcsv.field_description import FieldDescription
from mcsv.meta_csv_data import MetaCSVDataBuilder, MetaCSVData
from mcsv.util import (split_parameters, RFC4180_DIALECT, FileLike,
                       open_file_like, unescape_line_terminator)


class MetaCSVParser:
    def __init__(self, meta: FileLike,
                 create_object_description: Optional[Callable[
                     [Tuple[str]], FieldDescription]] = None):
        self._meta = meta
        self._logger = logging.getLogger("py-mcsv")
        self._col_type_parser = ColTypeParser(create_object_description)
        self._meta_csv_builder = MetaCSVDataBuilder()

    def parse(self) -> MetaCSVData:
        with open_file_like(self._meta, "r", encoding="utf-8") as source:
            self._parse_source(source)
        return self._meta_csv_builder.build()

    def _parse_source(self, source):
        reader = csv.reader(source, RFC4180_DIALECT)
        header = next(reader)
        if header != ["domain", "key", "value"]:
            raise ValueError(
                "Bad file header, expected: "
                f"[\"domain\", \"key\", \"value\"], was {header}")
        for row in reader:
            self._parse_row(row)

    def _parse_row(self, row: List[str]):
        domain, key, value = row
        if domain == "meta":
            self._parse_meta_row(key, value)
        elif domain == "file":
            self._parse_file_row(key, value)
        elif domain == "csv":
            self._parse_csv_row(key, value)
        elif domain == "data":
            self._parse_data_row(key, value)
        else:
            raise ValueError(f"Unknown domain: '{domain}'")

    def _parse_meta_row(self, key, value):
        if key == "version":
            self._meta_csv_builder.meta_version(value)
        else:
            self._meta_csv_builder.meta(key, value)

    def _parse_file_row(self, key, value):
        if key == "encoding":
            self._meta_csv_builder.encoding(value)
        elif key == "bom":
            self._meta_csv_builder.bom(self._parse_boolean_value(value))
        elif key == "line_terminator":
            self._meta_csv_builder.line_terminator(
                unescape_line_terminator(value))
        else:
            raise ValueError(f"Unknown file domain key: {key}")
        pass

    def _parse_csv_row(self, key, value):
        if key == "delimiter":
            self._meta_csv_builder.delimiter(value)
        elif key == "double_quote":
            self._meta_csv_builder.double_quote(
                self._parse_boolean_value(value))
        elif key == "escape_char":
            self._meta_csv_builder.escape_char(value)
        elif key == "quote_char":
            self._meta_csv_builder.quote_char(value)
        elif key == "skip_initial_space":
            self._meta_csv_builder.skip_initial_space(
                self._parse_boolean_value(value))
        else:
            raise ValueError(f"Unknown csv domain key: {key}")

    def _parse_boolean_value(self, value: str) -> bool:
        return value.strip() in ("true", "1")

    def _parse_data_row(self, key, value):
        subkeys = split_parameters(key)
        if subkeys[0] == "col":
            if len(subkeys) != 3:
                raise ValueError(f"Bad data key {key}")
            self._parse_data_col_row(*subkeys[1:], value)
        elif subkeys[0] == "null_value":
            self._meta_csv_builder.null_value(value)
        else:
            raise ValueError(f"Unknown data domain key {key}")

    def _parse_data_col_row(self, col_num, col_key, value):
        if col_key == "type":
            n = int(col_num)
            self._parse_col_type(n, value)
        else:
            raise ValueError(f"Unknown data col/n/key: {col_key}")

    def _parse_col_type(self, n, value):
        description = self._col_type_parser.parse_col_type(value)

        if description is not None:
            self._meta_csv_builder.description_by_col_index(n, description)
