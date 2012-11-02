#!/usr/bin/python

#       pybit-web
#       Copyright 2012:
#
#		Nick Davidson <nickd@toby-churchill.com>,
#		Simon Haswell <simonh@toby-churchill.com>,
#		Neil Williams <neilw@toby-churchill.com>,
#		James Bennet <github@james-bennet.com / James.Bennet@toby-churchill.com>
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

import psycopg2
import psycopg2.extras
import jsonpickle
from pybit.models import Arch,Dist,Format,Status,Suite,BuildD,Job,Package,PackageInstance,SuiteArch,JobHistory, ClientMessage
from pybit.common import load_settings_from_file

myDb = None

class Database(object):

	conn = None

	#<<<<<<<< General database functions >>>>>>>>

	#Constructor, connects on initialisation.

	def __init__(self):
		print "DEBUG: DB constructor called."
		if not myDb: # DONT allow construction of more than 1 db instance (i.e. none other than the myDb here)
			print "DEBUG: DB Singleton constructor called."
			self.settings = load_settings_from_file('db_settings.json')
			self.connect()

	#Deconstructor, disconnects on disposal.
	def __del__(self):
		self.disconnect()

	#Connects to DB using settings loaded from file.
	def connect(self):
		try:
			self.conn = psycopg2.connect(database=self.settings['db_databasename'], user=self.settings['db_user'], host=self.settings['db_hostname'], port=self.settings['db_port'])
			return True
		except psycopg2.Error as e:
			raise Exception("Error connecting to database. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return False

	#Called by deconstructor
	def disconnect(self):
		try:
			if self.conn:
				self.conn.commit()
				self.conn.close()
			return True
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error disconnecting from database. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return False

	#<<<<<<<< Lookup table queries >>>>>>>>
	# Do we care about update or delete?

	def get_arches(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM arch ORDER BY name")
			res = cur.fetchall()
			self.conn.commit()

			arches = []
			for i in res:
				arches.append(Arch(i['id'],i['name']))
			cur.close()
			return arches
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving arches list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_arch_id(self,arch_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM arch WHERE id=%s",(arch_id,))
			res = cur.fetchall()
			self.conn.commit()
			arch = Arch(res[0]['id'],res[0]['name'])
			cur.close()
			return arch
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving arch with id:" + str(arch_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None


	def get_arch_byname(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM arch WHERE name=%s",(name,))
			res = cur.fetchall()
			self.conn.commit()

			arches = []
			for i in res:
				arches.append(Arch(i['id'],i['name']))
			cur.close()
			return arches
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving arch by name:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_arch(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT into arch(name) VALUES (%s) RETURNING id",(name,))
			res = cur.fetchall()
			self.conn.commit()
			arch = Arch(res[0]['id'],name)
			cur.close()
			return arch
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error adding arch:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_arch(self,arch_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM arch WHERE id=%s RETURNING id",(arch_id,))
			res = cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == arch_id:
				cur.close()
				return True
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting arch with id:" + str(arch_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_suitearches(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,suite_id,arch_id FROM suitearches ORDER BY id")
			res = cur.fetchall()
			self.conn.commit()

			suite_arches = []
			for i in res:
				suite_arches.append(SuiteArch(i['id'],i['suite_id'],i['arch_id']))
			cur.close()
			return suite_arches
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving suite arches list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_suitearch_id(self,suitearch_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,suite_id,arch_id FROM suitearches WHERE id=%s",(suitearch_id,))
			res = cur.fetchall()
			self.conn.commit()
			suitearch = SuiteArch(res[0]['id'],res[0]['suite_id'],res[0]['arch_id'])
			cur.close()
			return suitearch
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving suite arch with id:" + str(suitearch_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_suitearch(self,suite_id,arch_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT into suitearches(suite_id,arch_id) VALUES (%s, %s) RETURNING id",(suite_id,arch_id))
			res = cur.fetchall()
			self.conn.commit()
			suitearch = SuiteArch(res[0]['id'],suite_id,arch_id)
			cur.close()
			return suitearch
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error adding suite arch:" + suite_id + arch_id + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_suitearch(self,suitearch_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM suitearches WHERE id=%s RETURNING id",(suitearch_id,))
			res = cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == suitearch_id:
				cur.close()
				return True
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting suitearch with id:" + str(suitearch_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_dists(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM distribution ORDER BY name")
			res = cur.fetchall()
			self.conn.commit()

			dists = []
			for i in res:
				dists.append(Dist(i['id'],i['name']))
			cur.close()
			return dists
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving dist list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_dist_id(self,dist_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM distribution WHERE id=%s",(dist_id,))
			res = cur.fetchall()
			self.conn.commit()
			dist = Dist(res[0]['id'],res[0]['name'])
			cur.close()
			return dist
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving dist with id:" + str(dist_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None


	def get_dist_byname(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM distribution WHERE name=%s",(name,))
			res = cur.fetchall()
			self.conn.commit()

			dists = []
			for i in res:
				dists.append(Dist(i['id'],i['name']))
			cur.close()
			return dists
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving dist by name:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_dist(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT into distribution(name) VALUES (%s)  RETURNING id",(name,))
			res = cur.fetchall()
			self.conn.commit()
			dist = Dist(res[0]['id'],name)
			cur.close()
			return dist
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error adding dist:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_dist(self,dist_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM distribution WHERE id=%s RETURNING id",(dist_id,))
			res = cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == dist_id:
				cur.close()
				return True
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting dist with id:" + str(dist_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_formats(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM format ORDER BY name")
			res = cur.fetchall()
			self.conn.commit()

			formats = []
			for i in res:
				formats.append(Format(i['id'],i['name']))
			cur.close()
			return formats
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving formats list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_format_id(self,format_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM format WHERE id=%s",(format_id,))
			res = cur.fetchall()
			self.conn.commit()
			format = Format(res[0]['id'],res[0]['name'])
			cur.close()
			return  format
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving format with id:" + str(format_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None


	def get_format_byname(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM format WHERE name=%s",(name,))
			res = cur.fetchall()

			formats = []
			for i in res:
				formats.append(Format(i['id'],i['name']))
			cur.close()
			return formats
		except psycopg2.Error as e:
			raise Exception("Error retrieving format by name:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_format(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT into format(name) VALUES (%s)  RETURNING id",(name,))
			res = cur.fetchall()
			self.conn.commit()
			format = Format(res[0]['id'],name)
			cur.close()
			return format
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error adding format:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_format(self,format_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM format WHERE id=%s RETURNING id",(format_id,))
			res = cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == format_id:
				cur.close()
				return True
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting format with id:" + str(format_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_statuses(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM status ORDER BY name")
			res = cur.fetchall()
			self.conn.commit()

			statuses = []
			for i in res:
				statuses.append(Status(i['id'],i['name']))
			cur.close()
			return statuses
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving status list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_status_id(self,status_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM status WHERE id=%s",(status_id,))
			res = cur.fetchall()
			self.conn.commit()
			status = Status(res[0]['id'],res[0]['name'])
			cur.close()
			return status
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving status with id:" + str(status_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_status(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT into status(name) VALUES (%s)  RETURNING id",(name,))
			res = cur.fetchall()
			self.conn.commit()
			status = Status(res[0]['id'],name)
			cur.close()
			return status
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error add status:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_status(self,status_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM status WHERE id=%s RETURNING id",(status_id,))
			res = cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == status_id:
				cur.close()
				return True
			else:
				cur.cloes()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting status with id:" + str(status_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_suites(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM suite ORDER BY name")
			res = cur.fetchall()
			self.conn.commit()

			suites = []
			for i in res:
				suites.append(Suite(i['id'],i['name']))
			cur.close()
			return suites
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving suite list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_suite_id(self,suite_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM suite WHERE id=%s",(suite_id,))
			res = cur.fetchall()
			self.conn.commit()
			suite = Suite(res[0]['id'],res[0]['name'])
			cur.close()
			return suite
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving suite with id:" + str(suite_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None


	def get_suite_byname(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM suite WHERE name=%s",(name,))
			res = cur.fetchall()
			self.conn.commit()

			suites = []
			for i in res:
				suites.append(Suite(i['id'],i['name']))
			cur.close()
			return suites
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving suite with name:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_suite(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT into suite(name) VALUES (%s)  RETURNING id",(name,))
			res = cur.fetchall()
			self.conn.commit()
			suite = Suite(res[0]['id'],name)
			cur.close()
			return suite
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error adding suite:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_suite(self,suite_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM suite WHERE id=%s RETURNING id",(suite_id,))
			res = cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == suite_id:
				cur.close()
				return True
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting suite with id:" + str(suite_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	#<<<<<<<< BuildD related database functions >>>>>>>>

	def get_buildclients(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM buildclients ORDER BY name")
			res = cur.fetchall()
			self.conn.commit()

			build_clients = []
			for i in res:
				build_clients.append(BuildD(i['id'],i['name']))
			cur.close()
			return build_clients
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving buildd list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_buildd_id(self,buildd_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name FROM buildclients WHERE id=%s",(buildd_id,))
			res = cur.fetchall()
			self.conn.commit()
			buildd = BuildD(res[0]['id'],res[0]['name'])
			cur.close()
			return buildd
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving buildd with id:" + str(buildd_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_buildclient(self,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT into buildclients(name) VALUES (%s)  RETURNING id",(name,))
			res = cur.fetchall()
			self.conn.commit()
			buildd = BuildD(res[0]['id'],name)
			cur.close()
			return buildd
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error adding buildd:" + name + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_buildclient(self,buildclient_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM buildclients WHERE id=%s RETURNING id",(buildclient_id,))
			res = cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == buildclient_id:
				cur.close()
				return True
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting buildd with id:" + str(buildclient_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_buildd_jobs(self,buildclient_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT job.id AS job_id,packageinstance_id,buildclients.id AS buildclients_id FROM buildclients,job WHERE buildclients.id=%s AND buildclients.id = job.buildclient_id  ORDER BY job.id",(buildclient_id,))
			res = cur.fetchall()
			self.conn.commit()

			jobs = []
			for i in res:
				packageinstance = self.get_packageinstance_id(i['packageinstance_id'])
				jobs.append(jobs.append(Job(i['job_id'],packageinstance,buildclient_id)))
			cur.close()
			return jobs
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving jobs on buildd with id:" + str(buildclient_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	#<<<<<<<< Job related database functions >>>>>>>>
	# UPDATE queries?

	def get_job(self,job_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job WHERE id=%s",(job_id,))
			res = cur.fetchall()
			self.conn.commit()

			packageinstance = self.get_packageinstance_id(res[0]['packageinstance_id'])
			buildclient = self.get_buildd_id(res[0]['buildclient_id']) if res[0]['buildclient_id'] else None
			job = Job(res[0]['id'],packageinstance,buildclient)
			cur.close()
			return job
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving job with id:" + str(job_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_jobs(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,packageinstance_id,buildclient_id FROM job ORDER BY id")
			res = cur.fetchall()
			self.conn.commit()

			jobs = []
			for i in res:
				packageinstance = self.get_packageinstance_id(i['packageinstance_id'])
				buildclient = self.get_buildd_id(i['buildclient_id']) if i['buildclient_id'] else None
				jobs.append(Job(i['id'],packageinstance,buildclient))
			cur.close()
			return jobs
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving jobs list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_jobs_by_status(self,status):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("WITH latest_status AS (SELECT DISTINCT ON (job_id) job_id, status.name FROM jobstatus LEFT JOIN status ON status_id=status.id ORDER BY job_id, time DESC) SELECT job_id, name FROM latest_status WHERE name=%s",(status,));
			res = cur.fetchall()
			self.conn.commit()

			jobs = []
			for i in res:
				jobs.append(self.get_job(i['job_id']))
			cur.close()
			return jobs
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving jobs list with status:" + status + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_unfinished_jobs(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("WITH latest_status AS (SELECT DISTINCT ON (job_id) job_id, status.name FROM jobstatus LEFT JOIN status ON status_id=status.id ORDER BY job_id, time DESC) SELECT job_id, name FROM latest_status WHERE name!='Uploaded' AND name!='Done' ORDER BY job_id");
			res = cur.fetchall()
			self.conn.commit()

			jobs = []
			for i in res:
				jobs.append(self.get_job(i['job_id']))
			return jobs
			cur.close()
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving unfinished jobs. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_job_statuses(self,job_id):
	#gets job status *history*
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT job.id AS job_id, status.name AS status, buildclients.name AS buildclient, jobstatus.time AS time FROM job LEFT JOIN jobstatus ON job.id=jobstatus.job_id LEFT JOIN status ON jobstatus.status_id=status.id  LEFT JOIN buildclients ON buildclients.id=job.buildclient_id WHERE job.id = %s ORDER BY time",(job_id,));
			res = cur.fetchall()
			self.conn.commit()
			jobstatuses = []
			for i in res:
				jobstatuses.append(JobHistory(i['job_id'],i['status'],i['buildclient'],i['time']))
			cur.close()
			return jobstatuses
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving job status with:" + str(job_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_job_status(self, jobid, status, client=None):
		try:
			print "put_job_status: %s %s %s", (jobid, status, client)
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT INTO jobstatus (job_id, status_id) VALUES (%s, (SELECT id FROM status WHERE name=%s))",
					 (jobid,status,))
			if client is not None:
				#insert the client if it doesn't already exist.
				cur.execute("INSERT INTO buildclients(name) SELECT name FROM buildclients UNION VALUES(%s) EXCEPT SELECT name FROM buildclients",
						(client,))
				
				cur.execute("UPDATE job SET buildclient_id=(SELECT id FROM buildclients WHERE name=%s) WHERE id=%s",
						 (client,jobid))
			self.conn.commit()
			cur.close()
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error setting job status. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_job(self,job_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM job WHERE id=%s  RETURNING id",(job_id,))
			res = cur.fetchall()
			self.conn.commit()
			if res[0]['id'] == job_id:
				cur.close()
				return True
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting job with:" + str(job_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_job(self,packageinstance,buildclient):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT INTO job (packageinstance_id,buildclient_id) VALUES (%s, %s)  RETURNING id",(packageinstance.id,(buildclient.id if buildclient else None)))
			res = cur.fetchall()

			job_id = res[0]['id']
			if job_id is not None:
				cur.execute("INSERT INTO jobstatus (job_id, status_id) VALUES (%s, (SELECT id FROM status WHERE status.name=%s))",
					(job_id, ClientMessage.waiting))
				self.conn.commit()
			else:
				self.conn.rollback()

			job =  Job(job_id,packageinstance,buildclient)
			cur.close()
			return job
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error adding job. Database error code: " + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	#<<<<<<<< Package related database functions >>>>>>>>
	# UPDATE queries?
	def get_packages(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,version,name FROM package ORDER BY name,id")
			res = cur.fetchall()
			self.conn.commit()

			packages = []
			for i in res:
				packages.append(Package(i['id'],i['version'],i['name']))
			cur.close()
			return packages
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving packages list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_packages_byname(self, name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,version,name FROM package WHERE name=%s",(name,))
			res = cur.fetchall()
			self.conn.commit()

			packages = []
			for i in res:
				packages.append(Package(i['id'],i['version'],i['name']))
			cur.close()
			return packages
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving package with name:" + str(name) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_package_id(self,package_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,version,name FROM package WHERE id=%s",(package_id,))
			res = cur.fetchall()
			self.conn.commit()
			package = Package(res[0]['id'],res[0]['version'],res[0]['name'])
			cur.close()
			return package
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving package with id:" + str(package_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None


	def get_package_byvalues(self,name,version):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,name,version FROM package WHERE name=%s AND version=%s",(name,version))
			res = cur.fetchall()
			self.conn.commit()

			packages = []
			for i in res:
				packages.append(Package(i['id'],i['version'],i['name']))
			cur.close()
			return packages
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving package by values:" + name + version + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_package(self,version,name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT into package(version,name) VALUES (%s, %s)  RETURNING id",(version,name))
			res = cur.fetchall()
			self.conn.commit()
			package = Package(res[0]['id'],version,name)
			cur.close()
			return package
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error adding package:" + name + version + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_package(self,package_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM package WHERE id=%s  RETURNING id",(package_id,))
			res = cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == package_id:
				cur.close()
				return True
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting package with:" + str(package_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	#<<<<<<<<< Packageinstance related Queries >>>>>>>

	def get_packageinstance_id(self,packageinstance_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance  WHERE id=%s",(packageinstance_id,))
			res = cur.fetchall()
			self.conn.commit()

			package = self.get_package_id(res[0]['package_id'])
			arch = self.get_arch_id(res[0]['arch_id'])
			suite = self.get_suite_id(res[0]['suite_id'])
			dist = self.get_dist_id(res[0]['dist_id'])
			pkg_format = self.get_format_id(res[0]['format_id'])
			p_i = PackageInstance(res[0]['id'],package,arch,suite,dist,pkg_format,res[0]['master'])
			cur.close()
			return p_i 
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving package instance with:" + str(packageinstance_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_packageinstances(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance ORDER BY id")
			res = cur.fetchall()
			self.conn.commit()

			packageinstances = []
			for i in res:
				packageinstances.append(self.get_packageinstance_id(i['id']))
			cur.close()
			return packageinstances
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving package instances list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_packageinstances_byname(self, name):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT packageinstance.id AS id,package.id AS package_id ,arch_id,suite_id,dist_id,format_id,master FROM packageinstance,package WHERE packageinstance.package_id = package.id AND name = %s ORDER BY package_id, id",(name,))
			res = cur.fetchall()
			self.conn.commit()

			packageinstances = []
			for i in res:
				packageinstances.append(self.get_packageinstance_id(i['id']))
			cur.close()
			return packageinstances
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving package instances by name. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None


	def get_packageinstance_byvalues(self,package,arch,suite,dist,pkg_format):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT id,package_id,arch_id,suite_id,dist_id,format_id,master FROM packageinstance WHERE package_id=%s AND arch_id=%s AND suite_id=%s AND dist_id=%s AND format_id=%s",(package.id,arch.id,suite.id,dist.id,pkg_format.id))
			res = cur.fetchall()
			self.conn.commit()

			packageinstances = []
			for i in res:
				packageinstances.append(self.get_packageinstance_id(i['id']))
			cur.close()
			return packageinstances
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving package instance by value. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def put_packageinstance(self,package,arch,suite,dist,pkg_format,master):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("INSERT into packageinstance(package_id,arch_id,suite_id,dist_id,format_id,master) VALUES (%s, %s, %s, %s, %s, %s)  RETURNING id",(package.id,arch.id,suite.id,dist.id,pkg_format.id,master))
			self.conn.commit()
			res = cur.fetchall()
			self.conn.commit()
			p_i = PackageInstance(res[0]['id'],package,arch,suite,dist,pkg_format,master)
			cur.close()
			return p_i 
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error adding package instance:" + str(package.id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def delete_packageinstance(self,packageinstance_id):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("DELETE FROM packageinstance WHERE id=%s RETURNING id",(packageinstance_id,))
			res = cur.fetchall()
			self.conn.commit()

			if res[0]['id'] == packageinstance_id:
				cur.close()
				return True
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error deleting package instance with:" + str(packageinstance_id) + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def check_specific_packageinstance_exists(self,arch,package,distribution,pkg_format,suite):
		try:
			if arch and distribution and pkg_format and package and suite:
				cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
				cur.execute("SELECT id FROM packageinstance WHERE arch_id=%s AND dist_id=%s AND format_id=%s AND package_id=%s AND suite_id=%s",(arch.id,distribution.id,pkg_format.id,package.id,suite.id))
				res = cur.fetchall()
				self.conn.commit()

				if len(res) > 0:
					#Found specific package instance
					cur.close()
					return True
				else:
					# doesnt exist
					#Cannot find specific package instance
					cur.close()
					return False
			else:
				#Error finding specific package instance
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error checking package instance exists. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None
	#<<<<<<<<< Report Queries >>>>>>>

	def get_report_package_instance(self):
		try:
			cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			cur.execute("SELECT packageinstance.id, suite.name AS suite, package.name AS package, package.version AS version, arch.name AS arch, format.name AS format, distribution.name AS dist, packageinstance.master AS master FROM packageinstance LEFT JOIN arch ON arch.id=arch_id LEFT JOIN suite ON suite.id=suite_id LEFT JOIN distribution ON distribution.id=dist_id LEFT JOIN package ON package_id=package.id LEFT JOIN format ON format_id=format.id")
			res = cur.fetchall()
			self.conn.commit()

			package_instances = []
			for i in res :
				package_instances.append(PackageInstance(i['id'], i['package'], i['arch'], i['suite'], i['dist'], i['format'], i['master']))
			cur.close()
			return package_instances
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving package instance list. Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

	def get_supported_architectures(self,suite) :
		try:
			if suite :
				cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
				cur.execute("SELECT arch.id, arch.name FROM suite LEFT JOIN suitearches ON suite.id=suite_id LEFT JOIN arch ON arch_id = arch.id WHERE suite.name=%s",[suite])
				res = cur.fetchall()
				self.conn.commit()

				arch_list = []
				for i in res :
					arch_list.append(i['name'])
				cur.close()
				return arch_list
			else:
				cur.close()
				return False
		except psycopg2.Error as e:
			self.conn.rollback()
			raise Exception("Error retrieving supported architectures for:" + suite + ". Database error code: "  + str(e.pgcode) + " - Details: " + str(e.pgerror))
			return None

myDb = Database() # singleton instance
