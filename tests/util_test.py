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
from pathlib import Path

from mcsv.util import split_parameters, escape_line_terminator, \
    unescape_line_terminator, render, render_escaped, format_decimal, \
    format_integer, to_meta_path, open_file_like


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

    def test_split(self):
        self.assertEqual(["foo", "bar"],
                         split_parameters("foo/bar"))

    def test_split_empty_parameter(self):
        self.assertEqual(["foo", "", "bar"],
                         split_parameters("foo//bar"))

    def test_split_one(self):
        self.assertEqual(["foo"],
                         split_parameters("foo"))

    def test_split_zero(self):
        self.assertEqual([""],
                         split_parameters(""))

    def test_render_escaped(self):
        s = StringIO()
        render_escaped(s, "a / and a \\ ")
        self.assertEqual("a \\/ and a \\\\ ", s.getvalue())

    def test_format_decimal(self):
        self.assertEqual("123456.789", format_decimal(123456.789, None, None))

    def test_format_decimal_th_sep_dec_sep(self):
        self.assertEqual("123~456,789", format_decimal(123456.789, "~", ","))

    def test_format_decimal_th_sep(self):
        self.assertEqual("123~456", format_decimal(123456, "~", None))

    def test_format_int_th_sep(self):
        self.assertEqual("1", format_integer(1, "~"))
        self.assertEqual("12", format_integer(12, "~"))
        self.assertEqual("123", format_integer(123, "~"))
        self.assertEqual("1~234", format_integer(1234, "~"))
        self.assertEqual("12~345", format_integer(12345, "~"))
        self.assertEqual("123~456", format_integer(123456, "~"))
        self.assertEqual("1~234~567", format_integer(1234567, "~"))

    def test_format_neg_int_th_sep(self):
        self.assertEqual("-1", format_integer(-1, "~"))
        self.assertEqual("-12", format_integer(-12, "~"))
        self.assertEqual("-123", format_integer(-123, "~"))
        self.assertEqual("-1~234", format_integer(-1234, "~"))
        self.assertEqual("-12~345", format_integer(-12345, "~"))
        self.assertEqual("-123~456", format_integer(-123456, "~"))
        self.assertEqual("-1~234~567", format_integer(-1234567, "~"))

    def test_to_meta_path(self):
        self.assertEqual(Path("foo.mcsv"), to_meta_path("foo.csv"))
        self.assertEqual(Path("foo.mcsv"), to_meta_path(Path("foo.csv")))

    def test_to_meta_path_err(self):
        with self.assertRaises(ValueError):
            to_meta_path(1)

    def test_open_file_like(self):
        s = StringIO()
        with open_file_like(s) as f:
            self.assertEqual(s, f)

    def test_open_file_like_err(self):
        with self.assertRaises(ValueError):
            with open_file_like(1):
                pass


if __name__ == "__main__":
    unittest.main()
