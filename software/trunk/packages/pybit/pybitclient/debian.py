#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       debian.py
#
#       Copyright 2012 Neil Williams <codehelp@debian.org>
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

import os
import json
import pybitclient
from buildclient import BuildClient

report_name = "controller"

class DebianBuildClient(BuildClient):
	options = {}

	def update_environment(self,name):
		try:
			command = "schroot -u root -c %s -- apt-get update > /dev/null 2>&1" % (name)
			if self.run_cmd (command, "failed", report_name, self.options["dry_run"]):
				return
		except Exception as e:
			raise Exception('Error updating build environment: ' + str(e))
			return

	def build_master (self, srcdir, pkg):
		try:
			if (not hasattr(pkg, 'package')):
				print "E: not able to identify package name."
				return
			package_dir = "%s/%s" % (srcdir, pkg.package)
			builddir= "%s/tmpbuilds/%s" % (buildroot, pkg.suite)
			if os.path.isdir(package_dir) :
				os.chdir (package_dir)
				command = "dpkg-checkbuilddeps"
				if run_cmd (command, "build-dep-wait", report_name, self.options["dry_run"]):
					return
			command = "dpkg-buildpackage -S -d > /dev/null 2>&1"
			if run_cmd (command, "failed", report_name, self.options["dry_run"]):
				return
			command = "sbuild -A -s -d %s%s/%s_%s.dsc" % (pkg.suite, srcdir, pkg.source, pkg.version)
			if run_cmd (command, "failed", report_name, self.options["dry_run"]):
				return
			changes = "%s/%s_%s_%s.changes" % (builddir, pkg.package, pkg.version, pkg.architecture)
			if not os.path.isfile (changes) :
				pkg.msgtype = "failed"
				send_message (chan, pkg, report_name)
				return
			upload (changes)
		except Exception as e:
			raise Exception('Error performing master build: ' + str(e))
			return

	def upload (changes):
		try:
			builddir= buildroot + "/tmpbuilds/" + pkg.suite
			command = "dput -c %s %s %s %s" % (dput_cfg, dput_opt, dput_dest, changes)
			if run_cmd (command, "failed", report_name, self.options["dry_run"]):
				return
			pkg.msgtype = "uploaded"
			send_message (chan, pkg, report_name)
		except Exception as e:
			raise Exception('Upload error: ' + str(e))
			return

	def build_slave (self, srcdir, pkg):
		try:
			command = "sbuild -d %s %s_%s" % (pkg.suite, pkg.source, pkg.version)
			if run_cmd (command, "failed", report_name, self.options["dry_run"]):
				return
			changes = "%s/%s_%s_%s.changes" % (builddir, pkg.package, pkg.version, pkg.architecture)
			if not os.path.isfile (changes) :
				pkg.msgtype = "failed"
				send_message (chan, pkg, report_name)
				return
			upload (changes)
		except Exception as e:
			raise Exception('Error performing slave build: ' + str(e))
			return

	def __init__(self):
		try:
			BuildClient.__init__(self)
			# Specific buildd options
			# FIXME: decide how this is managed and packaged
			self.options =  pybitclient.get_settings(self)
			if len(self.options) > 0 :
				dput_opt = self.options["dput"]
				buildroot = self.options["buildroot"]
			else :
				self.options["dry_run"] = True
			# variables to retrieve from the job object later
			#dput_dest = "tcl"
			dput_cfg = "/etc/pybit/dput.cf"
		except Exception as e:
			raise Exception('Error constructing debian build client: ' + str(e))
			return