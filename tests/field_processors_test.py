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
from time import mktime

from mcsv.date_format_converter import _DateFormatParser
from mcsv.field_processors import DateAndDatetimeFieldProcessor


class DateAndDatetimeFieldProcessorTest(unittest.TestCase):
    def test_milliseconds(self):
        processor = DateAndDatetimeFieldProcessor(datetime.fromtimestamp,
                                             _DateFormatParser.create().parse("yyyy-MM-dd'T'HH:mm:ss"),
                                             "fr_FR.UTF8", "null_value")
        self.assertEqual(datetime(2021, 1, 12, 15, 34, 25), processor.to_object("2021-01-12T15:34:25.1235"))

    def test_hours(self):
        processor = DateAndDatetimeFieldProcessor(date.fromtimestamp,
                                             _DateFormatParser.create().parse("yyyy-MM-dd"),
                                             "fr_FR.UTF8", "null_value")
        self.assertEqual(date(2021, 1, 12), processor.to_object("2021-01-12T15:34:25.1235"))


if __name__ == '__main__':
    unittest.main()
