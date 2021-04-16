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
from io import StringIO

from mcsv.meta_csv_data import MetaCSVDataBuilder
from mcsv.renderer import MetaCSVRenderer


class MetaCSVRendererTest(unittest.TestCase):
    def test_minimal(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter', ''],
                         dest.getvalue().split("\r\n"))

    def test_verbose(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest, False)
        data = MetaCSVDataBuilder().build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'file,encoding,UTF-8',
                          'file,line_terminator,\\r\\n',
                          'csv,delimiter,","',
                          'csv,double_quote,false',
                          'csv,escape_char,',
                          'csv,quote_char,""""',
                          'csv,skip_initial_space,false',
                          ''], dest.getvalue().split("\r\n"))


if __name__ == '__main__':
    unittest.main()
