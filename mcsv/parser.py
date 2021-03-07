# coding: utf-8

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

import csv
import io
import logging
from numbers import Number
from typing import (Union, List, Mapping, Any, Iterator, TypeVar, BinaryIO,
                    TextIO, Optional, Callable, Tuple)
from pathlib import Path
import collections

from mcsv.col_type_parser import ColTypeParser
from mcsv.field_description import FieldDescription
from mcsv.field_descriptions import TextFieldDescription
from mcsv.field_processors import TextFieldProcessor
from mcsv.meta_csv_data import MetaCSVDataBuilder, MetaCSVData
from mcsv.util import split_parameters, rfc4180_dialect, RFC4180_DIALECT

N = TypeVar('N', bound=Number)

Converter = collections.namedtuple("Converter", ['datatype', 'func'])


class CSVInterpreter:
    def __init__(self, data: MetaCSVData):
        self._data = data

    def reader(self, path: Union[str, Path, BinaryIO], skip_types: bool = True
               ) -> Iterator[List[Any]]:
        if self._data.encoding == "utf-8" and self._data.bom:
            encoding = "utf-8-sig"
        else:
            encoding = self._data.encoding

        if isinstance(path, (str, Path)):
            with open(path, "r", encoding=encoding) as source:
                yield from self._reader(source, skip_types)
        else:
            yield from self._reader(
                io.TextIOWrapper(path, encoding=encoding), skip_types)

    def _reader(self, source, skip_types: bool):
        reader = csv.reader(source, self._data.dialect)
        header = next(reader)
        yield header
        descriptions = [self._data.field_description_by_index[i]
                        if i in self._data.field_description_by_index
                        else TextFieldDescription.INSTANCE
                        for i in range(len(header))]
        if not skip_types:
            yield [description.get_data_type().name
                   for description in descriptions]
        processors = [description.to_field_processor(self._data.null_value)
                      for description in descriptions]
        for row in reader:
            yield [processor.to_object(v)
                   for processor, v in zip(processors, row)]

    def dict_reader(self, path: Union[str, Path], skip_types: bool = True
                    ) -> Iterator[Mapping[str, Any]]:
        reader = self.reader(path, skip_types)
        header = next(reader)
        width = len(header)
        for row in reader:
            if len(row) > width:
                d = dict(zip(header, row[:width]))
                d["@other"] = row[width:]
            else:
                d = dict(zip(header, row))
            yield d


CSVInterpreter.DEFAULT = CSVInterpreter(MetaCSVDataBuilder().build())


class MetaCSVParser:
    def __init__(self, meta_path: Union[str, Path, BinaryIO, TextIO],
                 create_object_description: Optional[Callable[
                     [Tuple[str]], FieldDescription]] = None):
        self._meta_path = meta_path
        self._logger = logging.getLogger("py-mcsv")
        self._col_type_parser = ColTypeParser(create_object_description)
        self._meta_csv_builder = MetaCSVDataBuilder()

    def parse(self) -> CSVInterpreter:
        if isinstance(self._meta_path, (str, Path)):
            with open(self._meta_path, "r", encoding="utf-8") as source:
                self._parse_source(source)
        elif isinstance(self._meta_path, io.TextIOBase):
            self._parse_source(self._meta_path)
        elif isinstance(self._meta_path, (io.RawIOBase, io.BufferedIOBase)):
            self._parse_source(
                io.TextIOWrapper(self._meta_path, encoding="utf-8"))
        else:
            raise TypeError(
                f"meta_path {self._meta_path} ({type(self._meta_path)})")

        data = self._meta_csv_builder.build()
        return CSVInterpreter(data)

    def _parse_source(self, source):
        reader = csv.reader(source, RFC4180_DIALECT)
        header = next(reader)
        if header != ["domain", "key", "value"]:
            raise ValueError(
                f"Bad file header, expected: [\"domain\", \"key\", \"value\"], was {header}")
        for row in reader:
            self._parse_row(row)

    def _parse_row(self, row: List[str]):
        domain, key, value = row
        if domain == "_meta":
            self._parse_meta_row(key, value)
        if domain == "file":
            self._parse_file_row(key, value)
        elif domain == "csv":
            self._parse_csv_row(key, value)
        elif domain == "data":
            self._parse_data_row(key, value)
        else:
            raise ValueError(f"Unknown domain: {domain}")

    def _parse_meta_row(self, key, value):
        if key == "version":
            self._meta_csv_builder.metaVersion(value)
        else:
            self._meta_csv_builder.meta(key, value)

    def _parse_file_row(self, key, value):
        if key == "encoding":
            self._meta_csv_builder.encoding(value)
        elif key == "bom":
            self._meta_csv_builder.bom(self._parse_boolean_value(value))
        elif key == "line_terminator":
            self._meta_csv_builder.line_terminator(value)
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
        elif subkeys[0] == "_null_value":
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


def get_parser(meta_path: Union[str, Path, BinaryIO, TextIO],
               strict: bool = False,
               create_object_description: Optional[Callable[
                   [Tuple[str]], FieldDescription]] = None) -> CSVInterpreter:
    try:
        interpreter = MetaCSVParser(meta_path,
                                    create_object_description).parse()
    except FileNotFoundError:
        interpreter = CSVInterpreter.DEFAULT
    return interpreter


def open_csv(path: Union[str, Path, BinaryIO, TextIO],
             meta_path: Union[str, Path, BinaryIO, TextIO] = None,
             strict: bool = False, skip_types=True) -> Iterator[List[Any]]:
    if meta_path is None:
        meta_path = _find_meta_path(path)
    interpreter = get_parser(meta_path, strict)
    return interpreter.reader(path, skip_types)


def open_dict_csv(path: Union[str, Path, BinaryIO, TextIO],
                  meta_path: Union[str, Path, BinaryIO, TextIO] = None,
                  strict: bool = False, skip_types=True
                  ) -> Iterator[Mapping[str, Any]]:
    if meta_path is None:
        meta_path = _find_meta_path(path)
    interpreter = get_parser(meta_path, strict)
    return interpreter.dict_reader(path, skip_types)


def _find_meta_path(path):
    if isinstance(path, Path):
        pass
    elif isinstance(path, str):
        path = Path(path)
    else:
        raise ValueError("Can't find the MetaCSV file")
    return path.with_suffix(".mcsv")
