# coding: utf-8
#  py-mcsv - A MetaCSV parser for Python
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
import io
from pathlib import Path
from typing import Any, List, BinaryIO, TextIO, Callable

from mcsv.meta_csv_data import MetaCSVData


class MetaCSVWriter:
    def __init__(self, writer: csv.writer,
                 map_row: Callable[[List[Any]], List[str]]):
        self._writer = writer
        self._map_row = map_row

    def writeheader(self, row: List[str]):
        self._writer.writerow(row)

    def writerow(self, row: List[Any]):
        self._writer.writerow(self._map_row(row))


class MetaCSVWriterFactory:
    def __init__(self, data: MetaCSVData):
        self._data = data

    def writer(self, path: Path) -> MetaCSVWriter:
        dest = self._get_dest(path)
        writer = csv.writer(dest, self._data.dialect)
        map_row = self._get_map_row()
        return MetaCSVWriter(writer, map_row)

    def _get_dest(self, path):
        encoding = self._get_encoding()
        if isinstance(path, (str, Path)):
            dest = open(path, "w", newline="", encoding=encoding)
        elif isinstance(path, (TextIO, io.TextIOBase)):
            dest = path
        elif isinstance(path, (BinaryIO, io.IOBase)):
            dest = io.TextIOWrapper(path, encoding=encoding)
        else:
            raise ValueError(path)
        return dest

    def _get_encoding(self):
        if self._data.encoding == "utf-8" and self._data.bom:
            encoding = "utf-8-sig"
        else:
            encoding = self._data.encoding
        return encoding

    def _get_map_row(self):
        processors = {
            i: d.to_field_processor(self._data.null_value)
            for i, d in self._data.field_description_by_index.items()
        }

        def map_row(row: List[Any]) -> List[str]:
            return [processors[i].to_string(value) if i in processors else str(
                value) for i, value in
                    enumerate(row)]

        return map_row
