# coding: utf-8
import unittest

from mcsv.parser import get_interpreter


class ParserTest(unittest.TestCase):
    def test(self):
        print(list(get_interpreter("fixtures/meta_csv.mcsv").dict_reader("fixtures/meta_csv.mcsv")))

    def test2(self):
        print(list(get_interpreter("fixtures/20201001-bal-216402149.mcsv").dict_reader("fixtures/20201001-bal-216402149.csv")))


if __name__ == "__main__":
    unittest.main()
