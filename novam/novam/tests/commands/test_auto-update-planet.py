from decimal import Decimal
from datetime import datetime, date, time, timedelta
from unittest import TestCase
from scripttest import TestFileEnvironment
from pylons import config

from novam.tests import table_contents, table_is_empty
from novam.model import meta
from novam import model

class TestAutoUpdatePlanetCommand(TestCase):

	def __init__(self, *args, **kwargs):
		self.env = TestFileEnvironment("./test_output")
		TestCase.__init__(self, *args, **kwargs)

	def setUp(self):
		connection = meta.engine.connect()
		connection.execute("TRUNCATE TABLE Tags")    # Use truncate to reset auto-increment
		connection.execute("TRUNCATE TABLE Stops")
		connection.execute(
			model.stops.insert().values(id=1, lat=Decimal("52.3"), lon=Decimal("-1.9"), osm_id=123, osm_version=2)
		)
		connection.execute(
			model.tags.insert().values(stop_id=1, name="highway", value="bus_stop")
		)
		connection.close()
		meta.session.expunge_all()

	def tearDown(self):
		connection = meta.engine.connect()
		connection.execute("TRUNCATE TABLE Tags")
		connection.execute("TRUNCATE TABLE Stops")
		connection.close()
		meta.session.expunge_all()
	
	def test_outdated(self):
		"""Test that an outdated planet database is not updated"""

		timestamp = datetime.utcnow().replace(microsecond=0) - timedelta(days=7)
		model.planet_timestamp.set(timestamp)
		
		ret = self.env.run("paster", "auto-update-planet", "file:planet-server/", "minutely", config['__file__'], expect_error=True)
		
		assert ret.returncode == 1
		assert model.planet_timestamp.get() == timestamp
		assert table_contents(model.stops, [(1, Decimal("52.3"), Decimal("-1.9"), 123, 2)])
		assert table_contents(model.tags, [(1, "highway", "bus_stop")])

	def test_daily_import(self):
		"""Test that an import with daily granularity works"""

		timestamp = datetime.combine(date.today(), time(12, 13, 0)) - timedelta(days=2)
		model.planet_timestamp.set(timestamp)

		start_time = timestamp.replace(hour=0, minute=0, second=0)
		end_time = start_time + timedelta(days=1)
		filename = "planet-server/daily/%s-%s.osc" % (start_time.strftime("%Y%m%d"), end_time.strftime("%Y%m%d"))
		self.env.writefile(filename,
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="101" version="1" timestamp="" lat="52.6" lon="-3.3">
				     <tag k="highway" v="bus_stop"/>
				   </node>
			     </create>
		      </osmChange>
			""")
		self.env.run("gzip", filename)

		start_time = end_time
		end_time = start_time + timedelta(days=1)
		filename = "planet-server/daily/%s-%s.osc" % (start_time.strftime("%Y%m%d"), end_time.strftime("%Y%m%d"))
		self.env.writefile(filename,
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="102" version="1" timestamp="" lat="52.6" lon="-3.3">
				     <tag k="highway" v="bus_stop"/>
				   </node>
			     </create>
		      </osmChange>
			""")
		self.env.run("gzip", filename)

		ret = self.env.run("paster", "auto-update-planet", "file:planet-server/", "daily", config['__file__'])

		assert model.planet_timestamp.get() == end_time
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 123, 2),
			(2, Decimal("52.6"), Decimal("-3.3"), 101, 1),
			(3, Decimal("52.6"), Decimal("-3.3"), 102, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "highway", "bus_stop")
		])

	def test_hourly_import(self):
		"""Test that an import with hourly granularity works"""

		timestamp = datetime.utcnow().replace(minute=20, second=10, microsecond=0)  - timedelta(hours=2)
		model.planet_timestamp.set(timestamp)

		start_time = timestamp.replace(minute=0, second=0)
		end_time = start_time + timedelta(hours=1)
		filename = "planet-server/hourly/%s-%s.osc" % (start_time.strftime("%Y%m%d%H"), end_time.strftime("%Y%m%d%H"))
		self.env.writefile(filename,
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="101" version="1" timestamp="" lat="52.6" lon="-3.3">
				     <tag k="highway" v="bus_stop"/>
				   </node>
			     </create>
		      </osmChange>
			""")
		self.env.run("gzip", filename)

		start_time = end_time
		end_time = start_time + timedelta(hours=1)
		filename = "planet-server/hourly/%s-%s.osc" % (start_time.strftime("%Y%m%d%H"), end_time.strftime("%Y%m%d%H"))
		self.env.writefile(filename,
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="102" version="1" timestamp="" lat="52.6" lon="-3.3">
				     <tag k="highway" v="bus_stop"/>
				   </node>
			     </create>
		      </osmChange>
			""")
		self.env.run("gzip", filename)

		ret = self.env.run("paster", "auto-update-planet", "file:planet-server/", "hourly", config['__file__'])

		assert model.planet_timestamp.get() == end_time
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 123, 2),
			(2, Decimal("52.6"), Decimal("-3.3"), 101, 1),
			(3, Decimal("52.6"), Decimal("-3.3"), 102, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "highway", "bus_stop")
		])

	def test_minutely_import(self):
		"""Test that an import with minutely granularity works"""

		timestamp = datetime.utcnow().replace(second=10, microsecond=0)  - timedelta(minutes=2)
		model.planet_timestamp.set(timestamp)

		start_time = timestamp.replace(second=0)
		end_time = start_time + timedelta(minutes=1)
		filename = "planet-server/minute/%s-%s.osc" % (start_time.strftime("%Y%m%d%H%M"), end_time.strftime("%Y%m%d%H%M"))
		self.env.writefile(filename,
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="101" version="1" timestamp="" lat="52.6" lon="-3.3">
				     <tag k="highway" v="bus_stop"/>
				   </node>
			     </create>
		      </osmChange>
			""")
		self.env.run("gzip", filename)

		start_time = end_time
		end_time = start_time + timedelta(minutes=1)
		filename = "planet-server/minute/%s-%s.osc" % (start_time.strftime("%Y%m%d%H%M"), end_time.strftime("%Y%m%d%H%M"))
		self.env.writefile(filename,
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="102" version="1" timestamp="" lat="52.6" lon="-3.3">
				     <tag k="highway" v="bus_stop"/>
				   </node>
			     </create>
		      </osmChange>
			""")
		self.env.run("gzip", filename)

		ret = self.env.run("paster", "auto-update-planet", "file:planet-server/", "minutely", config['__file__'])

		assert model.planet_timestamp.get() == end_time
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 123, 2),
			(2, Decimal("52.6"), Decimal("-3.3"), 101, 1),
			(3, Decimal("52.6"), Decimal("-3.3"), 102, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "highway", "bus_stop")
		])
