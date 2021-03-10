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
from decimal import Decimal
from time import strptime, mktime
from typing import Optional, Callable

from mcsv.field_processor import FieldProcessor
from mcsv.util import format_float, format_integer, T, format_decimal, \
    time_locale


class MetaCSVReadException(Exception):
    pass


class ReadError:
    def __init__(self, value: str, description: str):
        self.value = value
        self.description = description

    def __eq__(self, other):
        return (self.value == other.value
                and self.description == other.description)

    def __repr__(self):
        return f"ReadError({self.value}, {self.description})"


def text_or_none(text: str, null_value: str) -> Optional[str]:
    if text is None:
        return None
    textcf = text.strip()
    return None if textcf == null_value else text


class BooleanFieldProcessor(FieldProcessor[bool]):
    def __init__(self, true_word: str, false_word: str, null_value: str):
        self._null_value = null_value
        self._false_word = false_word.casefold()
        self._true_word = true_word.casefold()

    def to_object(self, text: str) -> Optional[bool]:
        text = text_or_none(text, self._null_value)
        if text is None:
            return None
        elif text.casefold() == self._true_word:
            return True
        elif text.casefold() == self._false_word:
            return False
        else:
            raise MetaCSVReadException(f"Wrong boolean: {text}")

    def to_string(self, value: Optional[bool]) -> str:
        return None if value is None else str(value).lower()


class CurrencyFieldProcessor(FieldProcessor[T]):
    def __init__(self, pre: Optional[bool], currency: Optional[str],
                 number_processor: FieldProcessor[T], null_value: str):
        self._pre = pre
        self._currency = currency
        self._number_processor = number_processor
        self._null_value = null_value

    def to_object(self, text: str) -> Optional[T]:
        text = text_or_none(text, self._null_value)
        if text is None:
            return None
        size = len(self._currency)
        if self._pre:
            if text.startswith(self._currency):
                text = text[size:].lstrip()
                return self._number_processor.to_object(text)
            else:
                raise MetaCSVReadException(
                    f"Missing {self._currency} currency symbol: {text}")
        else:
            if text.endswith(self._currency):
                text = text[:-size].lstrip()
                return self._number_processor.to_object(text)
            else:
                raise MetaCSVReadException(
                    f"Missing {self._currency} currency symbol: {text}")

    def to_string(self, value: Optional[T]) -> str:
        if value is None:
            return self._null_value
        v = self._number_processor.to_string(value)
        if self._pre:
            return f"{self._currency} {v}"
        else:
            return f"{v} {self._currency}"


class DateAndDatetimeFieldProcessor(FieldProcessor[T]):
    def __init__(self, fromtimestamp: Callable, date_format: str,
                 locale_name: str, null_value: str):
        self._fromtimestamp = fromtimestamp
        self._date_format = date_format
        self._locale_name = locale_name
        self._null_value = null_value

    def to_object(self, text: str) -> Optional[T]:
        text = text_or_none(text, self._null_value)
        if text is None:
            return None
        if self._locale_name is None:
            return self._fromtimestamp(
                mktime(strptime(text, self._date_format)))
        else:
            with time_locale(self._locale_name):
                return self._fromtimestamp(
                    mktime(strptime(text, self._date_format)))

    def to_string(self, value: Optional[T]) -> str:
        if self._locale_name is None:
            return value.strftime(self._date_format)
        else:
            with time_locale(self._locale_name):
                return value.strftime(self._date_format)


class DecimalFieldProcessor(FieldProcessor[Decimal]):
    def __init__(self, thousand_separator: Optional[str],
                 decimal_separator: str, null_value: str):
        self._thousand_separator = thousand_separator
        self._decimal_separator = decimal_separator
        self._null_value = null_value

    def to_object(self, text: str) -> Optional[Decimal]:
        if text is None:
            return None
        text = text.strip().casefold()
        if text == self._null_value:
            return None
        else:
            try:
                if self._thousand_separator:
                    text = text.replace(self._thousand_separator, "")
                if self._decimal_separator != ".":
                    text = text.replace(self._decimal_separator, ".")
                return Decimal(text)
            except ValueError as e:
                raise MetaCSVReadException(e)

    def to_string(self, value: Optional[Decimal]) -> str:
        if value is None:
            return self._null_value
        return format_decimal(value, self._thousand_separator,
                              self._decimal_separator)


class FloatFieldProcessor(FieldProcessor[float]):
    def __init__(self, thousand_separator: Optional[str],
                 decimal_separator: str, null_value: str):
        self._thousand_separator = thousand_separator
        self._decimal_separator = decimal_separator
        self._null_value = null_value

    def to_object(self, text: str) -> Optional[float]:
        if text is None:
            return None
        text = text.strip().casefold()
        if text == self._null_value:
            return None
        else:
            try:
                if self._thousand_separator:
                    text = text.replace(self._thousand_separator, "")
                if self._decimal_separator != ".":
                    text = text.replace(self._decimal_separator, ".")
                return float(text)
            except ValueError as e:
                raise MetaCSVReadException(e)

    def to_string(self, value: Optional[float]) -> str:
        if value is None:
            return self._null_value
        return format_float(value, self._thousand_separator,
                            self._decimal_separator)


class IntegerFieldProcessor(FieldProcessor[int]):
    def __init__(self, thousand_separator: Optional[str],
                 null_value: str):
        self._thousand_separator = thousand_separator
        self._null_value = null_value

    def to_object(self, text: str) -> Optional[float]:
        if text is None:
            return None
        text = text.strip().casefold()
        if text == self._null_value:
            return None
        else:
            try:
                if self._thousand_separator:
                    text = text.replace(self._thousand_separator, "")
                return int(text)
            except ValueError as e:
                raise MetaCSVReadException(e)

    def to_string(self, value: Optional[float]) -> str:
        if value is None:
            return self._null_value
        return format_integer(value, self._thousand_separator)


class PercentageFieldProcessor(FieldProcessor[T]):
    def __init__(self, pre: Optional[bool], sign: Optional[str],
                 number_processor: FieldProcessor[T], null_value: str):
        self._pre = pre
        self._sign = sign
        self._number_processor = number_processor
        self._null_value = null_value

    def to_object(self, text: str) -> Optional[T]:
        text = text_or_none(text, self._null_value)
        if text is None:
            return None
        size = len(self._sign)
        if self._pre:
            if text.startswith(self._sign):
                text = text[size:].lstrip()
                return self._number_processor.to_object(
                    text) / self._number_processor.to_object("100.0")
            else:
                raise MetaCSVReadException(
                    f"Missing {self._sign} currency symbol: {text}")
        else:
            if text.endswith(self._sign):
                text = text[:-size].lstrip()
                return self._number_processor.to_object(
                    text) / self._number_processor.to_object("100.0")
            else:
                raise MetaCSVReadException(
                    f"Missing {self._sign} currency symbol: {text}")

    def to_string(self, value: Optional[T]) -> str:
        if value is None:
            return self._null_value
        v = self._number_processor.to_string(value)
        if self._pre:
            return f"{self._sign} {v}"
        else:
            return f"{v} {self._sign}"


class TextFieldProcessor(FieldProcessor[int]):
    def __init__(self, null_value: str):
        self._null_value = null_value

    def to_object(self, text: str) -> Optional[str]:
        return text_or_none(text, self._null_value)

    def to_string(self, value: Optional[str]) -> str:
        if value is None:
            return self._null_value
        else:
            return value
