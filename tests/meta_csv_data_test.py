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
from decimal import Decimal

from mcsv.field_description import DataType
from mcsv.field_descriptions import DecimalFieldDescription, \
    TextFieldDescription
from mcsv.meta_csv_data import MetaCSVDataBuilder


class MetaCSVDataTest(unittest.TestCase):
    def test_meta(self):
        b = MetaCSVDataBuilder()
        b.meta("foo", "bar")
        data = b.build()
        self.assertEqual({'foo': 'bar'}, data.meta)

    def test_bom(self):
        b = MetaCSVDataBuilder()
        b.bom(True)
        data = b.build()
        self.assertTrue(data.bom)

    def test_escape(self):
        b = MetaCSVDataBuilder()
        b.escape_char('"')
        data = b.build()
        self.assertEqual('"', data.dialect.escapechar)

    def test_skip(self):
        b = MetaCSVDataBuilder()
        b.skip_initial_space(True)
        data = b.build()
        self.assertTrue(data.dialect.skipinitialspace)

    def test_to_meta_data(self):
        b = MetaCSVDataBuilder()
        b.description_by_col_index(1, DecimalFieldDescription.INSTANCE)
        meta_data = b.to_metadata()

        self.assertEqual(DataType.TEXT, meta_data.get_data_type(0))
        self.assertEqual(DataType.DECIMAL, meta_data.get_data_type(1))

        self.assertEqual(str, meta_data.get_python_type(0))
        self.assertEqual(Decimal, meta_data.get_python_type(1))

        self.assertEqual(TextFieldDescription.INSTANCE,
                         meta_data.get_description(0))
        self.assertEqual(DecimalFieldDescription.INSTANCE,
                         meta_data.get_description(1))


if __name__ == '__main__':
    unittest.main()
