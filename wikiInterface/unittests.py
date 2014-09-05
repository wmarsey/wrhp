import unittest as ut
import itertools as it
from argParser import ArgParser

SHOW_ERROR_MESSAGES = True

class CommandLineDBTest(ut.TestCase):
    argparse = None
    def setUp(self):
        args = ["--domain", "en", "--title", "engly", "-r"]
        self.argparse = ArgParser(args)
        
    def testValueRaise(self):
        self.assertRaises(ValueError, self.argparse.run)

class CommandLineMispell(ut.TestCase):
    argparse = None
    def setUp(self):
        args = ["--domain", "en", "--tile", "English"]
        self.argparse = ArgParser(args)
        
    def testValueRaise(self):
        self.assertRaises(ValueError, self.argparse.run)

class CommandLineNoDomain(ut.TestCase):
    argparse = None
    def setUp(self):
        args = ["--title", "Rupert Sheldrake"]
        self.argparse = ArgParser(args)
        
    def testValueRaise(self):
        self.assertRaises(ValueError, self.argparse.run)

class CommandLinePageIDNotNumber(ut.TestCase):
    argparse = None
    def setUp(self):
        args = ["--pageid", "en", "--domain", "en"]
        self.argparse = ArgParser(args)
        
    def testValueRaise(self):
        self.assertRaises(ValueError, self.argparse.run)

class CommandLineRevIDNotNumber(ut.TestCase):
    argparse = None
    def setUp(self):
        args = ["--revid", "en", "--domain", "en", "-v"]
        self.argparse = ArgParser(args)
        
    def testValueRaise(self):
        self.assertRaises(ValueError, self.argparse.run)

class CommandLineMissingArgument(ut.TestCase):
    argparse = None
    def setUp(self):
        args = ["--revid", "--domain", "en", "-v"]
        self.argparse = ArgParser(args)
        
    def testValueRaise(self):
        self.assertRaises(ValueError, self.argparse.run)

class CommandLineFlagGivenArg(ut.TestCase):
    argparse = None
    def setUp(self):
        args = ["-v", "000"]
        self.argparse = ArgParser(args)
        
    def testValueRaise(self):
        self.assertRaises(ValueError, self.argparse.run)

def run():
    ut.main()

if __name__ == '__main__':
    ut.main()
