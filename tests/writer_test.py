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
import csv
import unittest
from decimal import Decimal
from io import StringIO, BytesIO

from mcsv.field_descriptions import DecimalFieldDescription, \
    IntegerFieldDescription
from mcsv.meta_csv_data import MetaCSVDataBuilder
from mcsv.writer import MetaCSVWriterFactory, open_csv_writer


class WriterTest(unittest.TestCase):
    def test_writer(self):
        s = StringIO()
        data = (MetaCSVDataBuilder()
                .description_by_col_index(1, DecimalFieldDescription.INSTANCE)
                .description_by_col_index(2, IntegerFieldDescription.INSTANCE)
                .build())
        w = MetaCSVWriterFactory(data).writer(s)
        w.writeheader(['a', 'b', 'c'])
        w.writerow(['1', Decimal('2.0'), 3])
        self.assertEqual(['a,b,c', '1,2.0,3', ''], s.getvalue().split("\r\n"))

    def test_dict_writer(self):
        s = StringIO()
        data = (MetaCSVDataBuilder()
                .description_by_col_index(1, DecimalFieldDescription.INSTANCE)
                .description_by_col_index(2, IntegerFieldDescription.INSTANCE)
                .build())
        w = MetaCSVWriterFactory(data).dict_writer(s, ['a', 'b', 'c'])
        w.writerow({'a': '1', 'b': Decimal('2.0'), 'c': 3})
        self.assertEqual(['a,b,c', '1,2.0,3', ''], s.getvalue().split("\r\n"))

    def test_writer_bom(self):
        s = BytesIO()
        ms = BytesIO()
        data = (MetaCSVDataBuilder()
                .description_by_col_index(1, DecimalFieldDescription.INSTANCE)
                .description_by_col_index(2, IntegerFieldDescription.INSTANCE)
                .bom(True)
                .build())
        with open_csv_writer(s, data, ms) as w:
            w.writeheader(['a', 'b', 'c'])
            w.writerow(['1', Decimal('2.0'), 3])
            # see https://stackoverflow.com/questions/48434423/
            # why-is-textiowrapper-closing-the-given-bytesio-stream
            self.assertEqual((b'domain,key,delimiter\r\n'
                              b'file,bom,true\r\n'
                              b'data,col/1/type,decimal//.\r\n'
                              b'data,col/2/type,integer\r\n'), ms.getvalue())

        self.assertEqual(b'a,b,c\r\n1,2.0,3\r\n', s.getvalue())


if __name__ == '__main__':
    unittest.main()
