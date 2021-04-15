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
from datetime import date, datetime
from time import mktime

from mcsv.date_format_converter import _DateFormatParser
from mcsv.field_processors import (
    DateAndDatetimeFieldProcessor, ReadError, text_or_none,
    BooleanFieldProcessor, MetaCSVReadException,
    CurrencyFieldProcessor, IntegerFieldProcessor)


class DateAndDatetimeFieldProcessorTest(unittest.TestCase):
    def test_milliseconds(self):
        processor = DateAndDatetimeFieldProcessor(datetime.fromtimestamp,
                                                  _DateFormatParser.create().parse(
                                                      "yyyy-MM-dd'T'HH:mm:ss"),
                                                  "fr_FR.UTF8", "null_value")
        self.assertEqual(datetime(2021, 1, 12, 15, 34, 25),
                         processor.to_object("2021-01-12T15:34:25.1235"))

    def test_hours(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  _DateFormatParser.create().parse(
                                                      "yyyy-MM-dd"),
                                                  "fr_FR.UTF8", "null_value")
        self.assertEqual(date(2021, 1, 12),
                         processor.to_object("2021-01-12T15:34:25.1235"))

    def test_read_error_repr(self):
        self.assertEqual("ReadError(0, int)", repr(ReadError(0, "int")))

    def test_test_or_none(self):
        self.assertIsNone(text_or_none(None, "NULL"))

    def test_boolean_field_processor_error(self):
        processor = BooleanFieldProcessor("true", "false", "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("foo")

    def test_boolean_field_processor(self):
        processor = BooleanFieldProcessor("true", "false", "NULL")
        self.assertEqual("NULL", processor.to_string(None))

    def test_currency_field_processor(self):
        processor = CurrencyFieldProcessor(True, "$", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        self.assertEqual("NULL", processor.to_string(None))

    def test_currency_field_processor_err(self):
        processor = CurrencyFieldProcessor(True, "$", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("10€")

    def test_currency_field_processor2(self):
        processor = CurrencyFieldProcessor(True, "$", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        self.assertIsNone(processor.to_object(None))

    def test_currency_field_processor3(self):
        processor = CurrencyFieldProcessor(True, "$", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        self.assertEqual("$10", processor.to_string(10))

    def test_currency_field_processor4(self):
        processor = CurrencyFieldProcessor(False, "€", IntegerFieldProcessor(
            None, "NULL"), "NULL")
        self.assertEqual("10 €", processor.to_string(10))

    def test_date_field_processor_err(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  "yyyy-MM-dd", "fr_FR.utf-8",
                                                  "NULL")
        with self.assertRaises(MetaCSVReadException):
            processor.to_object("foo")

    def test_date_field_processor_none_to_string(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  "yyyy-MM-dd", "fr_FR.utf-8",
                                                  "NULL")
        self.assertEqual("NULL", processor.to_string(None))

    def test_date_field_processor_locale_to_string(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  "%Y-%B-%d", "fr_FR.utf-8",
                                                  "NULL")
        self.assertEqual("2009-février-14", processor.to_string(
            date.fromtimestamp(1234567891)))

    def test_date_field_processor_no_locale_to_string(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                                  "%Y-%m-%d", None,
                                                  "NULL")
        self.assertEqual("2009-02-14", processor.to_string(
            date.fromtimestamp(1234567891)))


if __name__ == '__main__':
    unittest.main()
