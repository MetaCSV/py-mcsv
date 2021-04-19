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

from mcsv.field_description import (DataType, data_type_to_python_type,
                                    python_type_to_data_type)


class FieldDescriptionTest(unittest.TestCase):
    def test_to_python_type(self):
        self.assertEqual(Decimal, data_type_to_python_type(
            DataType.PERCENTAGE_DECIMAL))

    def test_to_data_type(self):
        self.assertEqual(DataType.DECIMAL, python_type_to_data_type(Decimal))


if __name__ == '__main__':
    unittest.main()
