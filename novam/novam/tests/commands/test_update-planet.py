from decimal import Decimal
from datetime import datetime
from unittest import TestCase
from scripttest import TestFileEnvironment
from pylons import config

from novam.tests import table_contents
from novam.model import meta
from novam import model

_initial_timestamp = datetime(2001, 3, 5, 10, 13, 30)
_new_timestamp = datetime(2002, 2, 20, 4, 5, 23)

class TestUpdatePlanetCommand(TestCase):

	def __init__(self, *args, **kwargs):
		self.env = TestFileEnvironment("./test_output")
		TestCase.__init__(self, *args, **kwargs)

	def setUp(self):
		connection = meta.engine.connect()
		connection.execute("TRUNCATE TABLE Tags")    # Use truncate to reset auto-increment
		connection.execute("TRUNCATE TABLE Stops")
		connection.execute(
			model.stops.insert().values(id=1, lat=Decimal("52.3"), lon=Decimal("-1.9"), osm_id=101, osm_version=2)
		)
		connection.execute(
			model.stops.insert().values(id=2, lat=Decimal("51.3"), lon=Decimal("0.4"), osm_id=102, osm_version=3)
		)
		connection.execute(
			model.stops.insert().values(id=3, lat=Decimal("53.2"), lon=Decimal("0.1"), osm_id=103, osm_version=1)
		)
		connection.execute(
			model.tags.insert().values(stop_id=1, name="highway", value="bus_stop")
		)
		connection.execute(
			model.tags.insert().values(stop_id=2, name="highway", value="bus_stop")
		)
		connection.execute(
			model.tags.insert().values(stop_id=3, name="naptan:AtcoCode", value="12345")
		)
		connection.close()
		meta.session.expunge_all()

		model.planet_timestamp.set(_initial_timestamp)

	def tearDown(self):
		connection = meta.engine.connect()
		connection.execute("TRUNCATE TABLE Tags")
		connection.execute("TRUNCATE TABLE Stops")
		connection.close()
		meta.session.expunge_all()

	def test_successful_command(self):
		"""Test that update-planet works"""

		self.env.writefile("test_successful_command.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="104" version="1" timestamp="" lat="52.6" lon="-3.3">
				     <tag k="highway" v="bus_stop"/>
				     <tag k="name" v="Stop AB"/>
				   </node>
				   <node id="105" version="1" timestamp="" lat="53.3" lon="-6.6">
				     <tag k="highway" v="bus_stop"/>
				   </node>
			     </create>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "file:test_successful_command.osm", 
			_new_timestamp.strftime(model.planet_timestamp.FORMAT), config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert model.planet_timestamp.get() == _new_timestamp
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(2, Decimal("51.3"), Decimal("0.4"), 102, 3),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1),
			(4, Decimal("52.6"), Decimal("-3.3"), 104, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345"),
			(4, "highway", "bus_stop"),
			(4, "name", "Stop AB")
		])

	def test_failing_command(self):
		"""Test that update-planet fails without breaking anything"""

		self.env.writefile("test_failing_command.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="104" version="1" timestamp="" lat="52.6" lon="-3.3">
				     <tag k="highway" v="bus_stop"/>
				     <tag k="name" v="Stop AB"/>
				   </node>
				   </node>
			     </create>
		      </osmChange>
			""")
		ret = self.env.run("paster", "update-planet", "file:test_failing_command.osm", 
			_new_timestamp.strftime(model.planet_timestamp.FORMAT), config['__file__'],
			expect_error=True)
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert ret.returncode == 1
		assert model.planet_timestamp.get() == _initial_timestamp
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(2, Decimal("51.3"), Decimal("0.4"), 102, 3),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1),
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345"),
		])
