import os
from datetime import datetime
from paste.script.command import Command, BadCommand
from paste.deploy import appconfig
from pylons import config
import logging

from novam.config.environment import load_environment

__all__ = ['UpdatePlanetCommand']

class UpdatePlanetCommand(Command):
	# Parser configuration
	summary = "Update bus stops and naptan nodes from a osmosis changeset"
	description = """
	"""
	usage = "osmosis-changeset.osc timestamp [config-file]"
	group_name = "novam"
	parser = Command.standard_parser()
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

		# Configure logging from the config file
		self.logging_file_config(config_file)

		log = logging.getLogger(__name__)

		conf = appconfig(config_name, relative_to=here_dir)
		load_environment(conf.global_conf, conf.local_conf)

		import novam.lib.planet_osm as planet
		from novam.model import meta, planet_timestamp
		
		planet.load(self.args[0], datetime.strptime(self.args[1], planet_timestamp.FORMAT), planet.Updater())
		meta.session.commit()
