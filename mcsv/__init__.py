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
from contextlib import contextmanager
from typing import Union, Optional

from .field_description import (FieldDescription, python_type_to_data_type,
                                data_type_to_python_type)
from .field_descriptions import data_type_to_field_description
from .reader import (MetaCSVReader, MetaCSVDictReader,
                     open_csv_reader, open_dict_csv_reader)
from .util import to_meta_path, FileLike
from .writer import (MetaCSVWriter, open_csv_writer, open_dict_csv_writer,
                     MetaCSVDictWriter)


@contextmanager
def open_csv(file: FileLike, mode: str = "r",
             meta_file: Optional[FileLike] = None,
             *args, **kwargs) -> Union[MetaCSVReader, MetaCSVWriter]:
    if mode == "r":
        with open_csv_reader(file, meta_file, *args, **kwargs) as reader:
            yield reader
    elif mode == "w":
        with open_csv_writer(file, *args, meta_file=meta_file,
                             **kwargs) as writer:
            yield writer


def open_dict_csv(file: FileLike, mode: str = "r",
                  meta_file: Optional[FileLike] = None,
                  *args, **kwargs) -> Union[
    MetaCSVDictReader, MetaCSVDictWriter]:
    if mode == "r":
        with open_dict_csv_reader(file, meta_file, *args,
                                  **kwargs) as reader:
            yield reader
    elif mode == "w":
        with open_dict_csv_writer(file, *args, meta_file=meta_file,
                                  **kwargs) as writer:
            yield writer
