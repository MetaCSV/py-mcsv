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
from typing import TextIO

from mcsv.field_descriptions import TextFieldDescription
from mcsv.meta_csv_data import MetaCSVData
from mcsv.util import RFC4180_DIALECT, FileLike, open_file_like


class MetaCSVRenderer:
    @staticmethod
    def create(dest: TextIO, minimal=True) -> "MetaCSVRenderer":
        writer = csv.writer(dest, RFC4180_DIALECT)
        return MetaCSVRenderer(writer, minimal)

    def __init__(self, writer: csv.writer, minimal=True):
        self._writer = writer
        self._minimal = minimal

    def write(self, data: MetaCSVData):
        if self._minimal:
            self._write_minimal(data)
        else:
            self._write_verbose(data)

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
            self._writer.writerow(["csv", "quote_char",
                                   data.dialect.quotechar])
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


@contextmanager
def open_renderer(file: FileLike, minimal: bool =True):
    with open_file_like(file, "w", encoding="utf-8", newline="") as dest:
        return MetaCSVRenderer.create(dest, minimal)
