#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of captlog.
#
# captlog - The Captain's Log (secret diary and notes application)
#
# Written in 2013 by Ricardo Garcia <r@rg3.name>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.
from distutils.core import setup

VERSION = '0.1.1'

setup(
    name='captlog',
    version=VERSION,
    description="The Captain's Log (secret diary and notes application)",
    author='Ricardo Garcia',
    author_email='r@rg3.name',
    url='http://www.github.com/rg3/captlog',
    packages=['CaptainsLog'],
    package_dir={'CaptainsLog': 'src/lib'},
    package_data={'CaptainsLog': ['pixmap/*']},
    scripts=['src/bin/captlog'],
    provides=['CaptainsLog (%s)' % (VERSION, )],
    requires=['Crypto (>=2.6)'],
    )
