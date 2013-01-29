from __future__ import with_statement
# Copyright (c) 2012-2013 Simplistix Ltd
#
# See license.txt for more details.

from glob import glob
from os import sep, makedirs
from os.path import join, dirname, exists, split
from shutil import copyfile
from zipfile import ZipFile

def _paths(jenkins_home, *patterns):
    for pattern in patterns:
        for path in sorted(glob(join(jenkins_home, *pattern))):
            yield path

def make_path(config_folder, src_path):
    target_path = join(config_folder, *src_path.split(sep)[1:])
    target_dir = dirname(target_path)
    if not exists(target_dir):
        makedirs(target_dir)
    return target_path
    
    
def check(config_folder, jenkins_home):
    
    # The .xml files
    for src_path in _paths(jenkins_home,
                           ['*.xml'],
                           ['jobs', '*', 'config.xml']):
        target_path = make_path(config_folder, src_path)
        copyfile(src_path, target_path)
        
    # the plugin versions
    plugins = {}
    for manifest_path in _paths(jenkins_home,
                              ['plugins', '*', 'META-INF', 'MANIFEST.MF']):
        data = {}
        with open(manifest_path) as manifest:
            for line in manifest: # pragma: no branch
                parts = line.split(':', 1)
                if len(parts) < 2:
                    continue
                name, value = parts
                key = name.lower().strip()
                value = value.strip()
                if key in data:
                    raise AssertionError((
                        'duplicate keys for %r found, '
                        'value was %r, now %r'
                        ) % (key, data[key], value))
                data[key] = value

        # check what I think is true is actually true!
        for a, b in (('extension-name', 'implementation-title'),
                     ('plugin-version', 'implementation-version')):
            if data[a] != data[b]:
                raise AssertionError('%s (%r) != %s (%r)' % (
                    a, data[a], b, data[b]
                    ))

        name = data['extension-name']
        filename = manifest_path.split(sep)[-3]
        if name in plugins:
            raise AssertionError('%r and %r both said they were %r' % (
                plugins[name][1], filename, name
                ))
        plugins[name]= data['plugin-version'], filename
    
    with open(make_path(config_folder, join(
        jenkins_home, 'plugin-versions.txt'
        )), 'w') as output:
        for name, info in sorted(plugins.items()):
            version, _ = info
            output.write('%s: %s\n' % (name, version))

    return ''
    
