import unittest
import random
import os
from reader import ADSClassicInputStream

class TestFileObj(unittest.TestCase):
    
    def setUp(self):
        self.proj_home = os.path.abspath(os.path.abspath('.') + '/..')
        self.huge_file = self.proj_home + '/tests/data/generate_bigfile.tab'
        if not os.path.exists(self.huge_file):
            self._create_huge_file(self.huge_file)
    
    def _create_huge_file(self, file):
        with open(file, 'w') as fo:
            print 'Generating huge file: %s' % file
            for i in xrange(12000000):
                # example output: 1950RPPh...13...24G    0.22    6    3    4225
                fo.write('{:019}\t{}\t{}\t{}\t{}\n'
                         .format(i, random.randint(0, 100)/100.0, random.randint(0, 3000),
                                 random.randint(0, 10000), random.randint(0, 10000)))
            
    def test_fileobj(self):
            
        with ADSClassicInputStream(self.huge_file) as f:
            line = f.read()
            self.assertTrue(len(line.split('\n')), 12000001)

            
        with ADSClassicInputStream(self.huge_file) as f:
            i = 1
            for x in f:
                i += 1
            self.assertTrue(i, 12000001)
            
            
if __name__ == '__main__':
    unittest.main()            