from datetime import datetime, timedelta
from paste.script.command import Command
from paste.deploy import appconfig
from pylons import config

from novam.config.environment import load_environment

__all__ = ['AutoUpdatePlanetCommand']

class AutoUpdatePlanetCommand(Command):
	# Parser configuration
	summary = "Update bus stops"
	description = """
	"""
	usage = "server daily|hourly|minutely [config-file]"
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
		from novam.model import planet_timestamp
	
		self.server = self.argv[0]
		granularity = self.argv[1]

		# Maximum number of days that are applied through a diff. This
		# should be equal or less than the number of planet diffs on
		# the planet-server. If the database is older a new planet 
		# import is suggested.
		MAX_DAYS = 6 

		current_ts = planet_timestamp.get()
		age = datetime.utcnow() - current_ts

		if age.days > MAX_DAYS:
			print "Your database is too old. Please import a new planet dump."
			return

		def retrieve_and_apply_diff(diff_granularity):
			TIME_FORMAT = {
				"daily": "%Y%m%d",
				"hourly": "%Y%m%d%H",
				"minutely": "%Y%m%d%H%M"
			}

			if diff_granularity == "daily":
				end_time = start_time + timedelta(days=1)
				end_time = end_time.replace(hour=0, minute=0, second=0)
			elif diff_granularity == "hourly":
				end_time = start_time + timedelta(hours=1)
				end_time = end_time.replace(minute=0, second=0)
			elif diff_granularity == "minutely":
				end_time = start_time + timedelta(minutes=1)
				end_time = end_time.replace(second=0)

			file_from = start_time.strftime(TIME_FORMAT[diff_granularity])
			file_to = end_time.strftime(TIME_FORMAT[diff_granularity])
			filename = "%s-%s.osc.gz" % (file_from, file_to)

			# Retrieve timestamp for latest available diff on the server:
			fh = urlopen(self.server + "/" + diff_type + "/timestamp.txt")
			latest = datetime.strptime(fh.read(20), planet_timestamp.TIMESTAMP_FORMAT)
			fh.close();
			if end_time <= latest:
				planet.load(self.server + "/" + diff_type + "/" + filename, end_time, planet.Updater())
				current_ts = end_time
				age = datetime.utcnow() - current_ts
				return True
			else:
				return False

		# Apply daily diffs:
		while age.days > 0:
			if not retrieve_and_apply_diff("daily"):
				print "No new daily diffs available yet. Please try later again"
				return

		# Apply hourly diffs:
		if granularity in ("hourly", "minutely"):
			while age.seconds / 3600 > 0:
				if not retrieve_and_apply_diff("hourly"):
					print "No new hourly diffs available yet. Please try later again"
					return

		# Apply minutely diffs:
		if granularity == "minutely":
			while (age.seconds % 3600) / 60 > 0:
				if not retrieve_and_apply_diff("hourly"):
					print "No new minutely diffs available yet. Please try later again"
					return
