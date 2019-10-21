import unittest


class MyTestCase(unittest.TestCase):
    def test_something(self):
        import main
        print('%s' % str(main))


if __name__ == '__main__':
    unittest.main()
