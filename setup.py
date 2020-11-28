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
#
from setuptools import setup


def get_long_description():
    readme = open('README.md').read()
    return readme


setup(
    name='py-mcsv',
    version='0.1',
    description='A MetaCSV library for Python',
    long_description=get_long_description(),
    long_description_content_type='text/markdown; charset=UTF-8',
    author='Julien Férard',
    license='GPLv3',
    packages=['mcsv'],
    python_requires='>=3.6',
    url='https://github.com/jferard/py-mcsv',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
    ],
    keywords=[
        'csv',
        'type',
        'datatype',
    ],
)
