from __future__ import with_statement
# Copyright (c) 2012-2013 Simplistix Ltd
#
# See license.txt for more details.

import os

from base import ContextTest, OutputtingContext
from checker.checkers.jenkins import check
from testfixtures import ShouldRaise, TempDirectory, compare

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
            'nodeMonitors.xml',
            'plugin-versions.txt'
            )

    def test_overwrite(self):
        path = self.jenkins.write('config.xml', 'new')
        path = path.split(os.sep)[1:]
        self.c.dir.write(path, 'old')
        compare(check(self.c.dir.path, self.jenkins.path),'')
        compare(self.c.dir.read(path), 'new')

    def _write_jpi(self, name, manifest):
        self.jenkins.write('plugins/'+name+'/META-INF/MANIFEST.MF', manifest)

    def test_plugin_versions(self):
        self._write_jpi('test1', """
Url: http://wiki.jenkins-ci.org/display/JENKINS/Ant+Plugin
Junk: 1.0
Extension-Name: test1
Implementation-Title: test1
Implementation-Version: 2
Plugin-Version: 2
""")
        self._write_jpi('test2', """
Junk: 1.0
Extension-Name: test2
Implementation-Title: test2
Implementation-Version: 1
Plugin-Version: 1
""")
        compare(check(self.c.dir.path, self.jenkins.path), '')

        compare(os.linesep.join((
            'test1: 2',
            'test2: 1',
            '',
            )),
                self.c.dir.read(
                    self.jenkins.path.split(os.sep)[1:]+['plugin-versions.txt']
                    ))

    def test_extension_name_versus_implementation_title(self):
        self._write_jpi('test1', """
Junk: 1.0
Extension-Name: test1
Implementation-Title: Test1
Implementation-Version: 2
Plugin-Version: 2
""")
        with ShouldRaise(AssertionError(
            "extension-name ('test1') != implementation-title ('Test1')"
            )):
            check(self.c.dir.path, self.jenkins.path)

    def test_plugin_versions_versus_implementation_version(self):
        self._write_jpi('test1', """
Junk: 1.0
Extension-Name: test1
Implementation-Title: test1
Implementation-Version: 1
Plugin-Version: 2
""")
        with ShouldRaise(AssertionError(
            "plugin-version ('2') != implementation-version ('1')"
            )):
            check(self.c.dir.path, self.jenkins.path)

    def test_duplicate_key(self):
        self._write_jpi('test1', """
Extension-Name: test1
Extension-Name: test2
""")
        with ShouldRaise(AssertionError(
            "duplicate keys for 'extension-name' found, "
            "value was 'test1', now 'test2'")):
            check(self.c.dir.path, self.jenkins.path)

    def test_duplicate_name(self):
        self._write_jpi('test1', """
Junk: 1.0
Extension-Name: test1
Implementation-Title: test1
Implementation-Version: 2
Plugin-Version: 2
""")
        self._write_jpi('test2', """
Junk: 1.0
Extension-Name: test1
Implementation-Title: test1
Implementation-Version: 1
Plugin-Version: 1
""")
        with ShouldRaise(AssertionError(
            "'test1' and 'test2' both said they were 'test1'"
            )):
            check(self.c.dir.path, self.jenkins.path)
