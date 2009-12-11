# Copyright (c) 2009 Simplistix Ltd
# See license.txt for license details.

import os
from setuptools import setup

package_name = 'checker'
base_dir = os.path.dirname(__file__)

setup(
    name=package_name,
    version=file(os.path.join(base_dir,package_name,'version.txt')).read().strip(),
    author='Chris Withers',
    author_email='chris@simplistix.co.uk',
    license='MIT',
    description="A tool for checking system configuration.",
    long_description=open(os.path.join(base_dir,'docs','description.txt')).read(),
    url='http://www.simplistix.co.uk/software/python/checker',
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    ],    
    packages=[package_name],
    zip_safe=False,
    extras_require=dict(
        test=['mock','manuel'],
        )
    )
