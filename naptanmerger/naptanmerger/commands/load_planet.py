import os
from paste.script.command import Command
from paste.deploy import appconfig
from pylons import config

from xml.sax import parse, SAXException

from naptanmerger.config.environment import load_environment

class LoadPlanet(Command):
	# Parser configuration
	summary = "Import bus stops and naptan nodes from a planet.osm file"
	description = """Warning: This operation replaces all bus stops which are 
	currently stored in the database!
	"""
	usage = "planet.osm"
	group_name = "naptanmerger"
	parser = Command.standard_parser(verbose=False)
	min_args = 1
	max_args = 1

	def command(self):
		#TODO: Add support for specifing config files
		#if len(self.args) == 0:
		#	# Assume the .ini file is ./development.ini
		#	config_file = "development.ini"
		#	if not os.path.isfile(config_file):
		#		raise BadCommand("%sError: CONFIG_FILE not found at: .%s%s\n"
		#		                 "Please specify a CONFIG_FILE" % \
		#		                 (self.parser.get_usage(), os.path.sep,
		#		                 config_file))
		#	else:
		#		config_file = self.args[0]
		config_file = "development.ini"

		config_name = "config:%s" % config_file
		here_dir = os.getcwd()

		if not self.options.quiet:
			# Configure logging from the config file
			self.logging_file_config(config_file)

		conf = appconfig(config_name, relative_to=here_dir)
		load_environment(conf.global_conf, conf.local_conf)

		from naptanmerger import model
		from naptanmerger.model.meta import session
		from naptanmerger.lib.OSMImporter import OSMImporter
		
		session.execute(model.stops.delete())
		session.commit();

		planet_osm = self.args[0]
		parse(planet_osm, OSMImporter())
