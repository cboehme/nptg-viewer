"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import config, url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test

from novam.model import meta

__all__ = ['environ', 'url', 'TestController']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([config['__file__']])

environ = {}

class TestController(TestCase):

	def __init__(self, *args, **kwargs):
		if pylons.test.pylonsapp:
			wsgiapp = pylons.test.pylonsapp
		else:
			wsgiapp = loadapp('config:%s' % config['__file__'])
		self.app = TestApp(wsgiapp)
		url._push_object(URLGenerator(config['routes.map'], environ))
		TestCase.__init__(self, *args, **kwargs)


def table_contents(table, contents):
	connection = meta.engine.connect()
	result = connection.execute(table.select())
	connection.close()
	rows = result.fetchall()
	for row in rows[:]:
		print row
		if row in contents:
			contents.remove(row)
			rows.remove(row)
	return len(rows) == 0 and len(contents) == 0

def table_is_empty(table):
	connection = meta.engine.connect()
	result = connection.execute(table.count())
	connection.close()
	return result.fetchone()[0] == 0
