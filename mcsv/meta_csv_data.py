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
import logging
import typing
from pathlib import Path
from typing import Mapping
from typing import Union

from mcsv.field_description import FieldDescription
from mcsv.field_descriptions import TextFieldDescription
from mcsv.util import RFC4180_DIALECT, rfc4180_dialect


class MetaCSVData:
    def __init__(self, meta_version: str, meta: Mapping[str, str],
                 encoding: str, bom: bool, dialect: csv.Dialect,
                 null_value: str,
                 field_description_by_index: Mapping[int, FieldDescription]):
        self.meta_version = meta_version
        self.meta = meta
        self.encoding = encoding
        self.bom = bom
        self.dialect = dialect
        self.null_value = null_value
        self.field_description_by_index = field_description_by_index


class MetaCSVRenderer:
    @staticmethod
    def create(dest: Union[
        str, Path, typing.TextIO, typing.BinaryIO], minimal=True):
        if isinstance(dest, io.TextIOBase):
            return MetaCSVRenderer._create_from_dest(dest, minimal)
        elif isinstance(dest, (io.RawIOBase, io.BufferedIOBase)):
            dest = io.TextIOWrapper(dest, encoding="utf-8", newline="\r\n")
            return MetaCSVRenderer._create_from_dest(dest, minimal)
        elif isinstance(dest, Path):
            return MetaCSVRenderer._create_from_path(dest, minimal)
        elif isinstance(dest, str):
            return MetaCSVRenderer._create_from_path(Path(dest), minimal)

    @staticmethod
    def _create_from_path(path, minimal):
        with path.open("w", newline="\r\n") as dest:
            return MetaCSVRenderer._create_from_dest(dest, minimal)

    @staticmethod
    def _create_from_dest(dest, minimal):
        writer = csv.writer(dest, RFC4180_DIALECT)
        return MetaCSVRenderer(writer, minimal)

    def __init__(self, writer: csv.writer, minimal=True):
        self._writer = writer
        self._minimal = minimal

    # def __init__(self, dest: Path, _encoding: str, _dialect: csv.Dialect,
    #              header: Tuple[str],
    #              field_descriptions: Tuple[FieldDescription]):
    #     self.dest = dest
    #     self._encoding = _encoding
    #     self._dialect = _dialect
    #     self.header = header
    #     self.field_descriptions = list(field_descriptions)

    # def __setitem__(self, key, value):
    #     if isinstance(key, int):
    #         self.field_descriptions[key] = value
    #     else:
    #         try:
    #             i = self.header.index(key)
    #         except ValueError:
    #             pass
    #         else:
    #             self.field_descriptions[i] = value

    def _write_minimal(self, data: MetaCSVData):
        self._writer.writerow(["domain", "key", "delimiter"])
        if data.encoding.casefold() == "utf-8-sig":
            self._writer.writerow(["file", "encoding", "utf-8"])
            self._writer.writerow(["file", "bom", "true"])
        elif data.encoding.casefold() != "utf-8":
            self._writer.writerow(["file", "encoding", data.encoding])
        elif data.bom:
            self._writer.writerow(["file", "bom", "true"])

        if data.dialect.lineterminator != "\r\n":
            self._writer.writerow(
                ["file", "line_terminator", data.dialect.lineterminator])
        if data.dialect.delimiter != ",":
            self._writer.writerow(["csv", "delimiter", data.dialect.delimiter])
        if not data.dialect.doublequote:
            self._writer.writerow(["csv", "double_quote", str(
                bool(data.dialect.skipinitialspace)).lower()])
        if data.dialect.escapechar:
            self._writer.writerow(
                ["csv", "escape_char", data.dialect.escapechar])
        if data.dialect.quotechar != '"':
            self._writer.writerow(["csv", "quote_char", data.dialect.quotechar])
        if data.dialect.skipinitialspace:
            self._writer.writerow(["csv", "skip_initial_space", str(
                bool(data.dialect.skipinitialspace)).lower()])
        for i, description in data.field_description_by_index.items():
            if not isinstance(description, TextFieldDescription):
                self._writer.writerow(
                    ["data", f"col/{i}/type", str(description)])

    def _write_verbose(self, data: MetaCSVData):
        self._writer.writerow(["domain", "key", "delimiter"])
        self._writer.writerow(["file", "encoding", data.encoding])
        self._writer.writerow(
            ["file", "line_terminator", data.dialect.lineterminator])
        self._writer.writerow(["csv", "delimiter", data.dialect.delimiter])
        self._writer.writerow(["csv", "double_quote", str(
            bool(data.dialect.skipinitialspace)).lower()])
        self._writer.writerow(["csv", "escape_char", data.dialect.escapechar])
        self._writer.writerow(["csv", "quote_char", data.dialect.quotechar])
        self._writer.writerow(["csv", "skip_initial_space", str(
            bool(data.dialect.skipinitialspace)).lower()])
        for i, description in data.field_description_by_index.items():
            self._writer.writerow(["data", f"col/{i}/type", str(description)])


class MetaCSVDataBuilder:
    def __init__(self):
        self._logger = logging.getLogger("py-mcsv")
        self._dialect = rfc4180_dialect()
        self._description_by_col_index = {}
        self._meta_version = "draft0"
        self._meta = {}
        self._encoding = "UTF-8"
        self._bom = False
        self._null_value = ""

    def build(self) -> "MetaCSVData":
        return MetaCSVData(self._meta_version, self._meta, self._encoding,
                           self._bom, self._dialect, self._null_value,
                           self._description_by_col_index)

    def metaVersion(self, version: str) -> "MetaCSVDataBuilder":
        self._meta_version = version
        return self

    def meta(self, key: str, value: str) -> "MetaCSVDataBuilder":
        self._meta[key] = value
        return self

    def encoding(self, encoding) -> "MetaCSVDataBuilder":
        self._encoding = encoding
        return self

    def bom(self, bom: True) -> "MetaCSVDataBuilder":
        self._bom = bom
        return self

    def line_terminator(self, lt: str) -> "MetaCSVDataBuilder":
        self._dialect.lineterminator = lt
        return self

    def delimiter(self, delimiter: str) -> "MetaCSVDataBuilder":
        self._dialect.delimiter = delimiter
        return self

    def double_quote(self, dq: bool) -> "MetaCSVDataBuilder":
        self._dialect.doublequote = dq
        return self

    def escape_char(self, ec: str) -> "MetaCSVDataBuilder":
        self._dialect.escapechar = ec
        return self

    def quote_char(self, qc: str) -> "MetaCSVDataBuilder":
        self._dialect.quotechar = qc
        return self

    def skip_initial_space(self, sis: bool) -> "MetaCSVDataBuilder":
        self._dialect.skipinitialspace = sis
        return self

    def null_value(self, value: str) -> "MetaCSVDataBuilder":
        self._null_value = value
        return self

    def description_by_col_index(self, i: int,
                                 description: FieldDescription
                                 ) -> "MetaCSVDataBuilder":
        self._description_by_col_index[i] = description
        return self
