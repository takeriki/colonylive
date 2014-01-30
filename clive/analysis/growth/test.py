import unittest

class Test(unittest.TestCase):

    def test_colony2growth(self):
        from colony2growth import test
        test()
    
    def test_normalize(self):
        from normalize import test
        test()
    
    def test_modelfit(self):
        from lib.modelfit import test
        test()

if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
