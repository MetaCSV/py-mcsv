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
import logging
import typing
from typing import Mapping

from mcsv.field_description import FieldDescription, DataType
from mcsv.field_descriptions import TextFieldDescription
from mcsv.util import rfc4180_dialect


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

    def meta_version(self, version: str) -> "MetaCSVDataBuilder":
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

    def to_metadata(self) -> "MetaCSVMetaData":
        return MetaCSVMetaData(self._description_by_col_index)


class MetaCSVMetaData:
    def __init__(self,
                 description_by_col_index: Mapping[int, FieldDescription]):
        self._description_by_col_index = description_by_col_index

    def get_description(self, c: int) -> FieldDescription:
        return self._description_by_col_index.get(
            c, TextFieldDescription.INSTANCE)

    def get_data_type(self, c: int) -> DataType:
        return self._description_by_col_index.get(
            c, TextFieldDescription.INSTANCE).get_data_type()

    def get_python_type(self, c: int) -> typing.Type:
        return self._description_by_col_index.get(
            c, TextFieldDescription.INSTANCE).get_python_type()
