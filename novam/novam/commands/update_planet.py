import os
from paste.script.command import Command
from paste.deploy import appconfig
from pylons import config

from xml.sax import parse, SAXException

from novam.config.environment import load_environment

class UpdatePlanetCommand(Command):
	# Parser configuration
	summary = "Update bus stops and naptan nodes from a osmosis changeset"
	description = """
	"""
	usage = "osmosis-changeset.osc"
	group_name = "novam"
	parser = Command.standard_parser(verbose=False)
	min_args = 1
	max_args = 2
	takes_config_file = -1

	def command(self):
		if len(self.args) == 1:
			# Assume the .ini file is ./development.ini
			config_file = "development.ini"
			if not os.path.isfile(config_file):
				raise BadCommand("%sError: CONFIG_FILE not found at: .%s%s\n"
				                 "Please specify a CONFIG_FILE" % \
				                 (self.parser.get_usage(), os.path.sep,
				                 config_file))
		else:
			config_file = self.args[1]

		config_name = "config:%s" % config_file
		here_dir = os.getcwd()

		if not self.options.quiet:
			# Configure logging from the config file
			self.logging_file_config(config_file)

		conf = appconfig(config_name, relative_to=here_dir)
		load_environment(conf.global_conf, conf.local_conf)

		from novam import model
		from novam.model.meta import session
		from novam.lib.OSMImporter import OSMUpdater
		
		planet_osc = self.args[0]
		parse(planet_osc, OSMUpdater())
