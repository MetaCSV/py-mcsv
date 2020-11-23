#  py-mcsv - A MetaCSV parser for Python
#      Copyright (C) 2020 J. Férard <https://github.com/jferard>
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

from mcsv.date_format_converter import _DateFormatParser, Token, OpCode


class DateFormatConverterTest(unittest.TestCase):
    def test_lex_iso(self):
        self.assertEqual([
            Token(OpCode.FIELD, 'yyyy'), Token(OpCode.TEXT, '-'),
            Token(OpCode.FIELD, 'MM'), Token(OpCode.TEXT, '-'),
            Token(OpCode.FIELD, 'dd'), Token(OpCode.TEXT, 'T'),
            Token(OpCode.FIELD, 'HH'), Token(OpCode.TEXT, ':'),
            Token(OpCode.FIELD, 'mm'), Token(OpCode.TEXT, ':'),
            Token(OpCode.FIELD, 'ss'), Token(OpCode.TEXT, ','),
            Token(OpCode.FIELD, 'SSSS'), Token(OpCode.FIELD, 'Z')],
            list(_DateFormatParser.lex("yyyy-MM-dd'T'HH:mm:ss,SSSSZ")))

    def test_lex_quote(self):
        self.assertEqual(
            [Token(OpCode.TEXT, "'"), Token(OpCode.FIELD, 'yy'),
             Token(OpCode.TEXT, '/'), Token(OpCode.FIELD, 'MM'),
             Token(OpCode.TEXT, '/'), Token(OpCode.FIELD, 'dd')],
            list(_DateFormatParser.lex("''yy/MM/dd")))

    def test_parse_iso(self):
        self.assertEqual("%Y-%m-%dT%H:%M:%S,%f%Z",
                         _DateFormatParser.create().parse(
                             "yyyy-MM-dd'T'HH:mm:ss,SSSSZ"))

    def test_parse_quote(self):
        self.assertEqual("'%y/%m/%d",
                         _DateFormatParser.create().parse("''yy/MM/dd"))

    def test_parse_percent(self):
        self.assertEqual("%y%%%m%%%d",
                         _DateFormatParser.create().parse("yy%MM%dd"))


if __name__ == '__main__':
    unittest.main()
