# Copyright (c) 2009-2012 Simplistix Ltd
#
# See license.txt for more details.

from checker.checkers.buildout import check
from mock import Mock
from testfixtures import replace,compare
from unittest import TestCase

class TestBuildout(TestCase):

    @replace('os.sep','|')
    @replace('execute.simple',Mock())
    def test_right_bin_buildout_path_seperator(self,m):
        m.return_value=''
        check('x','y')
        compare(m.call_args_list,[
                (('bin|buildout -o -q',), {'cwd': 'y'}),
                ])
