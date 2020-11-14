import csv
import logging
from datetime import datetime
from decimal import Decimal
from locale import getlocale, LC_TIME, setlocale, Error
from numbers import Number
from time import strptime
from typing import (Union, List, Mapping, Callable, Any, Iterator, Optional,
                    TypeVar)
from pathlib import Path
import collections
import re

ULDML_TO_C1989 = {
    r'dd': '%d',
    r'd': '%d',
    r'MM': '%m',
    r'M': '%m',
    r'yyyy': '%Y',
    r'yy': '%Y',
    r'HH': '%H',
    r'mm': '%M',
    r'MMM': '%b',
}

pattern = r'\b(' + '|'.join(re.escape(k) for k in ULDML_TO_C1989) + r')\b'
regex = re.compile(pattern)


def replace(match):
    return ULDML_TO_C1989[match.group()]


def uldml_to_c1989_format(text):
    """
    See https://stackoverflow.com/a/16735620/6914441

    :param text: some unicode LDML format
    :return: some 1989 C format.
    """
    return re.sub(regex, replace, text)


N = TypeVar('N', bound=Number)


class rfc4180_dialect(csv.Dialect):
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\r\n'
    quoting = 0


RFC4180_DIALECT = rfc4180_dialect()
csv.register_dialect("RFC4180_DIALECT", RFC4180_DIALECT)

Converter = collections.namedtuple("Converter", ['datatype', 'func'])


class CSVInterpreter:
    def __init__(self, encoding: str, dialect: csv.Dialect,
                 converter_by_col_index: Mapping[int, Converter]):
        self._encoding = encoding
        self._dialect = dialect
        self._converter_by_col_index = converter_by_col_index

    def reader(self, path: Union[str, Path], skip_types: bool = True
               ) -> Iterator[List[Any]]:
        with open(path, "r", encoding=self._encoding) as source:
            reader = csv.reader(source, self._dialect)
            header = next(reader)
            yield header
            if not skip_types:
                yield [self._converter_by_col_index[
                           i].datatype if i in self._converter_by_col_index else "text"
                       for i in range(len(header))]
            for row in reader:
                yield [self._converter_by_col_index[i].func(
                    v) if i in self._converter_by_col_index else v for i, v in
                       enumerate(row)]

    def dict_reader(self, path: Union[str, Path], skip_types: bool = True
                    ) -> Iterator[Mapping[str, Any]]:
        reader = self.reader(path, skip_types)
        header = next(reader)
        width = len(header)
        for row in reader:
            if len(row) > width:
                d = dict(zip(header, row[:width]))
                d["@other"] = row[width:]
            else:
                d = dict(zip(header, row))
            yield d


CSVInterpreter.DEFAULT = CSVInterpreter("utf-8", RFC4180_DIALECT, {})


class MetaCSVParser:
    def __init__(self, meta_path: Union[str, Path], strict: bool = False):
        self._meta_path = meta_path
        self._strict = strict
        self._logger = logging.getLogger("py-mcsv")
        self._encoding = "UTF-8"
        self._dialect = rfc4180_dialect()
        self._converter_by_col_index = {}

    def parse(self) -> CSVInterpreter:
        with open(self._meta_path, "r", encoding="utf-8") as source:
            reader = csv.reader(source, RFC4180_DIALECT)
            header = next(reader)
            if header != ["domain", "key", "value"]:
                raise ValueError(
                    f"Bad file header, expected: [\"domain\", \"key\", \"value\"], was {header}")

            for row in reader:
                self._parse_row(row)

        return CSVInterpreter(self._encoding, self._dialect,
                              self._converter_by_col_index)

    def _parse_row(self, row: List[str]):
        domain, key, value = row
        if domain == "file":
            self._parse_file_row(key, value)
        elif domain == "csv":
            self._parse_csv_row(key, value)
        elif domain == "data":
            self._parse_data_row(key, value)
        else:
            raise ValueError(f"Unknown domain: {domain}")

    def _parse_file_row(self, key, value):
        if key == "encoding":
            self._encoding = value
        elif key == "line_terminator":
            self._dialect.lineterminator = value
        else:
            raise ValueError(f"Unknown file domain key: {key}")
        pass

    def _parse_csv_row(self, key, value):
        if key == "delimiter":
            self._dialect.delimiter = value
        elif key == "double_quote":
            self._dialect.doublequote = 1 if value.strip() in (
                "true", "1") else 0
        elif key == "escape_char":
            self._dialect.escapechar = value
        elif key == "quote_char":
            self._dialect.quotechar = value
        elif key == "skip_initial_space":
            self._dialect.skipinitialspace = 1 if value.strip() in (
                "true", "1") else 0
        else:
            raise ValueError(f"Unknown csv domain key: {key}")

    def _parse_data_row(self, key, value):
        n = self._get_col_num(key)
        datatype, *parameters = value.split("/")
        func = None
        if datatype == "bool":
            func = self._parse_data_bool_row(parameters)
        elif datatype == "currency":
            func = self._parse_data_currency_row(parameters)
        elif datatype == "date":
            func = self._parse_data_date_row(parameters)
        elif datatype == "datetime":
            func = self._parse_data_date_row(parameters)
        elif datatype == "float":
            func = self._parse_data_float_row(parameters)
        elif datatype == "integer":
            func = self._parse_data_integer_row(parameters)
        elif datatype == "percentage":
            func = self._parse_data_percentage_row(parameters)
        elif datatype == "text":
            pass
        elif datatype == "any":
            pass
        else:
            raise ValueError(f"Unknown data domain value: {value}")

        if func is not None:
            self._converter_by_col_index[n] = Converter(value, func)

    def _get_col_num(self, key):
        subkeys = key.split("/")
        if len(subkeys) != 3:
            raise ValueError(f"Bad data key {key}")

        col_word, col_n, type_word = subkeys
        if col_word != "col" or type_word != "type":
            raise ValueError(f"Unknown data domain key {key}")

        return int(col_n)

    def _parse_data_bool_row(self, parameters
                             ) -> Callable[[str], Optional[bool]]:
        if len(parameters) == 2:
            true_word, false_word = parameters

            def func(w: str) -> Optional[bool]:
                if w.strip().casefold() == true_word:
                    return True
                elif w.strip().casefold() == false_word:
                    return False
                elif w.strip():
                    return self._warn("Wrong boolean: %s", w)
                else:
                    return None

            return func
        else:
            raise ValueError()

    def _warn(self, *args, **kwargs) -> None:
        if self._strict:
            raise ValueError(args[0] % args[1:])
        else:
            self._logger.warning(*args, **kwargs)
            return None

    def _parse_data_currency_row(self, parameters
                                 ) -> Callable[[str], Optional[Decimal]]:
        if len(parameters) < 3:
            raise ValueError()

        pre_post, symbol, number_type, *number_parameters = parameters
        pre = self._is_pre(pre_post)
        if number_type == "integer":
            func0 = self._parse_data_integer_row(number_parameters)
        elif number_type == "float":
            func0 = self._parse_data_float_row(number_parameters, Decimal)
        else:
            raise ValueError()
        if pre:
            def func(w):
                ws = w.strip()
                if ws.startswith(symbol):
                    ws = ws[len(symbol):].lstrip()
                    return func0(ws)
                else:
                    self._warn("Missing %s currency symbol: %s", symbol, w)
                    return w
        else:
            def func(w):
                ws = w.strip()
                if ws.endswith(symbol):
                    ws = ws[:-len(symbol)].rstrip()
                    return func0(ws)
                else:
                    self._warn("Missing %s currency symbol: %s", symbol, w)
                    return w
        return func

    def _is_pre(self, pre_post: str) -> bool:
        if pre_post == "pre":
            return True
        elif pre_post == "post":
            return False
        else:
            raise ValueError()

    def _parse_data_date_row(self, parameters
                             ) -> Callable[[str], Optional[datetime]]:
        if len(parameters) == 1:
            uldml_date_format, = parameters
            c1989_date_format = uldml_to_c1989_format(uldml_date_format)
            def func(w: str) -> Optional[datetime]:
                try:
                    return strptime(w, c1989_date_format)
                except ValueError as e:
                    return self._warn(str(e))
        elif len(parameters) == 2:
            uldml_date_format, locale_name = parameters
            if "." not in locale_name:
                locale_name += "UTF-8"
            c1989_date_format = uldml_to_c1989_format(uldml_date_format)
            def func(w: str) -> Optional[datetime]:
                try:
                    oldlocale = getlocale(LC_TIME)
                    setlocale(LC_TIME, locale_name)
                except Error:
                    oldlocale = None

                try:
                    return strptime(w, c1989_date_format)
                except ValueError as e:
                    return self._warn(str(e))
                finally:
                    if oldlocale is not None:
                        setlocale(LC_TIME, oldlocale)
        return func

    def _parse_data_datetime_row(self, parameters
                                 ) -> Callable[[str], Optional[datetime]]:
        return self._parse_data_date_row(self, parameters)

    def _parse_data_float_row(self, parameters, f: Callable[[str], N] = float
                              ) -> Callable[[str], N]:
        if len(parameters) == 2:
            thousands_separator, dec_separator = parameters
            if dec_separator != " ":
                dec_separator = dec_separator.strip()

            if thousands_separator == dec_separator:
                raise ValueError()

            if thousands_separator:
                if dec_separator == ".":
                    return lambda w: float(w.replace(thousands_separator, ""))
                else:
                    return lambda w: float(
                        w.replace(thousands_separator, "").replace(
                            dec_separator, "."))
            else:
                if dec_separator == ".":
                    return f
                else:
                    return lambda w: f(w.replace(dec_separator, "."))
        else:
            raise ValueError()

    def _parse_data_integer_row(self, parameters) -> Callable[[str], int]:
        if len(parameters) == 0:
            return int
        elif len(parameters) == 1:
            thousands_separator, = parameters
            return lambda x: int(x.replace(thousands_separator, ""))
        else:
            raise ValueError()

    def parse_data_percentage_row(self, parameters) -> Callable[[str], Decimal]:
        func = self._parse_data_currency_row(parameters)
        return lambda w: func(w)/100


def get_interpreter(meta_path: Union[str, Path] = None, strict: bool = False,
                    skip_types: bool = True) -> CSVInterpreter:
    try:
        interpreter = MetaCSVParser(meta_path, strict).parse()
    except FileNotFoundError:
        interpreter = CSVInterpreter.DEFAULT
    return interpreter


def open_csv(path: Union[str, Path], meta_path: Union[str, Path] = None,
             strict: bool = False, skip_types=True) -> Iterator[List[Any]]:
    if meta_path is None:
        meta_path = path.with_suffix(".mcsv")
    interpreter = get_interpreter(meta_path, strict)
    return interpreter.reader(path, skip_types)


def open_dict_csv(path: Union[str, Path], meta_path: Union[str, Path] = None,
                  strict: bool = False, skip_types=True
                  ) -> Iterator[Mapping[str, Any]]:
    if meta_path is None:
        meta_path = path.with_suffix(".mcsv")
    interpreter = get_interpreter(meta_path, strict)
    return interpreter.dict_reader(path, skip_types)
