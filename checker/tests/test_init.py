# Copyright (c) 2012 Simplistix Ltd
#
# See license.txt for more details.

import os

from base import ContextTest, CommandContext, listall, cleanup
from checker.checkers.init import check
from testfixtures import compare

class TestPath(ContextTest):

    context = CommandContext

    def test_storage_path_already_exists(self):
        # This is the key element of this test:
        self.c.dir.makedir('init')

        # These rest is just to make sure nothing blows up:
        compare(check(self.c.config_folder, 'mysql'), '')
        compare(listall(self.c.dir), [
                'init',
                'init/mysql',
                ])
        compare(self.c.called, [
                "/usr/sbin/update-rc.d -n -f mysql remove",
                ])
