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
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TextIO

from mcsv.field_description import DataType, FieldDescription
from mcsv.field_processor import FieldProcessor
from mcsv.field_processors import (BooleanFieldProcessor,
                                   FloatFieldProcessor, IntegerFieldProcessor,
                                   CurrencyFieldProcessor,
                                   DecimalFieldProcessor,
                                   DateAndDatetimeFieldProcessor,
                                   PercentageFieldProcessor, TextFieldProcessor)
from mcsv.util import render, none_to_empty, T


class BooleanFieldDescription(FieldDescription[bool]):
    def __init__(self, true_word: str, false_word: str):
        self._true_word = true_word
        self._false_word = false_word

    def render(self, out: TextIO):
        if self._false_word:
            render(out, "boolean", self._true_word, self._false_word)
        else:
            render(out, "boolean", self._true_word)

    def to_field_processor(self, null_value: str) -> FieldProcessor:
        return BooleanFieldProcessor(self._true_word, self._false_word,
                                     null_value)

    def get_data_type(self) -> DataType:
        return DataType.BOOLEAN

    def __repr__(self) -> str:
        return (f"BooleanFieldDescription({repr(self._true_word)}, "
                f"{repr(self._false_word)})")


class CurrencyDecimalFieldDescription(FieldDescription[Decimal]):
    def __init__(self, pre: Optional[bool], currency: Optional[str],
                 decimal_description: FieldDescription[Decimal]):
        self._pre = pre
        self._currency = currency
        self._decimal_description = decimal_description

    def render(self, out: TextIO):
        pre = none_to_empty("pre" if self._pre else "post")
        render(out, "sign", pre, none_to_empty(self._currency))
        out.write("/")
        self._decimal_description.render(out)

    def to_field_processor(self, null_value: str) -> FieldProcessor[T]:
        processor = self._decimal_description.to_field_processor(null_value)
        return CurrencyFieldProcessor(self._pre, self._currency, processor,
                                      null_value)

    def get_data_type(self) -> DataType:
        return DataType.CURRENCY_DECIMAL

    def __repr__(self):
        return (f"CurrencyDecimalFieldDescription({repr(self._pre)}, "
                f"{repr(self._currency)}, "
                f"{repr(self._decimal_description)})")


class CurrencyIntegerFieldDescription(FieldDescription):
    def __init__(self, pre: Optional[bool], currency: Optional[str],
                 integer_description: FieldDescription):
        self._pre = pre
        self._currency = currency
        self._integer_description = integer_description

    def render(self, out: TextIO):
        pre = none_to_empty("pre" if self._pre else "post")
        render(out, "sign", pre, none_to_empty(self._currency))
        out.write("/")
        self._integer_description.render(out)

    def to_field_processor(self, null_value: str) -> FieldProcessor:
        processor = self._integer_description.to_field_processor(null_value)
        return CurrencyFieldProcessor(self._pre, self._currency, processor,
                                      null_value)

    def get_data_type(self) -> DataType:
        return DataType.INTEGER

    def __repr__(self):
        return (f"CurrencyIntegerFieldDescription({repr(self._pre)}, "
                f"{repr(self._currency)}, "
                f"{repr(self._integer_description)})")


class DateFieldDescription(FieldDescription[date]):
    def __init__(self, date_format: str, locale_name: Optional[str] = None):
        self._date_format = date_format
        self._locale_name = locale_name

    def render(self, out: TextIO):
        if self._locale_name is None:
            render(out, "date", self._date_format)
        else:
            render(out, "date", self._date_format, self._locale_name)

    def to_field_processor(self, null_value: str) -> FieldProcessor[T]:
        return DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                             self._date_format,
                                             self._locale_name, null_value)

    def get_data_type(self) -> DataType:
        return DataType.DATE

    def __repr__(self):
        if self._locale_name is None:
            return f"DateFieldDescription({repr(self._date_format)})"
        else:
            return (f"DateFieldDescription({repr(self._date_format)}, "
                    f"{repr(self._locale_name)})")


class DatetimeFieldDescription(FieldDescription[datetime]):
    def __init__(self, date_format: str, locale_name: Optional[str] = None):
        self._date_format = date_format
        self._locale_name = locale_name

    def render(self, out: TextIO):
        if self._locale_name is None:
            render(out, "datetime", self._date_format)
        else:
            render(out, "datetime", self._date_format, self._locale_name)

    def to_field_processor(self, null_value: str) -> FieldProcessor[T]:
        return DateAndDatetimeFieldProcessor(datetime.fromtimestamp,
                                             self._date_format,
                                             self._locale_name, null_value)

    def get_data_type(self) -> DataType:
        return DataType.DATETIME

    def __repr__(self):
        if self._locale_name is None:
            return f"DatetimeFieldDescription({repr(self._date_format)})"
        else:
            return (f"DatetimeFieldDescription({repr(self._date_format)}, "
                    f"{repr(self._locale_name)})")


class DecimalFieldDescription(FieldDescription[Decimal]):
    def render(self, out: TextIO):
        render(out, "decimal", none_to_empty(self._thousand_sep),
               self._decimal_sep)

    def to_field_processor(self, null_value: str) -> FieldProcessor[Decimal]:
        return DecimalFieldProcessor(self._thousand_sep, self._decimal_sep,
                                     null_value)

    def get_data_type(self) -> DataType:
        return DataType.DECIMAL

    def __init__(self, thousand_sep: Optional[str], decimal_sep: str):
        self._thousand_sep = thousand_sep
        self._decimal_sep = decimal_sep

    def __repr__(self):
        return (f"DecimalFieldDescription({repr(self._thousand_sep)}, "
                f"{repr(self._decimal_sep)})")


class FloatFieldDescription(FieldDescription[float]):
    def __init__(self, thousand_sep: Optional[str], decimal_sep: str):
        self._thousand_sep = thousand_sep
        self._decimal_sep = decimal_sep

    def render(self, out: TextIO):
        render(out, "float", none_to_empty(self._thousand_sep),
               self._decimal_sep)

    def to_field_processor(self, null_value: str) -> FieldProcessor:
        return FloatFieldProcessor(self._thousand_sep, self._decimal_sep,
                                   null_value)

    def get_data_type(self) -> DataType:
        return DataType.FLOAT

    def __repr__(self):
        return (f"FloatFieldDescription({repr(self._thousand_sep)}, "
                f"{repr(self._decimal_sep)})")


class IntegerFieldDescription(FieldDescription[int]):
    def __init__(self, thousand_sep: Optional[str] = None):
        self._thousand_sep = thousand_sep

    def render(self, out: TextIO):
        if self._thousand_sep is None:
            out.write("integer")
        else:
            render(out, "integer", none_to_empty(self._thousand_sep))

    def to_field_processor(self, null_value: str) -> FieldProcessor:
        return IntegerFieldProcessor(self._thousand_sep, null_value)

    def get_data_type(self) -> DataType:
        return DataType.INTEGER

    def __repr__(self):
        if self._thousand_sep is None:
            return "IntegerFieldDescription.INSTANCE"
        else:
            return f"IntegerFieldDescription({repr(self._thousand_sep)}"


class PercentageFloatFieldDescription(FieldDescription[float]):
    def __init__(self, pre: bool, sign: Optional[str],
                 float_description: FieldDescription[float]):
        self._pre = pre
        self._sign = sign
        self._float_description = float_description

    def render(self, out: TextIO):
        pre = none_to_empty("pre" if self._pre else "post")
        render(out, "percentage", pre, none_to_empty(self._sign))
        out.write("/")
        self._float_description.render(out)

    def to_field_processor(self, null_value: str) -> FieldProcessor[T]:
        return PercentageFieldProcessor(self._pre, self._sign,
                                        self._float_description, null_value)

    def get_data_type(self) -> DataType:
        return DataType.PERCENTAGE_FLOAT

    def __repr__(self):
        return (f"PercentageFloatFieldDescription({repr(self._pre)}, "
                f"{repr(self._sign)}, "
                f"{repr(self._float_description)})")


class PercentageDecimalFieldDescription(FieldDescription[Decimal]):
    def __init__(self, pre: bool, sign: Optional[str],
                 decimal_description: FieldDescription[Decimal]):
        self._pre = pre
        self._sign = sign
        self._decimal_description = decimal_description

    def render(self, out: TextIO):
        pre = none_to_empty("pre" if self._pre else "post")
        render(out, "percentage", pre, none_to_empty(self._sign))
        out.write("/")
        self._decimal_description.render(out)

    def to_field_processor(self, null_value: str) -> FieldProcessor[T]:
        return PercentageFieldProcessor(self._pre, self._sign,
                                        self._decimal_description, null_value)

    def get_data_type(self) -> DataType:
        return DataType.PERCENTAGE_DECIMAL

    def __repr__(self):
        return (f"PercentageDecimalFieldDescription({repr(self._pre)}, "
                f"{repr(self._sign)}, "
                f"{repr(self._decimal_description)})")


class TextFieldDescription(FieldDescription[str]):
    INSTANCE = None

    def render(self, out: TextIO):
        out.write("text")

    def to_field_processor(self, null_value: str) -> FieldProcessor[str]:
        return TextFieldProcessor(null_value)

    def get_data_type(self) -> DataType:
        return DataType.TEXT

    def __repr__(self):
        return "TextFieldDescription.INSTANCE"


IntegerFieldDescription.INSTANCE = IntegerFieldDescription()
TextFieldDescription.INSTANCE = TextFieldDescription()
