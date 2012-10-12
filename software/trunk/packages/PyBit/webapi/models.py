#!/usr/bin/python

# TODO: Change DB methods and associated HTTP GEThandlers to work on these JSON objects, rather than returning the raw resultsets themselves, which are a pain to deserialise.

import jsonpickle

# new
class model(object):
	def toJson(self):
		try:
			return jsonpickle.encode(self)
		except Exception as e:
			raise Exception('Error in toJson(): ' + str(e))
			return None
	def fromJson(self,jsonstring):
		try:
			self = jsonpickle.decode(jsonstring)
			return self
		except Exception as e:
			raise Exception('Error in fromJson(): ' + str(e))
			return None

class arch(model):

	def __init__(self,id,name):
		self.id = id
		self.name = name

class dist(model):

	def __init__(self,id,name):
		self.id = id
		self.name = name

class format(model):

	def __init__(self,id,name):
		self.id = id
		self.name = name

class status(model):

	def __init__(self,id,name):
		self.id = id
		self.name = name

class suite(model):

	def __init__(self,id,name):
		self.id = id
		self.name = name

class buildd(model):

	def __init__(self,id,name):
		self.id = id
		self.name = name

class job(model):

	def __init__(self,id,packageinstance_id,buildclient_id):
		self.id = id
		self.packageinstance_id = packageinstance_id
		self.buildclient_id = buildclient_id

class package(model):

	def __init__(self,id,version,name):
		self.id = id
		self.version = version
		self.name = name
		
class transport(model) :

	def __init__(self,id,method,uri,vcs_id):
		self.id = id
		self.method = method
		self.uri = uri
		self.vcs_id = vcs_id

class packageinstance(model):

	def __init__(self, id, suite, package, version, arch, format, distribution) :
		self.id = id
		self.suite = suite
		self.version = version
		self.arch = arch
		self.format = format
		self.distribution = distribution
