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

from mcsv.field_descriptions import IntegerFieldDescription, \
    TextFieldDescription
from mcsv.meta_csv_data import MetaCSVDataBuilder
from mcsv.renderer import MetaCSVRenderer, open_renderer


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
                          'file,bom,false',
                          'file,line_terminator,\\r\\n',
                          'csv,delimiter,","',
                          'csv,double_quote,false',
                          'csv,escape_char,',
                          'csv,quote_char,""""',
                          'csv,skip_initial_space,false',
                          ''], dest.getvalue().split("\r\n"))

    def test_utf8_sig(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest, False)
        data = MetaCSVDataBuilder().encoding("utf-8-sig").build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'file,encoding,utf-8',
                          'file,bom,true',
                          'file,line_terminator,\\r\\n',
                          'csv,delimiter,","',
                          'csv,double_quote,false',
                          'csv,escape_char,',
                          'csv,quote_char,""""',
                          'csv,skip_initial_space,false',
                          ''], dest.getvalue().split("\r\n"))

    def test_utf8_sig_minimal(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().encoding("utf-8-sig").build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'file,bom,true',
                          ''], dest.getvalue().split("\r\n"))

    def test_iso(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest, False)
        data = MetaCSVDataBuilder().encoding("ISO-8859-1").build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'file,encoding,ISO-8859-1',
                          'file,bom,false',
                          'file,line_terminator,\\r\\n',
                          'csv,delimiter,","',
                          'csv,double_quote,false',
                          'csv,escape_char,',
                          'csv,quote_char,""""',
                          'csv,skip_initial_space,false',
                          ''], dest.getvalue().split("\r\n"))

    def test_iso_minimal(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().encoding("ISO-8859-1").build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'file,encoding,ISO-8859-1',
                          ''], dest.getvalue().split("\r\n"))

    def test_bom(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest, False)
        data = MetaCSVDataBuilder().bom(True).build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'file,encoding,UTF-8',
                          'file,bom,true',
                          'file,line_terminator,\\r\\n',
                          'csv,delimiter,","',
                          'csv,double_quote,false',
                          'csv,escape_char,',
                          'csv,quote_char,""""',
                          'csv,skip_initial_space,false',
                          ''], dest.getvalue().split("\r\n"))

    def test_bom_minimal(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().bom(True).build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'file,bom,true',
                          ''], dest.getvalue().split("\r\n"))

    def test_line_terminator(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().line_terminator("\n").build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'file,line_terminator,\\n',
                          ''], dest.getvalue().split("\r\n"))

    def test_delimiter(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().delimiter(";").build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'csv,delimiter,;',
                          ''], dest.getvalue().split("\r\n"))

    def test_double_quote(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().double_quote(False).build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'csv,double_quote,false',
                          ''], dest.getvalue().split("\r\n"))

    def test_escape_char(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().escape_char("~").build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'csv,escape_char,~',
                          ''], dest.getvalue().split("\r\n"))

    def test_quote_char(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().quote_char("'").build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          "csv,quote_char,'",
                          ''], dest.getvalue().split("\r\n"))

    def test_skip_initial_spaces(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().skip_initial_space(True).build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'csv,skip_initial_space,true',
                          ''], dest.getvalue().split("\r\n"))

    def test_col(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest)
        data = MetaCSVDataBuilder().description_by_col_index(
            0, TextFieldDescription.INSTANCE).description_by_col_index(
            1, IntegerFieldDescription.INSTANCE).build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'data,col/1/type,integer',
                          ''], dest.getvalue().split("\r\n"))

    def test_col_verbose(self):
        dest = StringIO()
        renderer = MetaCSVRenderer.create(dest, False)
        data = MetaCSVDataBuilder().description_by_col_index(
            0, TextFieldDescription.INSTANCE).description_by_col_index(
            1, IntegerFieldDescription.INSTANCE).build()
        renderer.write(data)
        self.assertEqual(['domain,key,delimiter',
                          'file,encoding,UTF-8',
                          'file,bom,false',
                          'file,line_terminator,\\r\\n',
                          'csv,delimiter,","',
                          'csv,double_quote,false',
                          'csv,escape_char,',
                          'csv,quote_char,""""',
                          'csv,skip_initial_space,false',
                          'data,col/0/type,text',
                          'data,col/1/type,integer',
                          ''], dest.getvalue().split("\r\n"))

    def test_open_renderer(self):
        s = StringIO()
        data = MetaCSVDataBuilder().description_by_col_index(
            0, TextFieldDescription.INSTANCE).description_by_col_index(
            1, IntegerFieldDescription.INSTANCE).build()
        with open_renderer(s) as r:
            r.write(data)

        self.assertEqual(['domain,key,delimiter',
                          'data,col/1/type,integer',
                          ''], s.getvalue().split("\r\n"))


if __name__ == '__main__':
    unittest.main()
