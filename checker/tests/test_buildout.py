# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.

from checker.checkers.buildout import check
from mock import Mock
from testfixtures import replace,compare
from unittest import TestCase,TestSuite,makeSuite

class TestBuildout(TestCase):

    @replace('os.sep','|')
    @replace('checker.command.execute',Mock())
    def test_right_bin_buildout_path_seperator(self,m):
        m.return_value=''
        check('x','y')
        compare(m.call_args_list,[
                (('bin|buildout -o -q',), {'cwd': 'y'}),
                ])

def test_suite():
    return TestSuite((
        makeSuite(TestBuildout),
        ))
