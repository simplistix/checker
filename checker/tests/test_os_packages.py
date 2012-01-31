# Copyright (c) 2012 Simplistix Ltd
#
# See license.txt for more details.

import os

from base import ContextTest, CommandContext, listall, cleanup
from checker.checkers.os_packages import check
from testfixtures import compare

class TestPath(ContextTest):

    context = CommandContext

    def test_no_package_manager(self):
        self.c.add('which dpkg', returncode=1)
        self.c.add('which yum', returncode=1)
        self.c.add('which up2date', returncode=1)
        
        compare(check(self.c.config_folder, 'os_packages'),
                'Could not find package manager!')
        compare(listall(self.c.dir), ['os_packages'])
        compare(self.c.dir.read('os_packages'), '')
        compare(self.c.called, [
            'which dpkg', 'which yum', 'which up2date'
            ])
