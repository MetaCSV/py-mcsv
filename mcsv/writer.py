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
from contextlib import contextmanager
from typing import Any, List, TextIO, Callable, Optional, Mapping, Iterator

from mcsv.meta_csv_data import MetaCSVData
from mcsv.renderer import MetaCSVRenderer
from mcsv.util import FileLike, open_file_like


class MetaCSVWriter:
    def __init__(self, writer: csv.writer,
                 map_row: Callable[[List[Any]], List[str]]):
        self._writer = writer
        self._map_row = map_row

    def writeheader(self, row: List[str]):
        self._writer.writerow(row)

    def writerow(self, row: List[Any]):
        self._writer.writerow(self._map_row(row))


class MetaCSVDictWriter:
    def __init__(self, writer: csv.DictWriter,
                 map_row: Callable[[Mapping[str, Any]], Mapping[str, str]]):
        self._writer = writer
        self._map_row = map_row
        self._writer.writeheader()

    def writerow(self, row: Mapping[str, Any]):
        self._writer.writerow(self._map_row(row))


class MetaCSVWriterFactory:
    def __init__(self, data: MetaCSVData):
        self._data = data

    def writer(self, dest: TextIO) -> MetaCSVWriter:
        writer = csv.writer(dest, self._data.dialect)
        map_row = self._get_map_row()
        return MetaCSVWriter(writer, map_row)

    def dict_writer(self, dest: TextIO, header: List[str], *args, **kwargs
                    ) -> MetaCSVDictWriter:
        writer = csv.DictWriter(dest, header, *args,
                                dialect=self._data.dialect, **kwargs)
        map_row = self._get_map_dict_row(header)
        return MetaCSVDictWriter(writer, map_row)

    def _get_map_row(self) -> Callable[[List[Any]], List[str]]:
        processors_by_index = {
            i: d.to_field_processor(self._data.null_value)
            for i, d in self._data.field_description_by_index.items()
        }

        def map_row(row: List[Any]) -> List[str]:
            return [processors_by_index[i].to_string(value)
                    if i in processors_by_index
                    else str(value)
                    for i, value in enumerate(row)]

        return map_row

    def _get_map_dict_row(
            self, header: List[str]) -> Callable[[Mapping[str, Any]],
                                                 Mapping[str, str]]:
        processors_by_field = {
            header[i]: d.to_field_processor(self._data.null_value)
            for i, d in self._data.field_description_by_index.items()
        }

        def map_row(row: Mapping[str, Any]) -> Mapping[str, str]:
            return {field: processors_by_field[field].to_string(value)
                    if field in processors_by_field
                    else str(value)
                    for field, value in row.items()}

        return map_row


@contextmanager
def open_csv_writer(file: FileLike,
                    data: MetaCSVData,
                    meta_file: Optional[FileLike] = None
                    ) -> Iterator[MetaCSVWriter]:
    with _open_writer(file, data, meta_file) as dest:
        yield MetaCSVWriterFactory(data).writer(dest)


@contextmanager
def _open_writer(file: FileLike,
                 data: MetaCSVData,
                 meta_file: Optional[FileLike] = None
                 ) -> Iterator[MetaCSVWriter]:
    with open_file_like(meta_file, "w", encoding="utf-8") as meta_dest:
        MetaCSVRenderer.create(meta_dest).write(data)
    with open_file_like(file, "w", encoding=data.wrap_encoding()) as dest:
        yield dest


@contextmanager
def open_dict_csv_writer(file: FileLike,
                         header: List[str],
                         data: MetaCSVData,
                         meta_file: Optional[FileLike] = None
                         ) -> Iterator[MetaCSVDictWriter]:
    with _open_writer(file, data, meta_file) as dest:
        yield MetaCSVWriterFactory(data).dict_writer(dest, header)
