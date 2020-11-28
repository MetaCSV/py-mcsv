# coding: utf-8

import datetime
#  py-mcsv - A MetaCSV library for Python
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
import io
import os
import unittest

from mcsv.parser import get_interpreter, open_dict_csv


class ParserTest(unittest.TestCase):
    def test_meta(self):
        reader = get_interpreter(
            self._get_fixture("meta_csv.mcsv")).dict_reader(
            self._get_fixture("meta_csv.mcsv"), False)
        self.assertEqual({'domain': 'text', 'key': 'text', 'value': 'text'},
                         next(reader))
        self.assertEqual(
            {'domain': 'file', 'key': 'encoding', 'value': 'utf-8'},
            next(reader))

    def test_bal(self):
        reader = open_dict_csv(self._get_fixture("20201001-bal-216402149.csv"),
                               skip_types=False)
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
             'date_der_maj': datetime.date(2020, 6, 11),
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

    def test_self_contained_no_types(self):
        reader = open_dict_csv(self._get_fixture("example.csv"))
        self.assertEqual(
            [{'count': 15, 'date': datetime.date(2020, 11, 21),
              'name': 'foo'},
             {'count': -8, 'date': datetime.date(2020, 11, 22),
              'name': 'foo'}],
            list(reader))

    def _get_fixture(self, fixture_name: str) -> str:
        return os.path.abspath(
            os.path.join(__file__, "../fixtures", fixture_name))


if __name__ == "__main__":
    unittest.main()
