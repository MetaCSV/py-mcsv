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
from io import BytesIO

from mcsv.parser import MetaCSVParser


class ParserTest(unittest.TestCase):
    def test_header_err(self):
        with self.assertRaises(ValueError):
            MetaCSVParser(BytesIO(b"domain,key,valu")).parse()

    def test_domain_err(self):
        with self.assertRaises(ValueError):
            MetaCSVParser(BytesIO(b"domain,key,value\r\nfoo,bar,baz")).parse()

    def test_basic(self):
        data = MetaCSVParser(BytesIO(b"domain,key,value")).parse()
        self.assertEqual("UTF-8", data.encoding)

    def test_meta(self):
        data = MetaCSVParser(
            BytesIO(b"domain,key,value\r\nmeta,bar,baz")).parse()
        self.assertEqual({'bar': 'baz'}, data.meta)

    def test_file_err(self):
        with self.assertRaises(ValueError):
            MetaCSVParser(BytesIO(b"domain,key,value\r\nfile,bar,baz")).parse()

    def test_csv_err(self):
        with self.assertRaises(ValueError):
            MetaCSVParser(BytesIO(b"domain,key,value\r\ncsv,bar,baz")).parse()

    def test_escape_char(self):
        data = MetaCSVParser(BytesIO(
            b"domain,key,value\r\ncsv,escape_char,\"\"\"\"")).parse()
        self.assertEqual('"', data.dialect.escapechar)

    def test_skip(self):
        data = MetaCSVParser(BytesIO(
            b"domain,key,value\r\ncsv,skip_initial_space,true")).parse()
        self.assertTrue(data.dialect.skipinitialspace)

    def test_data_err(self):
        with self.assertRaises(ValueError):
            MetaCSVParser(BytesIO(b"domain,key,value\r\ndata,bar,baz")).parse()

    def test_data_col_err(self):
        with self.assertRaises(ValueError):
            MetaCSVParser(
                BytesIO(b"domain,key,value\r\ndata,col/1,baz")).parse()

    def test_data_col_n_err(self):
        with self.assertRaises(ValueError):
            MetaCSVParser(
                BytesIO(b"domain,key,value\r\ndata,col/1/bar,baz")).parse()


if __name__ == '__main__':
    unittest.main()
