# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.
import sys

from checker.command import execute
from testfixtures import tempdir,compare
from unittest import TestSuite,TestCase,makeSuite

class TestExecute(TestCase):

    @tempdir()
    def test_out_and_err(self,d):
        # without the flushes, the order comes out wrong
        path = d.write('test.py','\n'.join((
                "import sys",
                "sys.stdout.write('stdout\\n')",
                "sys.stdout.flush()",
                "sys.stderr.write('stderr\\n')",
                "sys.stderr.flush()",
                "sys.stdout.write('stdout2\\n')",
                "sys.stdout.flush()",
                )),path=True)
        compare('stdout\nstderr\nstdout2\n',
                execute(sys.executable+' '+path))
    
    @tempdir()
    def test_args(self,d):
        path = d.write('test.py','\n'.join((
                "import sys",
                "print sys.argv",
                )),path=True)
        compare("[%r, 'x=1', '--y=2', 'a', 'b']\n" % path,
                execute(sys.executable+' '+path+' x=1 --y=2 a b'))
    
def test_suite():
    return TestSuite((
        makeSuite(TestExecute),
        ))
