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

from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
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
        pass  # pragma: no cover

    @abstractmethod
    def to_field_processor(self, null_value: str) -> FieldProcessor[T]:
        pass  # pragma: no cover

    @abstractmethod
    def get_data_type(self) -> DataType:
        pass  # pragma: no cover

    @abstractmethod
    def get_python_type(self) -> Type:
        pass  # pragma: no cover

    def __str__(self) -> str:
        o = StringIO()
        self.render(o)
        return o.getvalue()


def data_type_to_python_type(data_type: DataType) -> Type:
    return {
        DataType.BOOLEAN: bool, DataType.CURRENCY_INTEGER: int,
        DataType.CURRENCY_DECIMAL: Decimal, DataType.DATE: date,
        DataType.DATETIME: datetime, DataType.DECIMAL: Decimal,
        DataType.FLOAT: float, DataType.INTEGER: int,
        DataType.PERCENTAGE_DECIMAL: Decimal,
        DataType.PERCENTAGE_FLOAT: float, DataType.TEXT: str
    }.get(data_type, str)


def python_type_to_data_type(python_type: Type) -> "DataType":
    return {bool: DataType.BOOLEAN, date: DataType.BOOLEAN,
            datetime: DataType.DATETIME, Decimal: DataType.DECIMAL,
            float: DataType.FLOAT, int: DataType.INTEGER,
            str: DataType.TEXT}.get(python_type, DataType.OBJECT)
