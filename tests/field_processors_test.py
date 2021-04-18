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

import unittest
from datetime import date, datetime, timezone
from decimal import Decimal

from mcsv.date_format_converter import _DateFormatParser
from mcsv.field_processors import (
    DateAndDatetimeFieldProcessor, ReadError, text_or_none,
    BooleanFieldProcessor, MetaCSVReadException,
    CurrencyFieldProcessor, IntegerFieldProcessor, DecimalFieldProcessor,
    FloatFieldProcessor, PercentageFieldProcessor, TextFieldProcessor)


class BooleanFieldProcessorTest(unittest.TestCase):
    def test_to_object_error(self):
        processor = BooleanFieldProcessor("true", "false", "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("foo")

    def test_to_string(self):
        processor = BooleanFieldProcessor("true", "false", "NULL")
        self.assertEqual("NULL", processor.to_string(None))


class CurrencyFieldProcessorTest(unittest.TestCase):
    def test_to_string_none(self):
        processor = CurrencyFieldProcessor(True, "$", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        self.assertEqual("NULL", processor.to_string(None))

    def test_to_object_none(self):
        processor = CurrencyFieldProcessor(True, "$", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        self.assertIsNone(processor.to_object(None))

    def test_to_object_err(self):
        processor = CurrencyFieldProcessor(True, "$", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("10€")

    def test_to_string(self):
        processor = CurrencyFieldProcessor(True, "$", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        self.assertEqual("$10", processor.to_string(10))

    def test_to_string_euro(self):
        processor = CurrencyFieldProcessor(False, "€", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        self.assertEqual("10 €", processor.to_string(10))


class DateAndDatetimeFieldProcessorTest(unittest.TestCase):
    def test_milliseconds(self):
        processor = DateAndDatetimeFieldProcessor(datetime.fromtimestamp,
                                                  _DateFormatParser.create().parse(
                                                      "yyyy-MM-dd'T'HH:mm:ss"),
                                                  "fr_FR.UTF8",
                                                  "null_value")
        self.assertEqual(datetime(2021, 1, 12, 15, 34, 25),
                         processor.to_object("2021-01-12T15:34:25.1235"))

    def test_hours(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  _DateFormatParser.create().parse(
                                                      "yyyy-MM-dd"),
                                                  "fr_FR.UTF8",
                                                  "null_value")
        self.assertEqual(date(2021, 1, 12),
                         processor.to_object("2021-01-12T15:34:25.1235"))

    def test_to_object_err(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  "yyyy-MM-dd", "fr_FR.utf-8",
                                                  "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("foo")

    def test_to_object_err_no_locale(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  "yyyy-MM-dd", None,
                                                  "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("foo")

    def test_to_string_none(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  "yyyy-MM-dd", "fr_FR.utf-8",
                                                  "NULL")
        self.assertEqual("NULL", processor.to_string(None))

    def test_to_string_locale(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  "%Y-%B-%d", "fr_FR.utf-8",
                                                  "NULL")
        d = datetime.fromtimestamp(1234567891).astimezone(timezone.utc).date()
        self.assertEqual("2009-février-13", processor.to_string(
            d))

    def test_to_string_no_locale_(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  "%Y-%m-%d", None,
                                                  "NULL")
        d = datetime.fromtimestamp(1234567891).astimezone(timezone.utc).date()
        self.assertEqual("2009-02-13", processor.to_string(d))

    def test_datetime_field_processor_locale_to_string(self):
        processor = DateAndDatetimeFieldProcessor(datetime.fromtimestamp,
                                                  "%Y-%B-%d", "fr_FR.utf-8",
                                                  "NULL")
        d = datetime.fromtimestamp(1234567891).astimezone(timezone.utc)
        self.assertEqual("2009-février-13", processor.to_string(
            d))


class DecimalFieldProcessorTest(unittest.TestCase):
    def test_to_object_none(self):
        processor = DecimalFieldProcessor(None, ".", "NULL")
        self.assertIsNone(processor.to_object(None))

    def test_to_object_null(self):
        processor = DecimalFieldProcessor(None, ".", "NULL")
        self.assertIsNone(processor.to_object("NULL"))

    def test_to_object_th_sep(self):
        processor = DecimalFieldProcessor(" ", ".", "NULL")
        self.assertEqual(Decimal('1234.5'), processor.to_object("1 234.5"))

    def test_to_object_dec_sep(self):
        processor = DecimalFieldProcessor(" ", ",", "NULL")
        self.assertEqual(Decimal('1234.5'), processor.to_object("1 234,5"))

    def test_to_object_err(self):
        processor = DecimalFieldProcessor(" ", ",", "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("foo")

    def test_to_string_none(self):
        processor = DecimalFieldProcessor(" ", ",", "NULL")
        self.assertEqual("NULL", processor.to_string(None))

    def test_string(self):
        processor = DecimalFieldProcessor(" ", ",", "NULL")
        self.assertEqual("1 234,5", processor.to_string(Decimal('1234.5')))


class FloatFieldProcessorTest(unittest.TestCase):
    def test_to_object_none(self):
        processor = FloatFieldProcessor(None, ".", "NULL")
        self.assertIsNone(processor.to_object(None))

    def test_to_object_null(self):
        processor = FloatFieldProcessor(None, ".", "NULL")
        self.assertIsNone(processor.to_object("NULL"))

    def test_to_object_th_sep(self):
        processor = FloatFieldProcessor(" ", ".", "NULL")
        self.assertEqual(1234.5, processor.to_object("1 234.5"))

    def test_to_object_dec_sep(self):
        processor = FloatFieldProcessor(" ", ",", "NULL")
        self.assertEqual(1234.5, processor.to_object("1 234,5"))

    def test_to_object_err(self):
        processor = FloatFieldProcessor(" ", ",", "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("foo")

    def test_to_string_none(self):
        processor = FloatFieldProcessor(" ", ",", "NULL")
        self.assertEqual("NULL", processor.to_string(None))

    def test_to_string(self):
        processor = FloatFieldProcessor(" ", ",", "NULL")
        self.assertEqual("1 234,5", processor.to_string(1234.5))


class IntegerFieldProcessorTest(unittest.TestCase):
    def test_to_object_none(self):
        processor = IntegerFieldProcessor(None, "NULL")
        self.assertIsNone(processor.to_object(None))

    def test_to_object_null(self):
        processor = IntegerFieldProcessor(None, "NULL")
        self.assertIsNone(processor.to_object("NULL"))

    def test_to_object_th_sep(self):
        processor = IntegerFieldProcessor(" ", "NULL")
        self.assertEqual(1234, processor.to_object("1 234"))

    def test_to_object(self):
        processor = IntegerFieldProcessor(None, "NULL")
        self.assertEqual(1234, processor.to_object("1234"))

    def test_to_object_err(self):
        processor = IntegerFieldProcessor(" ", "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("foo")

    def test_to_string_none(self):
        processor = IntegerFieldProcessor(" ", "NULL")
        self.assertEqual("NULL", processor.to_string(None))

    def test_to_string(self):
        processor = IntegerFieldProcessor(" ", "NULL")
        self.assertEqual("1 234", processor.to_string(1234))


class PercentageFieldProcessorTest(unittest.TestCase):
    def setUp(self):
        self.processor = PercentageFieldProcessor(
            False, "%", FloatFieldProcessor("", ".", "NULL"), "NULL")

    def test_to_object_none(self):
        self.assertIsNone(self.processor.to_object(None))

    def test_to_object_null(self):
        self.assertIsNone(self.processor.to_object("NULL"))

    def test_to_object(self):
        self.assertEqual(0.125, self.processor.to_object("12.5%"))

    def test_to_object_err(self):
        with self.assertRaises(MetaCSVReadException):
            self.processor.to_object("foo")

    def test_to_string_none(self):
        self.assertEqual("NULL", self.processor.to_string(None))

    def test_to_string(self):
        self.assertEqual("12.5 %", self.processor.to_string(0.125))

    def test_to_object_pre(self):
        processor = PercentageFieldProcessor(
            True, "%", FloatFieldProcessor("", ".", "NULL"), "NULL")
        self.assertEqual(0.125, processor.to_object("%12.5"))

    def test_to_object_pre_err(self):
        processor = PercentageFieldProcessor(
            True, "%", FloatFieldProcessor("", ".", "NULL"), "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("&12.5")

    def test_to_string_pre(self):
        processor = PercentageFieldProcessor(
            True, "%", FloatFieldProcessor("", ".", "NULL"), "NULL")
        self.assertEqual("% 12.5", processor.to_string(0.125))


class TextFieldProcessorTest(unittest.TestCase):
    def setUp(self):
        self.processor = TextFieldProcessor("NULL")

    def test_to_object_none(self):
        self.assertIsNone(self.processor.to_object(None))

    def test_to_object_null(self):
        self.assertIsNone(self.processor.to_object("NULL"))

    def test_to_object_th_sep(self):
        self.assertEqual("1234", self.processor.to_object("1234"))

    def test_to_object(self):
        self.assertEqual("1234", self.processor.to_object("1234"))

    def test_to_string_none(self):
        self.assertEqual("NULL", self.processor.to_string(None))

    def test_to_string(self):
        self.assertEqual("1234", self.processor.to_string("1234"))


class MiscTest(unittest.TestCase):
    def test_read_error_repr(self):
        self.assertEqual("ReadError(0, int)", repr(ReadError("0", "int")))

    def test_test_or_none(self):
        self.assertIsNone(text_or_none(None, "NULL"))


if __name__ == '__main__':
    unittest.main()
