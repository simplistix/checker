# Copyright (c) 2009 Simplistix Ltd
#
# See license.txt for more details.
from __future__ import with_statement

import os,sys

from base import OpenRaisesContext,ConfigContext, OutputtingContext
from checker import main, check
from mock import Mock
from testfixtures import Replacer,should_raise,compare,LogCapture
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

    def setUp(self):
        self.r = Replacer()
        self.l = LogCapture()

    def tearDown(self):
        self.l.uninstall()
        self.r.restore()

    def checker_returns(self,output):
        resolve = Mock()
        self.r.replace('checker.resolve',resolve)
        def the_checker(param):
            return output
        resolve.return_value = the_checker
        return resolve
        
    def test_bad_checker(self):
        from checker import check
        check = should_raise(check,ImportError('No module named unknown'))
        check('unknown',None)

    def test_normal(self):
        m = self.checker_returns('some output')
        check('achecker',None)
        compare(m.call_args_list,[
                (('checker.checkers.achecker.check',), {})
                ])

    def test_log_newline(self):
        self.checker_returns('some output\n')
        check('achecker','aparam')
        self.l.check(
            ('root', 'INFO', 'some output'),
            )

    def test_log_no_newline(self):
        self.checker_returns('some output')
        check('achecker','aparam')
        self.l.check(
            ('root', 'INFO', 'some output'),
            )
        
    def test_no_log_empty(self):
        self.checker_returns('')
        check('achecker','aparam')
        self.l.check()

class TestEmail(TestCase):

    def setUp(self):
        self.c = OutputtingContext()

    def tearDown(self):
        self.c.__exit__()

    def test_defaults(self):
        self.c.run_with_config('email_to:recipient@example.com')
        self.c.check_email_config(
            'recipient@example.com',
            ['recipient@example.com'],
            'Checker output from %(hostname)s',
            'localhost',
            )
    
    def test_default_from_multiple_to(self):
        self.c.run_with_config(
            'email_to:r1@example.com, r2@example.com'
            )
        self.c.check_email_config(
            'r1@example.com',
            ['r1@example.com','r2@example.com'],
            'Checker output from %(hostname)s',
            'localhost',
            )
    
def test_suite():
    return TestSuite((
        makeSuite(TestMain),
        makeSuite(TestMain2),
        makeSuite(TestCheck),
        makeSuite(TestEmail),
        ))
