import unittest

class Test(unittest.TestCase):
    
    def test_motsu(self):
        from lib.motsu import test
        test()

    def test_objmap(self):
        from objmap import test
        test()
    

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
