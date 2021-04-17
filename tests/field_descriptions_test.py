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
from decimal import Decimal
from io import StringIO

from mcsv.field_descriptions import IntegerFieldDescription, \
    BooleanFieldDescription, CurrencyIntegerFieldDescription, \
    CurrencyDecimalFieldDescription, DecimalFieldDescription, \
    DateFieldDescription, DatetimeFieldDescription, FloatFieldDescription


class BooleanFieldDescriptionTest(unittest.TestCase):
    def test_render_boolean(self):
        s = StringIO()
        BooleanFieldDescription.INSTANCE.render(s)
        self.assertEqual("boolean/true/false", s.getvalue())

    def test_render_boolean_no_false(self):
        s = StringIO()
        BooleanFieldDescription("X", "").render(s)
        self.assertEqual("boolean/X", s.getvalue())

    def test_type(self):
        self.assertEqual(bool,
                         BooleanFieldDescription.INSTANCE.get_python_type())


class CurrencyDecimalFieldDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.description = CurrencyDecimalFieldDescription(
            False, "€", DecimalFieldDescription.INSTANCE)

    def test_render_currency(self):
        s = StringIO()
        self.description.render(s)
        self.assertEqual("currency/post/€/decimal//.", s.getvalue())

    def test_type(self):
        self.assertEqual(Decimal, self.description.get_python_type())

    def test_repr(self):
        self.assertEqual(("CurrencyDecimalFieldDescription("
                          "False, '€', DecimalFieldDescription(None, '.'))"),
                         repr(self.description))


class CurrencyIntegerFieldDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.description = CurrencyIntegerFieldDescription(
            False, "€", IntegerFieldDescription.INSTANCE)

    def test_render_currency(self):
        s = StringIO()
        self.description.render(s)
        self.assertEqual("currency/post/€/integer", s.getvalue())

    def test_type(self):
        self.assertEqual(int, self.description.get_python_type())

    def test_repr(self):
        self.assertEqual(("CurrencyIntegerFieldDescription("
                          "False, '€', IntegerFieldDescription.INSTANCE)"),
                         repr(self.description))


class DateFieldDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.description = DateFieldDescription("yyyy-MM-dd", "en_US.UTF-8")

    def test_render(self):
        s = StringIO()
        self.description.render(s)
        self.assertEqual("date/yyyy-MM-dd/en_US.UTF-8", s.getvalue())

    def test_render_no_locale(self):
        description = DateFieldDescription("yyyy-MM-dd")
        s = StringIO()
        description.render(s)
        self.assertEqual("date/yyyy-MM-dd", s.getvalue())

    def test_type(self):
        self.assertEqual(date, self.description.get_python_type())

    def test_repr(self):
        self.assertEqual("DateFieldDescription('yyyy-MM-dd', 'en_US.UTF-8')",
                         repr(self.description))

    def test_repr_no_locale(self):
        description = DateFieldDescription("yyyy-MM-dd")
        self.assertEqual("DateFieldDescription('yyyy-MM-dd')",
                         repr(description))


class DatetimeFieldDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.description = DatetimeFieldDescription("yyyy-MM-dd'T'HH:mm:ss",
                                                    "en_US.UTF-8")

    def test_render(self):
        s = StringIO()
        self.description.render(s)
        self.assertEqual("datetime/yyyy-MM-dd'T'HH:mm:ss/en_US.UTF-8",
                         s.getvalue())

    def test_render_no_locale(self):
        description = DatetimeFieldDescription("yyyy-MM-dd'T'HH:mm:ss")
        s = StringIO()
        description.render(s)
        self.assertEqual("datetime/yyyy-MM-dd'T'HH:mm:ss", s.getvalue())

    def test_type(self):
        self.assertEqual(datetime, self.description.get_python_type())

    def test_repr(self):
        self.assertEqual(("DatetimeFieldDescription("
                          "\"yyyy-MM-dd'T'HH:mm:ss\", 'en_US.UTF-8')"),
                         repr(self.description))

    def test_repr_no_locale(self):
        description = DatetimeFieldDescription("yyyy-MM-dd'T'HH:mm:ss")
        self.assertEqual("DatetimeFieldDescription(\"yyyy-MM-dd'T'HH:mm:ss\")",
                         repr(description))


class DecimalFieldDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.description = DecimalFieldDescription.INSTANCE

    def test_render(self):
        s = StringIO()
        self.description.render(s)
        self.assertEqual("decimal//.", s.getvalue())

    def test_type(self):
        self.assertEqual(Decimal, self.description.get_python_type())

    def test_repr(self):
        self.assertEqual("DecimalFieldDescription(None, '.')",
                         repr(self.description))


class FloatFieldDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.description = FloatFieldDescription.INSTANCE

    def test_render(self):
        s = StringIO()
        self.description.render(s)
        self.assertEqual("float//.", s.getvalue())

    def test_type(self):
        self.assertEqual(float, self.description.get_python_type())

    def test_repr(self):
        self.assertEqual("FloatFieldDescription(None, '.')",
                         repr(self.description))


class IntegerFieldDescriptionTest(unittest.TestCase):
    def setUp(self):
        self.description = IntegerFieldDescription.INSTANCE

    def test_render(self):
        s = StringIO()
        self.description.render(s)
        self.assertEqual("integer", s.getvalue())

    def test_render_ts(self):
        description = IntegerFieldDescription(",")
        s = StringIO()
        description.render(s)
        self.assertEqual("integer/,", s.getvalue())

    def test_type(self):
        self.assertEqual(int, IntegerFieldDescription().get_python_type())


if __name__ == '__main__':
    unittest.main()
