# Copyright (c) 2012 Simplistix Ltd
#
# See license.txt for more details.

import os

from base import ContextTest, OutputtingContext
from checker.checkers.jenkins import check
from testfixtures import TempDirectory, compare

class Tests(ContextTest):

    context = OutputtingContext

    def setUp(self):
        ContextTest.setUp(self)
        self.jenkins = TempDirectory()
        
    def tearDown(self):
        self.jenkins.cleanup()
        ContextTest.tearDown(self)
        
    def test_simple(self):
        self.jenkins.write('nodeMonitors.xml', 'nodeMonitors')
        self.jenkins.write('another.xml', 'another')
        self.jenkins.write('jobs/test-multi/config.xml', 'multi-config')
        self.jenkins.write('jobs/test-another/config.xml', 'single-config')
        self.jenkins.write('jobs/test-another/workspace/junk.xml', 'junk')

        compare(check(self.c.dir.path, self.jenkins.path),'')

        self.c.dir.check_all(
            self.jenkins.path.split(os.sep)[1:],
            'another.xml',
            'jobs/',
            'jobs/test-another/',
            'jobs/test-another/config.xml',
            'jobs/test-multi/',
            'jobs/test-multi/config.xml',
            'nodeMonitors.xml'
            )

    def test_overwrite(self):
        path = self.jenkins.write('config.xml', 'new')
        path = path.split(os.sep)[1:]
        self.c.dir.write(path, 'old')
        compare(check(self.c.dir.path, self.jenkins.path),'')
        compare(self.c.dir.read(path), 'new')
