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
from typing import (Iterator, List, Any, Callable, Mapping, Union, TextIO,
                    BinaryIO, Optional, Tuple)

from mcsv.field_description import FieldDescription, DataType
from mcsv.field_descriptions import TextFieldDescription
from mcsv.field_processor import FieldProcessor
from mcsv.field_processors import MetaCSVReadException, ReadError
from mcsv.meta_csv_data import MetaCSVData, MetaCSVDataBuilder
from mcsv.parser import MetaCSVParser


class MetaCSVReader(Iterator[List[Any]]):
    def __init__(self, header: List[str], reader: csv.reader,
                 source: TextIO,
                 map_row: Callable[[List[str]], List[Any]],
                 descriptions: List[FieldDescription]):
        self.header = header
        self._reader = reader
        self._source = source
        self._map_row = map_row
        self._descriptions = descriptions
        self._first = True

    def __iter__(self) -> "MetaCSVReader":
        return self

    def __next__(self) -> List[Any]:
        if self._first:
            self._first = False
            return self.header

        try:
            row = next(self._reader)
        except StopIteration:
            self._source.close()
            raise
        else:
            return self._map_row(row)

    def get_types(self) -> List[DataType]:
        return [d.get_data_type() for d in self._descriptions]


class MetaCSVDictReader(Iterator[Mapping[str, Any]]):
    def __init__(self, header: List[str], reader: csv.reader,
                 source: TextIO,
                 func: Callable[[List[str]], List[Any]],
                 descriptions: List[FieldDescription]):
        self.header = header
        self._reader = reader
        self._source = source
        self._func = func
        self._descriptions = descriptions
        self._width = len(header)

    def __iter__(self) -> "MetaCSVDictReader":
        return self

    def __next__(self) -> Mapping[str, Any]:
        try:
            row = next(self._reader)
        except StopIteration:
            self._source.close()
            raise
        else:
            if len(row) > self._width:
                d = dict(zip(self.header, self._func(row[:self._width])))
                d["@other"] = row[self._width:]
            else:
                d = dict(zip(self.header, self._func(row)))
            return d

    def get_types(self) -> Mapping[str, DataType]:
        return {col: d.get_data_type() for col, d in
                zip(self.header, self._descriptions)}


class MetaCSVReaderFactory:
    def __init__(self, data: MetaCSVData, on_error="wrap"):
        self._data = data
        self._on_error = on_error

    def reader(self, path: Union[str, Path, TextIO, BinaryIO]
               ) -> MetaCSVReader:
        source = self._get_source(path)
        reader = csv.reader(source, self._data.dialect)
        header = next(reader)
        descriptions = [self._data.field_description_by_index[i]
                        if i in self._data.field_description_by_index
                        else TextFieldDescription.INSTANCE
                        for i in range(len(header))]
        map_row = self._get_map_row(descriptions)
        return MetaCSVReader(header, reader, source, map_row, descriptions)

    def dict_reader(self, path: Union[str, Path]) -> MetaCSVDictReader:
        source = self._get_source(path)
        reader = csv.reader(source, self._data.dialect)
        header = next(reader)
        descriptions = [self._data.field_description_by_index[i]
                        if i in self._data.field_description_by_index
                        else TextFieldDescription.INSTANCE
                        for i in range(len(header))]
        func = self._get_map_row(descriptions)
        return MetaCSVDictReader(header, reader, source, func, descriptions)

    def _get_source(self, path):
        encoding = self._get_encoding()
        if isinstance(path, (str, Path)):
            source = open(path, "r", encoding=encoding)
        elif isinstance(path, (TextIO, io.TextIOBase)):
            source = path
        elif isinstance(path, (BinaryIO, io.IOBase)):
            source = io.TextIOWrapper(path, encoding=encoding)
        else:
            raise ValueError(path)
        return source

    def _get_encoding(self):
        if self._data.encoding == "utf-8" and self._data.bom:
            encoding = "utf-8-sig"
        else:
            encoding = self._data.encoding
        return encoding

    def _get_map_row(self, descriptions: List[FieldDescription]
                     ) -> Callable[[List[str]], List[Optional[Any]]]:
        processors = [description.to_field_processor(self._data.null_value)
                      for description in descriptions]
        if self._on_error == "wrap":
            def aux(description: FieldDescription,
                    processor: FieldProcessor,
                    text: str) -> Optional[Any]:
                try:
                    return processor.to_object(text)
                except MetaCSVReadException:
                    return ReadError(text, str(description))

            def map_row(row):
                return [aux(description, processor, v)
                        for description, processor, v in
                        zip(descriptions, processors, row)]
        elif self._on_error == "null":
            def aux(processor: FieldProcessor,
                    text: str) -> Optional[Any]:
                try:
                    return processor.to_object(text)
                except MetaCSVReadException:
                    return None

            def map_row(row):
                return [aux(processor, v) for processor, v in
                        zip(processors, row)]
        elif self._on_error == "text":
            def aux(processor: FieldProcessor,
                    text: str) -> Optional[Any]:
                try:
                    return processor.to_object(text)
                except MetaCSVReadException:
                    return text

            def map_row(row):
                return [aux(processor, v) for processor, v in
                        zip(processors, row)]
        elif self._on_error == "exception":
            def map_row(row):
                return [processor.to_object(v) for processor, v in
                        zip(processors, row)]
        else:
            raise ValueError(self._on_error)

        return map_row


MetaCSVReaderFactory.DEFAULT = MetaCSVReaderFactory(
    MetaCSVDataBuilder().build(),
    on_error="wrap")


def get_reader_factory(meta_path: Union[str, Path, BinaryIO, TextIO],
                       create_object_description: Optional[Callable[
                           [Tuple[str]], FieldDescription]] = None,
                       on_error: str = "wrap") -> MetaCSVReaderFactory:
    """
    Create a new MetaCSVReaderFactory

    :param meta_path:
    :param create_object_description:
    :return:
    """
    data = MetaCSVParser(meta_path,
                         create_object_description).parse()
    return MetaCSVReaderFactory(data, on_error)


def open_csv(path: Union[str, Path, BinaryIO, TextIO],
             meta_path: Union[str, Path, BinaryIO, TextIO] = None
             ) -> MetaCSVReader:
    if meta_path is None:
        meta_path = _find_meta_path(path)
    reader_factory = get_reader_factory(meta_path)
    return reader_factory.reader(path)


def open_dict_csv(path: Union[str, Path, BinaryIO, TextIO],
                  meta_path: Union[str, Path, BinaryIO, TextIO] = None,
                  ) -> MetaCSVDictReader:
    if meta_path is None:
        meta_path = _find_meta_path(path)
    reader_factory = get_reader_factory(meta_path)
    return reader_factory.dict_reader(path)


def _find_meta_path(path):
    if isinstance(path, Path):
        pass
    elif isinstance(path, str):
        path = Path(path)
    else:
        raise ValueError("Can't find the MetaCSV file")
    return path.with_suffix(".mcsv")
