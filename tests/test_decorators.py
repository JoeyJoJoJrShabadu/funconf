from __future__ import absolute_import

try:
    import unittest2 as unittest
except ImportError:
    import unittest

try:
    from inspect import signature
except ImportError:
    from funcsigs import signature


import funconf


class TestWrapsKwargs(unittest.TestCase):

    def test_wrapped(self):
        kwargs = dict(a=1)
        @funconf.wraps_kwargs(kwargs)
        def main(**k):
            return k
        self.assertTrue(kwargs == main())
        self.assertTrue(kwargs == main(a=5))
        self.assertTrue(kwargs != main(c=5))
        self.assertEqual({'a':5, 'c':5}, main(c=5))
        self.assertTrue(kwargs is not main())

    def test_wrapped_no_params(self):
        @funconf.wraps_kwargs({})
        def main(**k):
            return k
        self.assertTrue({} == main())

    def test_keyword_with_var(self):
        @funconf.wraps_kwargs({})
        def main(a=3, **k):
            return (a, k)
        a, k = main(a=4)
        self.assertTrue(k == {})
        self.assertTrue(a == 4)
        a, k = main(b=6)
        self.assertTrue(k == {'b':6})
        self.assertTrue(a == 3)
        a, k = main()
        self.assertTrue(k == {})
        self.assertTrue(a == 3)
 
    def test_with_no_var_keywords(self):
        conf = dict(b=4)
        @funconf.wraps_kwargs(conf)
        def main(a=4):
            return a
        self.assertTrue(main(b=5) == 4)
        self.assertTrue(dict(b=5) == conf)

    def test_var_arg(self):
        conf = dict(a=4)
        @funconf.wraps_kwargs(conf)
        def main(a, b):
            self.assertEqual(conf, {'a':a})
        main(4, 5)
        main('afs', 'foo')

    def test_fixed_arg(self):
        pass

    def test_arg_in_kwarg(self):
        kwargs = dict(blob=4)
        @funconf.wraps_kwargs(kwargs)
        def main(blob=3):
            return blob
        self.assertEqual(main(), 4)
        self.assertEqual(main(blob=2), 2)


class TestLazyStringCast(unittest.TestCase):
    
    def test_cast_int(self):
        @funconf.lazy_string_cast(dict(a=1))
        def main(**k):
            return k
        self.assertTrue(dict(a=111) == main(a='111'))
        self.assertRaises(ValueError, main, a='aaa')

    def test_cast_bool(self):
        @funconf.lazy_string_cast(dict(a=True))
        def main(**k):
            return k
        self.assertTrue(dict(a=False) == main(a='False'))
        self.assertTrue(dict(a=False) == main(a='f'))
        self.assertTrue(dict(a=False) == main(a='false'))
        self.assertTrue(dict(a=False) == main(a='n'))
        self.assertTrue(dict(a=False) == main(a='no'))
        self.assertTrue(dict(a=True) == main(a='true'))
        self.assertTrue(dict(a=True) == main(a='t'))
        self.assertTrue(dict(a=True) == main(a='y'))
        self.assertTrue(dict(a=True) == main(a='yes'))
        self.assertRaises(ValueError, main, a='aaa')

    def test_cast_float(self):
        @funconf.lazy_string_cast(dict(a=4.0))
        def main(**k):
            return k
        self.assertTrue(dict(a=1.11) == main(a='1.11'))
        self.assertRaises(ValueError, main, a='aaa')

    def test_cast_other(self):
        @funconf.lazy_string_cast(dict(a=dict(moo='foo')))
        def main(**k):
            return k
        self.assertTrue(main(a='blah')['a'] == 'blah')

    def test_cast_list_int(self):
        @funconf.lazy_string_cast(dict(a=[1]))
        def main(**k):
            return k
        self.assertTrue(main(a='111 222')['a'] == [111, 222])
        self.assertRaises(ValueError, main, a='aaa')

    def test_cast_list_bool(self):
        @funconf.lazy_string_cast(dict(a=[True]))
        def main(**k):
            return k
        self.assertTrue(main(a='False True')['a'] == [False, True])
        self.assertRaises(ValueError, main, a='aaa')

    def test_cast_list_float(self):
        @funconf.lazy_string_cast(dict(a=[4.0]))
        def main(**k):
            return k
        self.assertTrue(main(a='34.23 232.1')['a'] == [34.23, 232.1])
        self.assertRaises(ValueError, main, a='aaa')

    def test_models_as_func_or_method(self):
        @funconf.lazy_string_cast
        def main(debug=True):
            return debug
        self.assertFalse(main(debug='f'))

    def test_positional(self):
        @funconf.lazy_string_cast(dict(debug=True))
        def main(debug):
            return debug
        self.assertEqual(main('f'), False)

    def test_var_pos_and_var_keyword(self):
        @funconf.lazy_string_cast(dict(debug=True, foobar=4, moo=3))
        def main(debug, foobar=6, *a, **k):
            return debug, foobar, k, a
        debug, foobar, k, a = main('f', 34, 65, 'hi', moo='24')
        self.assertEqual(debug, False)
        self.assertEqual(foobar, 34)
        self.assertEqual(a, (65,'hi'))
        self.assertEqual(k, {'moo':24})

    def test_no_model_var_pos_and_var_keyword(self):
        @funconf.lazy_string_cast
        def main(debug, foobar=6, *a, **k):
            return debug, foobar, k, a
        debug, foobar, k, a = main('f', 34, 65, 'hi', moo='24')
        self.assertEqual(debug, 'f')
        self.assertEqual(foobar, 34)
        self.assertEqual(a, (65,'hi'))
        self.assertEqual(k, {'moo':'24'})

