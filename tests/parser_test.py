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
import datetime
import os
import unittest
import urllib.request
from decimal import Decimal
from typing import (TextIO, Optional, List, Type)
from urllib.parse import ParseResult, urlparse

from mcsv.field_description import FieldDescription, DataType
from mcsv.field_descriptions import TextFieldDescription
from mcsv.field_processor import FieldProcessor
from mcsv.field_processors import text_or_none, ReadError
from mcsv.reader import open_dict_csv_reader
from mcsv.util import T, render


class ParserTest(unittest.TestCase):
    def test_meta(self):
        with open_dict_csv_reader(self._get_fixture("meta_csv.mcsv"),
                                  self._get_fixture("meta_csv.mcsv")) as reader:
            self.assertEqual({'domain': DataType.TEXT, 'key': DataType.TEXT,
                              'value': DataType.TEXT},
                             reader.get_data_types())
            self.assertEqual(
                {'domain': 'file', 'key': 'encoding', 'value': 'utf-8'},
                next(reader))

    def test_bal(self):
        with open_dict_csv_reader(
                self._get_fixture("20201001-bal-216402149.csv")) as reader:
            self.assertEqual({
                'cle_interop': DataType.TEXT,
                'commune_nom': DataType.TEXT,
                'complement': DataType.TEXT,
                'date_der_maj': DataType.DATE,
                'lat': DataType.FLOAT,
                'long': DataType.FLOAT,
                'numero': DataType.INTEGER,
                'position': DataType.TEXT,
                'refparc': DataType.TEXT,
                'source': DataType.TEXT,
                'suffixe': DataType.TEXT,
                'uid_adresse': DataType.TEXT,
                'voie_nom': DataType.TEXT,
                'voie_nom_eu': DataType.TEXT,
                'x': DataType.FLOAT,
                'y': DataType.FLOAT
            }, reader.get_data_types())
            self.assertEqual(
                {'cle_interop': '64214_0010_00700',
                 'commune_nom': 'Espès-undurein',
                 'complement': None,
                 'date_der_maj': datetime.date(2020, 6, 11),
                 'lat': 43.28315047649357,
                 'long': -0.8748110149745267,
                 'numero': 700,
                 'position': 'entrée',
                 'refparc': 'ZB0188',
                 'source': 'Commune de Espès-undurein',
                 'suffixe': None,
                 'uid_adresse': None,
                 'voie_nom': 'Route du Pays de Soule',
                 'voie_nom_eu': 'Xiberoko errepidea',
                 'x': 385432.96,
                 'y': 6250383.75},
                next(reader))

    def test_self_contained_no_types(self):
        with open_dict_csv_reader(self._get_fixture("example.csv")) as reader:
            self.assertEqual(
                [{'count': 15, 'date': datetime.date(2020, 11, 21),
                  'name': 'foo'},
                 {'count': -8, 'date': datetime.date(2020, 11, 22),
                  'name': 'foo'}],
                list(reader))

    def _get_fixture(self, fixture_name: str) -> str:
        return os.path.abspath(
            os.path.join(__file__, "../fixtures", fixture_name))

    def test_fixture1(self):
        class URLFieldProcessor(FieldProcessor[ParseResult]):
            def __init__(self, null_value: str):
                self._null_value = null_value

            def to_object(self, text: str) -> Optional[ParseResult]:
                text = text_or_none(text, self._null_value)
                if text is None:
                    return None
                return urlparse(text)

            def to_string(self, value: Optional[ParseResult]) -> str:
                return value.geturl()

        class URLFieldDescription(FieldDescription[ParseResult]):
            def render(self, out: TextIO):
                render(out, "object", "url")

            def to_field_processor(self, null_value: str) -> FieldProcessor[T]:
                return URLFieldProcessor(null_value)

            def get_data_type(self) -> DataType:
                return DataType.OBJECT

            def get_python_type(self) -> Type:
                return ParseResult

            def __repr__(self):
                return "URLFieldDescription()"

        def create_object_description(
                parameters: List[str]) -> FieldDescription:
            if len(parameters) == 1 and parameters[0] == "URL":
                return URLFieldDescription()
            else:
                return TextFieldDescription.INSTANCE

        examples_dir = ("https://raw.githubusercontent.com/"
                        "MetaCSV/MetaCSV/main/examples/")
        with urllib.request.urlopen(
                examples_dir + "example1.mcsv") as mcsv_source, \
                urllib.request.urlopen(
                    examples_dir + "example1.csv") as csv_source:

            with open_dict_csv_reader(csv_source, mcsv_source,
                                      create_object_description,
                                      on_error="wrap") as reader:
                self.assertEqual({
                    'a boolean': DataType.BOOLEAN,
                    'a currency': DataType.CURRENCY_INTEGER,
                    'another currency': DataType.CURRENCY_DECIMAL,
                    'a date': DataType.DATE,
                    'a datetime': DataType.DATETIME,
                    'a decimal': DataType.DECIMAL,
                    'a float': DataType.FLOAT,
                    'an integer': DataType.INTEGER,
                    'a percentage': DataType.PERCENTAGE_FLOAT,
                    'another percentage': DataType.PERCENTAGE_DECIMAL,
                    'a text': DataType.TEXT,
                    'an URL': DataType.OBJECT,
                },
                    reader.get_data_types())
                self.assertEqual(
                    {'a boolean': True,
                     'a currency': 5,
                     'a date': datetime.date(1975, 4, 20),
                     'a datetime': datetime.datetime(1975, 4, 20, 13, 45),
                     'a decimal': Decimal('10.3'),
                     'a float': 1232.0,
                     'a percentage': 0.56,
                     'a text': 'meta csv |',
                     'an URL': ParseResult(scheme='https', netloc='github.com',
                                           path='/jferard', params='', query='',
                                           fragment=''),
                     'an integer': 56,
                     'another currency': Decimal('10.3'),
                     'another percentage': Decimal('0.782')},
                    next(reader))
                self.assertEqual(
                    {'a boolean': None,
                     'a currency': 17,
                     'a date': datetime.date(2017, 11, 21),
                     'a datetime': None,
                     'a decimal': Decimal('1.03'),
                     'a float': -2.5,
                     'a percentage': 0.58,
                     'a text': '"java-mcsv"',
                     'an URL': None,
                     'an integer': 76,
                     'another currency': Decimal('10.8'),
                     'another percentage': Decimal('0.182')},
                    next(reader))
                self.assertEqual(
                    {'a boolean': False,
                     'a currency': ReadError("7",
                                             "currency/post/€/integer"),
                     'a date': datetime.date(2003, 6, 3),
                     'a datetime': None,
                     'a decimal': Decimal('32.5'),
                     'a float': -2456.5,
                     'a percentage': 0.85,
                     'a text': 'py-mcsv',
                     'an URL': None,
                     'an integer': 1786,
                     'another currency': Decimal('17.8'),
                     'another percentage': Decimal('0.128')},
                    next(reader))


if __name__ == "__main__":
    unittest.main()
