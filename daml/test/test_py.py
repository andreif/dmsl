# -*- coding: utf-8 -*-
import os.path
import unittest
import daml

class TestPy(unittest.TestCase):
    def setUp(self):
        self.t = {
            'py_include': None,
            'py_looping': None,
            'py_block_default': None,
            'py_extends': None,}

        for k, v in self.t.items():
            # template file
            a = open(os.path.join('test/templates', k+'.daml')).readlines()
            # expected output
            b = open(os.path.join('test/templates', k+'.html')).read()
            self.t[k] = (a, b)

    def test_py_include(self):
        parsed, expected = self.t['py_include']
        parsed = daml.parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_looping(self):
        parsed, expected = self.t['py_looping']
        parsed = daml.parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_block_default(self):
        parsed, expected = self.t['py_block_default']
        parsed = daml.parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

    def test_py_extends(self):
        parsed, expected = self.t['py_extends']
        parsed = daml.parse(parsed)
        self.assertEqual(parsed.strip(), expected.strip())

