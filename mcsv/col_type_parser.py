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

from typing import Callable, Optional, Union, Tuple

from mcsv.date_format_converter import _DateFormatParser
from mcsv.field_description import FieldDescription
from mcsv.field_descriptions import (
    DecimalFieldDescription, DateFieldDescription, DatetimeFieldDescription,
    TextFieldDescription, IntegerFieldDescription,
    PercentageDecimalFieldDescription, PercentageFloatFieldDescription,
    BooleanFieldDescription, CurrencyIntegerFieldDescription,
    CurrencyDecimalFieldDescription, FloatFieldDescription)
from mcsv.util import split_parameters


class ColTypeParser:
    def __init__(self, create_object_description: Optional[Callable[
        [Tuple[str]], FieldDescription]] = None):
        if create_object_description is None:
            def create_object_description(parameters):
                return TextFieldDescription.INSTANCE
        self._create_object_description = create_object_description

    def parse_col_type(self, value):
        datatype, *parameters = split_parameters(value)
        if datatype == "bool":
            description = self.parse_data_bool_row(parameters)
        elif datatype == "sign":
            description = self.parse_data_currency_row(parameters)
        elif datatype == "date":
            description = self.parse_data_date_row(parameters)
        elif datatype == "datetime":
            description = self.parse_data_datetime_row(parameters)
        elif datatype == "decimal":
            description = self.parse_data_decimal_row(parameters)
        elif datatype == "float":
            description = self.parse_data_float_row(parameters)
        elif datatype == "integer":
            description = self.parse_data_integer_row(parameters)
        elif datatype == "percentage":
            description = self.parse_data_percentage_row(parameters)
        elif datatype == "text":
            description = TextFieldDescription.INSTANCE
        elif datatype == "object":
            description = self.parse_data_object_row(parameters)
        else:
            raise ValueError(f"Unknown data domain delimiter: {value}")
        return description

    def parse_data_bool_row(self, parameters) -> BooleanFieldDescription:
        if len(parameters) == 1:
            true_word = parameters[0]
            false_word = ""
        elif len(parameters) == 2:
            true_word, false_word = parameters
        else:
            raise ValueError(f"Bad number of boolean parameters: {parameters}")
        return BooleanFieldDescription(true_word, false_word)

    def parse_data_currency_row(self, parameters
                                ) -> Union[CurrencyIntegerFieldDescription,
                                           CurrencyDecimalFieldDescription]:
        if len(parameters) < 3:
            raise ValueError()

        pre_post, symbol, number_type, *number_parameters = parameters
        pre = self._is_pre(pre_post)
        if number_type == "integer":
            number_description = self.parse_data_integer_row(number_parameters)
            return CurrencyIntegerFieldDescription(pre, symbol,
                                                   number_description)
        elif number_type == "decimal":
            number_description = self.parse_data_decimal_row(number_parameters)
            return CurrencyDecimalFieldDescription(pre, symbol,
                                                   number_description)
        else:
            raise ValueError()

    def _is_pre(self, pre_post: str) -> bool:
        if pre_post == "pre":
            return True
        elif pre_post == "post":
            return False
        else:
            raise ValueError()

    def parse_data_date_row(self, parameters
                            ) -> DateFieldDescription:
        c1989_date_format, locale_name = self._parse_data_date_or_datetime_parameters(
            parameters)
        return DateFieldDescription(c1989_date_format, locale_name)

    def parse_data_datetime_row(self, parameters
                                ) -> DatetimeFieldDescription:
        c1989_date_format, locale_name = self._parse_data_date_or_datetime_parameters(
            parameters)
        return DatetimeFieldDescription(c1989_date_format, locale_name)

    def _parse_data_date_or_datetime_parameters(self, parameters: Tuple[str, ...]
                                                ) -> Tuple[str, Optional[str]]:
        if len(parameters) == 1:
            uldml_date_format = parameters[0]
            locale_name = None
        elif len(parameters) == 2:
            uldml_date_format, locale_name = parameters
            if "." not in locale_name:
                locale_name += "UTF8"
        else:
            raise ValueError()
        c1989_date_format = date_parser.parse(uldml_date_format)
        return c1989_date_format, locale_name

    def parse_data_float_row(self, parameters) -> FloatFieldDescription:
        if len(parameters) == 2:
            thousands_separator, dec_separator = parameters
            if dec_separator != " ":
                dec_separator = dec_separator.strip()

            if thousands_separator == dec_separator:
                raise ValueError()
            return FloatFieldDescription(thousands_separator, dec_separator)
        else:
            raise ValueError

    def parse_data_decimal_row(self, parameters) -> DecimalFieldDescription:
        if len(parameters) == 2:
            thousands_separator, dec_separator = parameters
            if dec_separator != " ":
                dec_separator = dec_separator.strip()

            if thousands_separator == dec_separator:
                raise ValueError()
            return DecimalFieldDescription(thousands_separator, dec_separator)
        else:
            raise ValueError

    def parse_data_integer_row(self, parameters) -> IntegerFieldDescription:
        if len(parameters) == 0:
            thousands_separator = None
        elif len(parameters) == 1:
            thousands_separator = parameters[0]
        else:
            raise ValueError()

        return IntegerFieldDescription(thousands_separator)

    def parse_data_percentage_row(self, parameters
                                  ) -> Union[PercentageDecimalFieldDescription,
                                             PercentageFloatFieldDescription]:
        if len(parameters) < 3:
            raise ValueError()

        pre_post, symbol, number_type, *number_parameters = parameters
        pre = self._is_pre(pre_post)
        if number_type == "decimal":
            number_description = self.parse_data_decimal_row(number_parameters)
            return PercentageDecimalFieldDescription(pre, symbol,
                                                     number_description)
        elif number_type == "float":
            number_description = self.parse_data_float_row(number_parameters)
            return PercentageFloatFieldDescription(pre, symbol,
                                                   number_description)
        else:
            raise ValueError()

    def parse_data_object_row(self, parameters) -> FieldDescription:
        return self._create_object_description(parameters)


date_parser = _DateFormatParser.create()