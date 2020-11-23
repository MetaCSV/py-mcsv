# coding: utf-8

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
from datetime import datetime

from mcsv.parser import get_interpreter


class ParserTest(unittest.TestCase):
    def test(self):
        reader = get_interpreter("test/fixtures/meta_csv.mcsv").dict_reader(
            "test/fixtures/meta_csv.mcsv", False)
        self.assertEqual({'domain': 'text', 'key': 'text', 'value': 'text'},
                         next(reader))
        self.assertEqual(
            {'domain': 'file', 'key': 'encoding', 'value': 'utf-8'},
            next(reader))

    def test2(self):
        reader = get_interpreter(
            "test/fixtures/20201001-bal-216402149.mcsv").dict_reader(
            "test/fixtures/20201001-bal-216402149.csv", False)
        self.assertEqual({'cle_interop': 'text',
                          'commune_nom': 'text',
                          'complement': 'text',
                          'date_der_maj': 'date/yyyy-MM-dd',
                          'lat': 'float//.',
                          'long': 'float//.',
                          'numero': 'integer',
                          'position': 'text',
                          'refparc': 'text',
                          'source': 'text',
                          'suffixe': 'text',
                          'uid_adresse': 'text',
                          'voie_nom': 'text',
                          'voie_nom_eu': 'text',
                          'x': 'float//.',
                          'y': 'float//.'},
                         next(reader))
        self.assertEqual(
            {'cle_interop': '64214_0010_00700',
             'commune_nom': 'Espès-undurein',
             'complement': '',
             'date_der_maj': datetime(2020, 6, 11, 0, 0, 0).timetuple(),
             'lat': 43.28315047649357,
             'long': -0.8748110149745267,
             'numero': 700,
             'position': 'entrée',
             'refparc': 'ZB0188',
             'source': 'Commune de Espès-undurein',
             'suffixe': '',
             'uid_adresse': '',
             'voie_nom': 'Route du Pays de Soule',
             'voie_nom_eu': 'Xiberoko errepidea',
             'x': 385432.96,
             'y': 6250383.75},
            next(reader))


if __name__ == "__main__":
    unittest.main()
