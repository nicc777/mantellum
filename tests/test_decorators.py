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

    def reset(self):
        self.messages = list()


class TestDecoratorTimer(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        print('='*80)
        self.l = TestLogger()
        self.l.reset()
        override_logger(new_logger=self.l)

    def tearDown(self):
        print('Log Message Dump:')
        print('-'*40)
        print('{}'.format(json.dumps(self.l.messages, default=str)))

    def test_function_taking_1_second(self):

        @timer
        def test_function()->int:
            time.sleep(1)
            return 1

        result = test_function()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)

        self.assertIsNotNone(self.l)
        self.assertIsNotNone(self.l.messages)
        self.assertIsInstance(self.l.messages, list)
        self.assertTrue(len(self.l.messages) > 0)


class TestDecoratorRetryOnException(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        print('='*80)
        self.l = TestLogger()
        self.l.reset()
        override_logger(new_logger=self.l)
        self.tmp_file_handler = tempfile.TemporaryFile()

    def tearDown(self):
        self.tmp_file_handler.close()
        print('Log Message Dump:')
        print('-'*40)
        print('{}'.format(json.dumps(self.l.messages, default=str)))

    def test_function_with_1_retry_forced_with_jitter(self):

        @retry_on_exception(number_of_retries=2, enable_jitter=True)
        def test_function(fh)->int:
            retry_count = 0
            fh.seek(0)
            data = fh.read()
            try:
                retry_count = int(data.decode('utf-8'))
            except:
                retry_count = 0
            if retry_count > 0:
                return 1
            fh.seek(0)
            fh.write('1'.encode('utf-8'))
            raise Exception('Oopsie')

        result = test_function(fh=self.tmp_file_handler)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertEqual(result, 1)



if __name__ == '__main__':
    unittest.main()

