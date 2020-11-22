# coding: utf-8
import unittest

from mcsv.util import split_parameters


class UtilTest(unittest.TestCase):
    def test(self):
        self.assertEqual(['DD/mm/yyyy', 'locale'], split_parameters("DD\/mm\/yyyy/locale"))

    def test_bs(self):
        self.assertEqual(['DD\\mm\\yyyy', 'locale'], split_parameters("DD\\mm\\yyyy/locale"))


if __name__ == "__main__":
    unittest.main()