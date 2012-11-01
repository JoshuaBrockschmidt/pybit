#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       setup.py
#
#       Copyright 2012 Neil Williams <codehelp@debian.org>
#       Copyright (C) 2006 James Westby <jw+debian@jameswestby.net>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from setuptools import setup

setup(name='pybit-common',
	version='0.1.0',
	description='PyBit common modules',
	licence='gpl2'
	url='https://github.com/nicholasdavidson/pybit.git',
	packages=['pybit'],
	maintainer='TCL Build System user',
	maintainer_email='rnd@toby-churchill.com',
	)

setup(name='pybit-client',
	version='0.1.0',
	description='PyBit client related modules',
	licence='gpl2'
	url='https://github.com/nicholasdavidson/pybit.git',
	packages=['pybitclient'],
	maintainer='TCL Build System user',
	maintainer_email='rnd@toby-churchill.com',
	test_suite='tests'
	)

setup(name='pybit-web',
	version='0.1.0',
	description='PyBit controller and RESTful API',
	licence='gpl2'
	url='https://github.com/nicholasdavidson/pybit.git',
	packages=['pybitweb'],
	maintainer='TCL Build System user',
	maintainer_email='rnd@toby-churchill.com',
	)