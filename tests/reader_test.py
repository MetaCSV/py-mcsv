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
from io import StringIO

from mcsv import MetaCSVReader
from mcsv.field_description import DataType
from mcsv.field_descriptions import TextFieldDescription, \
    DecimalFieldDescription, IntegerFieldDescription
from mcsv.meta_csv_data import MetaCSVDataBuilder
from mcsv.reader import MetaCSVReaderFactory


class ReaderTest(unittest.TestCase):
    def setUp(self):
        data = (MetaCSVDataBuilder()
                .description_by_col_index(1, DecimalFieldDescription.INSTANCE)
                .description_by_col_index(2, IntegerFieldDescription.INSTANCE)
                .build())
        s = StringIO("a,b,c\r\n1,2,3")
        self.reader = MetaCSVReaderFactory(data).reader(s)

    def test_reader_rows(self):
        it = iter(self.reader)
        self.assertEqual(['a', 'b', 'c'], next(it))
        self.assertEqual(['1', Decimal('2'), 3], next(it))
        with self.assertRaises(StopIteration):
            next(it)

    def test_reader_data(self):
        self.assertEqual([DataType.TEXT, DataType.DECIMAL, DataType.INTEGER],
                         self.reader.get_data_types())

    def test_reader_python(self):
        self.assertEqual([str, Decimal, int], self.reader.get_python_types())


class DictReaderTest(unittest.TestCase):
    def setUp(self):
        data = (MetaCSVDataBuilder()
                .description_by_col_index(1, DecimalFieldDescription.INSTANCE)
                .description_by_col_index(2, IntegerFieldDescription.INSTANCE)
                .build())
        s = StringIO("a,b,c\r\n1,2,3,4")
        self.reader = MetaCSVReaderFactory(data).dict_reader(s)

    def test_reader_rows(self):
        it = iter(self.reader)
        self.assertEqual({'a': '1', 'b': Decimal('2'), 'c': 3, '@other': ['4']},
                         next(it))
        with self.assertRaises(StopIteration):
            next(it)

    def test_reader_data(self):
        self.assertEqual(
            {'a': DataType.TEXT, 'b': DataType.DECIMAL, 'c': DataType.INTEGER},
            self.reader.get_data_types())

    def test_reader_python(self):
        self.assertEqual({'a': str, 'b': Decimal, 'c': int},
                         self.reader.get_python_types())


if __name__ == '__main__':
    unittest.main()
