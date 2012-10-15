#!/usr/bin/python

from bottle import Bottle,response,error,request
from amqplib import client_0_8 as amqp
import jsonpickle
import os.path

from common.db import db
from common.models import transport, packageinstance, job
# example CURL command....
# /usr/bin/curl -X POST http://localhost:8080/add --data "uri=http://svn.tcl.office/svn/lwdev&directory=software/branches/software_release_chickpea/packages/appbarwidget&method=svn&distribution=Debian&vcs_id=20961&architecture_list=all,any&package_version=0.6.33chickpea47&package=appbarwidget&suite=chickpea&format=deb"

# PyBit setup variables - package content
queue_name = "rabbit"
report_name = "controller"
listening_name = "buildd"
dput_cfg = "/etc/pybit/client/dput.cf"

class controller:

	def __init__(self, jobDb):
		self.job_db = jobDb
		print "controller init"

	def add(self):
		uri = request.forms.get('uri')
		method = request.forms.get('method')
		dist = request.forms.get('distribution')
		vcs_id = request.forms.get('vcs_id')
		architectures = request.forms.get('architecture_list')
		version = request.forms.get('package_version')
		package_name = request.forms.get('package')
		suite = request.forms.get('suite')
		format = request.forms.get('format')
		
		trans = transport(None, method, uri, vcs_id)

		if not uri and method and dist and vcs_id and architectures and version and package_name and suite and format :
			response.status = "400 - Required fields missing."
			return

		supported_arches = self.job_db.supportedArchitectures(suite)

		if (len(supported_arches) == 0):
			response.status = "404 - no supported architectures for this suite."
			return

		if (architectures and len(architectures) == 1 and architectures[0] == "all"):
			# TODO: check_specific_packageinstance_exists
			new_packageinstance = packageinstance(suite, package_name, version, supported_arches[0], format, dist, trans)
		else :
			current_package = None
			matching_package_versions = self.job_db.get_package_byvalues(package_name,version)
			if len(matching_package_versions) < 0 :
				print "FOUND", len(matching_package_versions)
				current_package = matching_package_versions[0] #FIXME: 
			else :
				print "NO PACKAGE FOUND"
				# add new package to db
				current_package = self.job_db.put_package(version,package_name)
				if not current_package.id : 
					#TODO: throw error???
					print "FAILED TO ADD PACKAGE:", package_name
					response.status = "404 - failed to add package."
					return
			for arch in supported_arches:
				if not self.job_db.check_specific_packageinstance_exists(arch, dist, format, package_name, version, suite) :
					# add package instance to db
					new_packageinstance = self.job_db.put_packageinstance(current_package.id,arch,suite,dist,format,False)
					if new_packageinstance.id : 
						print "ADDED", new_packageinstance.id
						# TODO: check if database contains a package where status = building, version < package_version, suite = suite
						new_job = self.job_db.add(new_packageinstance.id, None)
						if new_job.id :
							print "ADDED", job.id
							#TODO: add job to message queue
#							msg = amqp.Message(jsonpickle.encode(instance))
#							msg.properties["delivery_mode"] = 2
#							chan.basic_publish(msg,exchange="i386",routing_key="buildd")
						else :
							print "FAILED TO ADD JOB"
							response.status = "404 - failed to add job."
					else : 
						print "FAILED TO ADD PACKAGE INSTANCE!"
						response.status = "404 - failed to add package instance."
			# cancel any job older jobs matching this package on queue
		return

	def cancelAllBuilds(self):
		return

	def cancelPackage(self):
		
		return

	def cancelPackageInstance(self):
		return
