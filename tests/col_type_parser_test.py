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

from mcsv.col_type_parser import ColTypeParser
from mcsv.field_descriptions import TextFieldDescription, \
    BooleanFieldDescription


class ColTypeParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = ColTypeParser(
            lambda parameters: TextFieldDescription.INSTANCE)

    def test_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("foo")

    def test_bool(self):
        self.assertEqual("BooleanFieldDescription('T', '')",
                         repr(self.parser.parse_col_type("boolean/T")))

    def test_boolean_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("boolean/True/False/Maybe")

    def test_currency_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("currency")

    def test_currency_prepost_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("currency/foo/€/decimal//.")

    def test_currency_number_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("currency/pre/€/float//.")

    def test_date_locale_wo_encoding(self):
        self.assertEqual("DateFieldDescription('%Y-%m-%d', 'en_US.utf8')",
                         repr(self.parser.parse_col_type(
                             "date/yyyy-MM-dd/en_US")))

    def test_date_locale_w_encoding(self):
        self.assertEqual("DateFieldDescription('%Y-%m-%d', 'en_US.utf8')",
                         repr(self.parser.parse_col_type(
                             "date/yyyy-MM-dd/en_US.utf8")))

    def test_date_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("date/yyyy-MM-dd/en_US.utf8/foo")

    def test_float_double_space(self):
        self.assertEqual("FloatFieldDescription('  ', '.')",
                         repr(self.parser.parse_col_type(
                             "float/  /.")))

    def test_float_strip(self):
        self.assertEqual("FloatFieldDescription('', '.')",
                         repr(self.parser.parse_col_type(
                             "float// .")))

    def test_float_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("float/./.")

    def test_float_error_param_count(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("float/././foo")

    def test_decimal_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("decimal/./.")

    def test_decimal_error_param_count(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("decimal/././foo")

    def test_percentage_error_param_count(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("percentage/foo")

    def test_percentage_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("percentage/post/%/integer")

    def test_integer_error(self):
        with self.assertRaises(ValueError):
            self.parser.parse_col_type("integer//foo")

    def test_integer_th_sep(self):
        self.assertEqual("IntegerFieldDescription(' ')",
                         repr(self.parser.parse_col_type("integer/ ")))


if __name__ == '__main__':
    unittest.main()
