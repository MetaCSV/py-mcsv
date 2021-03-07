#  py-mcsv - A MetaCSV parser for Python
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

from abc import ABC, abstractmethod
from enum import Enum
from io import StringIO
from typing import Generic, TextIO, Type

from mcsv.field_processor import FieldProcessor
from mcsv.util import T


class DataType(Enum):
    BOOLEAN = 1
    CURRENCY_INTEGER = 2
    CURRENCY_DECIMAL = 3
    DATE = 4
    DATETIME = 5
    DECIMAL = 6
    FLOAT = 7
    INTEGER = 8
    PERCENTAGE_DECIMAL = 9
    PERCENTAGE_FLOAT = 10
    TEXT = 11
    OBJECT = 12


class FieldDescription(ABC, Generic[T]):
    @abstractmethod
    def render(self, out: TextIO):
        pass

    @abstractmethod
    def to_field_processor(self, null_value: str) -> FieldProcessor[T]:
        pass

    @abstractmethod
    def get_data_type(self) -> DataType:
        pass

    def get_python_type(self) -> Type:
        return T

    def __str__(self) -> str:
        o = StringIO()
        self.render(o)
        return o.getvalue()