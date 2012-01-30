# Copyright (c) 2009-2012 Simplistix Ltd
#
# See license.txt for more details.

import os

from base import ContextTest,CommandContext
from checker.checkers.crontab import check
from testfixtures import compare

class TestCrontab(ContextTest):

    context = CommandContext

    def test_crontabs_folder_exists(self):
        self.c.dir.makedir('crontabs')
        self.c.add('crontab -l -u root','crontab output')
        compare(check(self.c.config_folder,'root'),'')
        self.c.dir.check_dir('crontabs','root')
        compare(self.c.dir.read(('crontabs','root')),
                'crontab output')
