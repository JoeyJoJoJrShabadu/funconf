from __future__ import absolute_import
try:
    import unittest2 as unittest
except ImportError:
    import unittest
try:
    from inspect import signature
except ImportError:
    from funcsigs import signature
import sys
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x
from io import StringIO
from mock import patch
import yaml

import funconf


TEST_CONFIG = u("""
#
# Aaa
#
aaa:
  float: 4.4
  int: 4
  list_int:
  - 1
  - 2
  list_str:
  - aaa
  - bbb


#
# Bbb
#
bbb:
  float: 8.4
  int: 7
  list_int:
  - 3
  - 4
  list_str:
  - bbb
  - ccc

""".strip())


class TestConfig(unittest.TestCase):

    @patch('__builtin__.open') 
    def test_print_config(self, mock_open):
        mock_open.return_value = StringIO(TEST_CONFIG)
        config = funconf.Config('mocked.conf')
        self.assertEqual(str(config).strip(), TEST_CONFIG)
        self.assertEqual(len(config), 8)

    @patch('__builtin__.open') 
    def test_accessing_attributes(self, mock_open):
        mock_open.return_value = StringIO(TEST_CONFIG)
        config = funconf.Config('mocked.conf')
        self.assertEqual(config.aaa.int, 4)
        config.aaa.int = 5
        self.assertEqual(config.aaa.int, 5)
        self.assertRaises(funconf.ConfigAttributeError, getattr, config, 'nope')
        self.assertRaises(funconf.ConfigAttributeError, getattr, config.aaa,
                'nope')
        
    @patch('__builtin__.open') 
    def test_empty_config(self, mock_open):
        mock_open.return_value = StringIO(u(""))
        config = funconf.Config('mocked.conf')

    @patch('__builtin__.open')
    def test_empty_section(self, mock_open):
        mock_open.return_value = StringIO(u("empty: 1"))
        config = funconf.Config('mocked.conf')

    @patch('__builtin__.open')
    def test_broken_yaml(self, mock_open):
        mock_open.return_value = StringIO(u("`empty:a df asd Z X324!~ 1"))
        self.assertRaises(yaml.scanner.ScannerError, 
                funconf.Config, 'mocked.conf')

    def test_file_doesnt_exist(self):
        funconf.Config(['blaoo.con'])

    def test_setting(self):
        config = funconf.Config()
        config.set('foo', 'bar', [34, 2, 5])
        config.set('foo', 'moo', "shoe")
        config.set('foo', 'bar', 24.22323)
        config.set('bread', 'milk', True)
        config.set('bread', 'butter', False)
        self.assertTrue(config.bread.milk)

    def test_setting_attributes(self):
        config = funconf.Config()
        self.assertRaises(Exception, setattr, config, 'blah', 4)
        config.set('foo', 'bar', False)
        self.assertRaises(Exception, setattr, config.foo, 'blah', 4)
        config.foo.bar = True
        self.assertTrue(config.foo.bar)

    def test_delattr(self):
        config = funconf.Config()
        config.set('foo', 'bar', False)
        self.assertRaises(NotImplementedError, config.__delitem__, 'foo')
        self.assertRaises(NotImplementedError, config.foo.__delitem__, 'bar')

    def test_dirty(self):
        config = funconf.Config()
        config.set('foo', 'bar', False)
        self.assertTrue(config.foo.dirty)
        self.assertFalse(config.foo.dirty)
