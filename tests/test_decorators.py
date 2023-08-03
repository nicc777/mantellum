"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
import json
import time

relative_path_of_this_test = os.path.realpath(__file__)
src_path = '{}{}src'.format(
    '/'.join(relative_path_of_this_test.split(os.sep)[0:-1]),
    os.sep
)

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
sys.path.append(src_path)
print('sys.path={}'.format(sys.path))

import unittest


from mantellum.decorators import *

running_path = os.getcwd()
print('Current Working Path: {}'.format(running_path))


class TestLogger:

    def __init__(self):
        self.messages = list()

    def add_log_event(self, message: str, level: str='info'):
        self.messages.append(
            {
                'Level': level,
                'Message': message
            }
        )

    def info(self, message: str):
        self.add_log_event(message=message, level='INFO')

    def warn(self, message: str):
        self.add_log_event(message=message, level='WARNING')

    def warning(self, message: str):
        self.add_log_event(message=message, level='WARNING')

    def error(self, message: str):
        self.add_log_event(message=message, level='ERROR')

    def debug(self, message: str):
        self.add_log_event(message=message, level='DEBUG')


class TestDecoratorTimer(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        print('-'*80)

    def test_function_taking_1_second(self):

        @timer(l=TestLogger())
        def test_function()->int:
            time.sleep(1)
            return 1

        result = test_function()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)




if __name__ == '__main__':
    unittest.main()

