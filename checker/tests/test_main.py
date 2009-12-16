# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.
from __future__ import with_statement

import os

from base import OpenRaisesContext,ConfigContext
from checker import main
from mock import Mock
from testfixtures import replace,should_raise,compare
from unittest import TestSuite,TestCase,makeSuite

class TestMain(TestCase):

    def test_no_args(self):
        with OpenRaisesContext(['ascript']):
            # make sure we look for the config in /config by default
            should_raise(main,IOError("'/config/checker.txt' 'rU'"))()

class TestMain2(TestCase):

    def setUp(self):
        self.c = ConfigContext()

    def tearDown(self):
        self.c.__exit__()

    def test_ignore_whitespace_lines(self):
        self.c.run_with_config(" \t\nt1:arg\n")
        self.c.check_checkers_called(
                ('t1',('arg',),{}),
                ('svn',(self.c.dir.path,),{}),
                )

    def test_uniform_line_endings(self):
        self.c.run_with_config(" \t\nt1:arg1\r\nt2:arg2\n")
        self.c.check_checkers_called(
                ('t1',('arg1',),{}),
                ('t2',('arg2',),{}),
                ('svn',(self.c.dir.path,),{}),
                )

    def test_missing_line_ending_okay(self):
        self.c.run_with_config("t2:arg")
        self.c.check_checkers_called(
                ('t2',('arg',),{}),
                ('svn',(self.c.dir.path,),{}),
                )

    def test_colon_in_parameter(self):
        self.c.run_with_config("t2:argpt1:argpt2")
        self.c.check_checkers_called(
                ('t2',('argpt1:argpt2',),{}),
                ('svn',(self.c.dir.path,),{}),
                )

    def test_no_colon_in_line(self):
        should_raise(
            self.c.run_with_config,
            ValueError('No colon found on a line in checker.txt')
            )("foo")

class TestCheck(TestCase):
                           
    def test_bad_checker(self):
        from checker import check
        check = should_raise(check,ImportError('No module named unknown'))
        check('unknown',None)

    @replace('checker.resolve',Mock())
    def test_normal(self,m):
        from checker import check
        check('achecker',None)
        compare(m.call_args_list,[
                (('checker.checkers.achecker.check',), {})
                ])

class TestEmail(TestCase):

    def test_default_from(self):
        pass
    
    def test_default_subject(self):
        pass
    
    def test_default_smtphost(self):
        pass
    
def test_suite():
    return TestSuite((
        makeSuite(TestMain),
        makeSuite(TestMain2),
        makeSuite(TestCheck),
        ))
