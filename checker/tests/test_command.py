# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.
from __future__ import with_statement

import sys

from checker.command import execute
from mock import Mock
from subprocess import PIPE,STDOUT
from testfixtures import tempdir,compare,Replacer
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
    
    @tempdir()
    def test_working_directory(self,d):
        dir = d.makedir('a_dir',path=True)
        path = d.write('test.py','\n'.join((
                "import os",
                "print os.getcwd()",
                )),path=True)
        compare(dir+'\n',
                execute(sys.executable+' '+path,cwd=dir))

    def test_popen_params(self):
        m = Mock()
        m.Popen.return_value = m.Popeni
        m.Popeni.communicate.return_value=('','')
        with Replacer() as r:
            r.replace('checker.command.Popen',m.Popen)
            execute('something')
        compare(m.method_calls,[
                ('Popen',
                 ('something',),
                 {'cwd': None,
                  'shell': True,
                  'stderr': STDOUT,
                  'stdout': PIPE,
                  'universal_newlines': True}),
                ('Popeni.communicate', (), {})
                ])
    
def test_suite():
    return TestSuite((
        makeSuite(TestExecute),
        ))
