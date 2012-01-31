# Copyright (c) 2009-2012 Simplistix Ltd
#
# See license.txt for more details.

import os

from base import ContextTest,CommandContext,listall,cleanup
from checker.checkers.path import check
from testfixtures import compare

class TestPath(ContextTest):

    context = CommandContext

    def test_source_doesnt_exist(self):
        bad_path = os.path.join(self.c.config_folder,'bad')
        compare(
            check(self.c.config_folder,bad_path),
            "Does not exist:%r"%bad_path
            )

    def test_source_is_made_absolute_at_start(self):
        # CommandContext pretends nothing exists
        compare(
            check(self.c.config_folder,'foo'),
            "Does not exist:%r"%os.path.abspath('foo')
            )

    def test_make_target_dir(self):
        # make us not-windows
        self.c.r.replace('subprocess.mswindows',False)
        # pretend only our path exists
        path = '/some/deep/path'
        self.c.existing_paths.add(path)
        compare(check(self.c.config_folder,path),'')
        compare(listall(self.c.dir),[
                'some',
                'some/deep',
                'some/deep/path.listing',
                ])
        compare(self.c.called,[
                "cp -R '/some/deep/path' '<config>/some/deep'",
                "LC_COLLATE=\"C\" ls -laR --time-style=+ '/some/deep/path'",
                ])

    def test_storage_path_already_exists(self):
        # This is the key element of this test:
        self.c.dir.makedir('something')
        
        self.c.r.replace('subprocess.mswindows',False)
        # pretend only our path exists
        path = '/something'
        self.c.existing_paths.add(path)

        compare(check(self.c.config_folder, path), '')
        compare(listall(self.c.dir),[
                'something.listing',
                'something',
                ])
        compare(self.c.called,[
                "cp -R '/something' '<config>'",
                "LC_COLLATE=\"C\" ls -laR --time-style=+ '/something'",
                ])
