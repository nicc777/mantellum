"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://github.com/nicc777/mantellum/blob/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
import json
import time
import tempfile

relative_path_of_this_test = os.path.realpath(__file__)
src_path = '{}{}src'.format(
    '/'.join(relative_path_of_this_test.split(os.sep)[0:-1]),
    os.sep
)

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
sys.path.append(src_path)
print('sys.path={}'.format(sys.path))

import unittest


from mantellum.metrics import *

running_path = os.getcwd()
print('Current Working Path: {}'.format(running_path))


class TestClassDimensions(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        print('='*80)

    def tearDown(self):
        print('-'*40)

    def test_dimensions(self):
        d = Dimensions()
        d.add_dimension(dimension=Dimension(name='Application', value='TestApp'))
        d.add_dimension(dimension=Dimension(name='Function', value='TestFunction'))
        dump = d.to_dict()
        self.assertIsNotNone(dump)
        self.assertIsInstance(dump, dict)
        self.assertTrue('Dimensions' in dump)
        self.assertIsNotNone(dump['Dimensions'])
        self.assertIsInstance(dump['Dimensions'], list)
        self.assertEqual(len(dump['Dimensions']), 2)
        for item in dump['Dimensions']:
            self.assertIsNotNone(item)
            self.assertIsInstance(item, dict)
            self.assertTrue('Name' in item)
            self.assertTrue('Value' in item)


class TestMetricRecords(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        print('='*80)
        self.d = Dimensions()
        self.d.add_dimension(dimension=Dimension(name='Application', value='TestApp'))
        self.d.add_dimension(dimension=Dimension(name='Function', value='TestFunction'))

    def tearDown(self):
        print('-'*40)

    def test_metric_records(self):
        record = MetricRecords(name='UnitTest')
        record.record_dimension_value(
            dimensions=self.d, 
            recorded_value=1
        )
        dump = record.to_dict()
        self.assertIsNotNone(dump)
        self.assertIsInstance(dump, dict)
        print('DUMP as JSON: {}'.format(json.dumps(dump, default=str)))



if __name__ == '__main__':
    unittest.main()
