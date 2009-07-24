from datetime import datetime, timedelta
from paste.script.command import Command
from paste.deploy import appconfig
from pylons import config
from urlparse import urljoin
import os
import logging

from novam.config.environment import load_environment

__all__ = ['AutoUpdatePlanetCommand']

class AutoUpdatePlanetCommand(Command):
	# Parser configuration
	summary = "Update bus stops"
	description = """
	"""
	usage = "server daily|hourly|minutely [config-file]"
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
	
		self.server = self.args[0]
		granularity = self.args[1]

		# Maximum number of days that are applied through a diff. This
		# should be equal or less than the number of planet diffs on
		# the planet-server. If the database is older a new planet 
		# import is suggested.
		MAX_DAYS = 6 

		current_ts = planet_timestamp.get()
		age = datetime.utcnow() - current_ts

		if age.days > MAX_DAYS:
			log.critical("Your database is too old. Please import a new planet dump.")
			return 1

		def retrieve_and_apply_diff(diff_granularity, start_time):
			TIME_FORMAT = {
				"daily": "%Y%m%d",
				"hourly": "%Y%m%d%H",
				"minute": "%Y%m%d%H%M"
			}
			
			if diff_granularity == "daily":
				end_time = start_time + timedelta(days=1)
				end_time = end_time.replace(hour=0, minute=0, second=0)
			elif diff_granularity == "hourly":
				end_time = start_time + timedelta(hours=1)
				end_time = end_time.replace(minute=0, second=0)
			elif diff_granularity == "minute":
				end_time = start_time + timedelta(minutes=1)
				end_time = end_time.replace(second=0)

			file_from = start_time.strftime(TIME_FORMAT[diff_granularity])
			file_to = end_time.strftime(TIME_FORMAT[diff_granularity])
			filename = "%s-%s.osc.gz" % (file_from, file_to)

			if self.server[:5] == "file:":
				url = os.path.join(self.server, diff_granularity, filename)
			else:
				url = urljoin(self.server, diff_granularity + "/" + filename)

			try:
				planet.load(url, end_time, planet.Updater())
				meta.session.commit()
			except e:
				log.warning(e.message())
				return start_time
			return end_time

		# Apply daily diffs:
		while age.days > 0:
			new_ts = retrieve_and_apply_diff("daily", current_ts)
			if new_ts == current_ts:
				log.info("No new daily diffs available yet. Please try again later.")
				break
			else:
				current_ts = new_ts
				age = datetime.utcnow() - current_ts

		# Apply hourly diffs:
		if granularity in ("hourly", "minutely"):
			while age.days > 0 or age.seconds / 3600 > 0:
				new_ts = retrieve_and_apply_diff("hourly", current_ts)
				if new_ts == current_ts:
					log.info("No new hourly diffs available yet. Please try again later.")
					break
				else:
					current_ts = new_ts
					age = datetime.utcnow() - current_ts

		# Apply minutely diffs:
		if granularity == "minutely":
			while age.days > 0 or age.seconds / 60 > 0:
				new_ts = retrieve_and_apply_diff("minute", current_ts)
				if new_ts == current_ts:
					log.info("No new minutely diffs available yet. Please try again later.")
					break
				else:
					current_ts = new_ts
					age = datetime.utcnow() - current_ts
