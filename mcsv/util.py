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

def split_parameters(parameters):
    # Avoid split("/") because of escaped slashes
    new_parameters = []
    start = 0
    backslash = False
    cur = ""
    for j, c in enumerate(parameters):
        if j < start:
            pass
        elif c == "\\":
            backslash = True
        elif c == "/":
            if backslash:
                cur += c
                backslash = False
            else:
                new_parameters.append(cur)
                cur = ""
                start = j + 1
        else:
            if backslash:             # let's not forget the \
                cur += "\\"
            cur += c
            backslash = False

    new_parameters.append(parameters[start:])
    return new_parameters