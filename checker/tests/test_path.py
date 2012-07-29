# Copyright (c) 2009-2012 Simplistix Ltd
#
# See license.txt for more details.
from __future__ import with_statement

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

    def test_selinux_entries(self):
        # selinux in the 2.6 kernel introduces a new column
        # in the permissions block, which we ignore for now
        checker_txt = "path:/some/folder\n"
        
        with CommandContext() as c:
            # pretend we're not on windows
            c.r.replace('subprocess.mswindows',False)
            # pretend the paths exist
            c.existing_paths.add('/some/folder')
            # stub out the cp and ls calls
            c.add("cp -R '/some/folder' '<config>/some'",files=(
                ('some/folder/afile.cfg','content'),
                ('some/folder/bfile.cfg','content'),
                ('some/folder/cfile.cfg','content'),
                ))
            c.add("LC_COLLATE=\"C\" ls -laR --time-style=+ '/some/folder'",
                  output="""/some/folder:
total 36
drwxr-xr-x.  2 root root 4096  .
drwxr-xr-x+ 46 root root 4096  ..
-rw-r--r--.  1 root root 2425  afile.cfg
-rw-r--r--+  1 root root 1421  bfile.cfg
-rw-r--r--   1 root root 1421  cfile.cfg
""")
            # now run the config
            c.run_with_config(checker_txt)
            # check the calls
            compare(c.called,[
                "cp -R '/some/folder' '<config>/some'",
                "LC_COLLATE=\"C\" ls -laR --time-style=+ '/some/folder'",
                'svn up -q <config>',
                'svn status <config>'
                ])
            # check the files are as expected
            compare([
                'checker.txt',
                'some/folder.listing',
                'some/folder/afile.cfg',
                'some/folder/bfile.cfg',
                'some/folder/cfile.cfg',
                ], listall(c.dir,dir=False))
            compare("""/some/folder:
drwxr-xr-x root root .
-rw-r--r-- root root afile.cfg
-rw-r--r-- root root bfile.cfg
-rw-r--r-- root root cfile.cfg
""", c.dir.read(('some', 'folder.listing')))
