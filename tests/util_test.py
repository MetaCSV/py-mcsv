# coding: utf-8

#  py-mcsv - A MetaCSV library for Python
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

from mcsv.util import split_parameters, escape_line_terminator, \
    unescape_line_terminator, render


class UtilTest(unittest.TestCase):
    def test(self):
        self.assertEqual(['DD/mm/yyyy', 'locale'], split_parameters(
            "DD\\/mm\\/yyyy/locale"))

    def test_bs(self):
        self.assertEqual(['DD\\mm\\yyyy', 'locale'], split_parameters(
            "DD\\mm\\yyyy/locale"))

    def test_line_terminator(self):
        raw = ["\n", "\r\n", "\r", "~"]
        escaped = ["\\n", "\\r\\n", "\\r", "~"]
        for r, e in zip(raw, escaped):
            self.assertEqual(e, escape_line_terminator(r))
            self.assertEqual(r, unescape_line_terminator(e))

    def test_render0(self):
        s = StringIO()
        render(s)
        self.assertEqual("", s.getvalue())

    def test_render1(self):
        s = StringIO()
        render(s, "foo")
        self.assertEqual("foo", s.getvalue())

    def test_render2(self):
        s = StringIO()
        render(s, "foo", "bar")
        self.assertEqual("foo/bar", s.getvalue())

    def test_render3(self):
        s = StringIO()
        render(s, "foo", "bar", "baz")
        self.assertEqual("foo/bar/baz", s.getvalue())

    def test_render_blanks(self):
        s = StringIO()
        render(s, "foo", "", "")
        self.assertEqual("foo", s.getvalue())

    def test_render_only_blanks(self):
        s = StringIO()
        render(s, "", "", "")
        self.assertEqual("", s.getvalue())


if __name__ == "__main__":
    unittest.main()
