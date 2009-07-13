import os
from datetime import datetime
from paste.script.command import Command
from paste.deploy import appconfig
from pylons import config

from novam.config.environment import load_environment

__all__ = ['LoadPlanetCommand']

class LoadPlanetCommand(Command):
	# Parser configuration
	summary = "Import bus stops and naptan nodes from a planet.osm file"
	description = """Warning: This operation replaces all bus stops which are 
	currently stored in the database!
	"""
	usage = "file:planet.osm|http://www.example.org/planet.osm.bz2 timestamp [config-file]"
	group_name = "novam"
	parser = Command.standard_parser(verbose=False)
	min_args = 2
	max_args = 3

	def command(self):
		if len(self.args) == 2:
			# Assume the .ini file is ./development.ini
			config_file = "development.ini"
			if not os.path.isfile(config_file):
				raise BadCommand("%sError: CONFIG_FILE not found at: .%s%s\n"
				                 "Please specify a CONFIG_FILE" % \
				                 (self.parser.get_usage(), os.path.sep,
				                 config_file))
		else:
			config_file = self.args[2]

		config_name = "config:%s" % config_file
		here_dir = os.getcwd()

		if not self.options.quiet:
			# Configure logging from the config file
			self.logging_file_config(config_file)

		conf = appconfig(config_name, relative_to=here_dir)
		load_environment(conf.global_conf, conf.local_conf)

		import novam.lib.planet_osm as planet
		from novam.model import meta, planet_timestamp
		
		planet.load(self.args[0], datetime.strptime(self.args[1], planet_timestamp.FORMAT), planet.Importer())
		meta.session.commit()
