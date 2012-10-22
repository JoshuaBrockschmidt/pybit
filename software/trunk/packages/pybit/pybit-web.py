#!/usr/bin/python

import jsonpickle
from pybitweb.bottle import Bottle,route,run,template,debug,HTTPError,response,error,redirect,request
from pybitweb.db import db
from pybitweb import buildd,forms,job,lookups,reports
from pybit.models import package,packageinstance
from pybitweb.controller import controller

myDb = db()
buildController = controller(myDb)

def load_settings_from_file(path):
	settings_file = open(path, 'r')
	encoded_string = settings_file.read()
	settings = jsonpickle.decode(encoded_string )
	return settings

settings = load_settings_from_file('configs/web_settings.json')

@error(404)
def error404(error):
    return 'HTTP Error 404 - Not Found.'

# Remove this to get more debug.
#@error(500)
#def error404(error):
#    return 'HTTP Error 500 - Internal Server Error.'

@route('/', method='GET')
def index():
	#main index page for the whole API, composed of forms and reports pages
	return '''<h1>PyBit - python Buildd Integration Toolkit.</h1>''', forms.index() , reports.index()

route('/add', method='POST') (buildController.add)
# example CURL command....
# /usr/bin/curl -X POST http://localhost:8080/add --data "uri=http://svn.tcl.office/svn/lwdev&directory=software/branches/software_release_chickpea/packages/appbarwidget&method=svn&distribution=Debian&vcs_id=20961&architecture_list=all,any&package_version=0.6.33chickpea47&package=appbarwidget&suite=chickpea&format=deb"

route('/cancel_all', method='POST') (buildController.cancelAllBuilds)
#/usr/bin/curl -X POST http://localhost:8080/cancel_all"

route('/cancel_package', method='POST') (buildController.cancelPackage)
#/usr/bin/curl -X POST http://localhost:8080/cancel_package --data "package_version=0.6.33chickpea47&package=appbarwidget"

route('/cancel_package_instance', method='POST') (buildController.cancelPackageInstance)
#/usr/bin/curl -X POST http://localhost:8080/cancel_package_instance --data "job_id=54"

try:
	debug(settings['debug'])
	run(host=settings['host'], port=settings['port'], reloader=settings['reloader'])
except Exception as e:
		raise Exception('Error starting web server: ' + str(e))
