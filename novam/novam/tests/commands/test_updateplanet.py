from decimal import Decimal
from unittest import TestCase
from scripttest import TestFileEnvironment
from pylons import config

from novam.tests import table_contents, table_is_empty
from novam.model import meta
from novam import model

class TestUpdatePlanetCommand(TestCase):

	def __init__(self, *args, **kwargs):
		self.env = TestFileEnvironment("./test-output")
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

	def tearDown(self):
		connection = meta.engine.connect()
		connection.execute("TRUNCATE TABLE Tags")
		connection.execute("TRUNCATE TABLE Stops")
		connection.close()

	def test_create_stop_inside(self):
		"""Test that only nodes within Britain are added"""

		self.env.writefile("test_create_nodes_inside.osm", \
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
		self.env.run("paster", "update-planet", "test_create_nodes_inside.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
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

	def test_create_bus_stops_only(self):
		"""Test that only nodes tagged as highway=bus_stop or having naptan:AtcoCode
		   are added"""

		self.env.writefile("test_create_bus_stops_only.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="104" version="1" timestamp="" lat="52.6" lon="-3.3">
				     <tag k="naptan:AtcoCode" v="54321"/>
				   </node>
				   <node id="105" version="1" timestamp="" lat="52.1" lon="0.1" />
				   <node id="106" version="1" timestamp="" lat="53.3" lon="0.6">
				     <tag k="highway" v="bus_stop"/>
				   </node>
				   <node id="107" version="1" timestamp="" lat="52.1" lon="0.6">
				     <tab k="name" v="not a busstop"/>
				   </node>
			     </create>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_create_bus_stops_only.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(2, Decimal("51.3"), Decimal("0.4"), 102, 3),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1),
			(4, Decimal("52.6"), Decimal("-3.3"), 104, 1),
			(5, Decimal("53.3"), Decimal("0.6"), 106, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345"),
			(4, "naptan:AtcoCode", "54321"),
			(5, "highway", "bus_stop")
		])

	def test_dont_create_old_nodes(self):
		"""Verify that existing nodes are not overwritten"""

		self.env.writefile("test_dont_create_old_nodes.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <create>
				   <node id="101" version="1" timestamp="" lat="52.3" lon="-1.8">
				     <tag k="highway" v="bus_stop"/>
				   </node>
			     </create>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_dont_create_old_nodes.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(2, Decimal("51.3"), Decimal("0.4"), 102, 3),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345")

		])

	def test_delete_bus_stops(self):
		"""Test that nodes are deleted"""

		self.env.writefile("test_delete_bus_stops.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <delete>
				   <node id="102" version="3" timestamp="" lat="53.2" lon="0.1" />
			     </delete>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_delete_bus_stops.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345")
		])

	def test_delete_only_matching_stops(self):
		"""Verify that stops are only deleted if version and id match"""

		self.env.writefile("test_delete_only_matching_stops.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <delete>
				   <node id="101" version="3" timestamp="" lat="52.3" lon="-1.9" />
			     </delete>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_delete_only_matching_stops.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(2, Decimal("51.3"), Decimal("0.4"), 102, 3),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345")

		])

	def test_modify_stop(self):
		"""Test a normal modify operation with tag, lan/lot changes"""

		self.env.writefile("test_modify_stop.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <modify>
				   <node id="102" version="4" timestamp="" lat="51.2" lon="0.5">
				     <tag k="highway" v="bus_stop"/>
				     <tag k="naptan:AtcoCode" v="54321"/>
				   </node>
			     </modify>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_modify_stop.osm", config['__file__'])

		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1),
			(4, Decimal("51.2"), Decimal("0.5"), 102, 4)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345"),
			(4, "highway", "bus_stop"),
			(4, "naptan:AtcoCode", "54321")
		])

	def test_modify_stop_old_version(self):
		"""Test that an old version does not overwrite a new one"""

		self.env.writefile("test_modify_stop_old_version.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <modify>
				   <node id="102" version="2" timestamp="" lat="51.2" lon="0.5">
				     <tag k="highway" v="bus_stop"/>
				     <tag k="naptan:AtcoCode" v="54321"/>
				   </node>
			     </modify>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_modify_stop_old_version.osm", config['__file__'])

		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(2, Decimal("51.3"), Decimal("0.4"), 102, 3),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345")
		])
	
	def test_modify_stop_tags_removed(self):
		"""Verify that a stop will be removed if it does not contain bus stops tags anymore"""

		self.env.writefile("test_modify_stop_tags_removed.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <modify>
				   <node id="102" version="4" timestamp="" lat="51.2" lon="0.5">
				     <tag k="highway" v="not a bus stop"/>
				   </node>
			     </modify>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_modify_stop_tags_removed.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345")

		])

	def test_modify_stop_tags_add(self):
		"""Verify that a stop will be added if it contains bus stop tags"""

		self.env.writefile("test_modify_stop_tags_add.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <modify>
				   <node id="104" version="2" timestamp="" lat="51.2" lon="0.5">
				     <tag k="highway" v="bus_stop"/>
				   </node>
			     </modify>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_modify_stop_tags_add.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(2, Decimal("51.3"), Decimal("0.4"), 102, 3),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1),
			(4, Decimal("51.2"), Decimal("0.5"), 104, 2)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345"),
			(4, "highway", "bus_stop")
		])

	def test_modify_stop_inside(self):
		"""Verify that a stop will be added if it is inside Britain"""

		self.env.writefile("test_modify_stop_inside.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <modify>
				   <node id="104" version="2" timestamp="" lat="51.2" lon="0.5">
				     <tag k="naptan:AtcoCode" v="54321"/>
				   </node>
			     </modify>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_modify_stop_inside.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(2, Decimal("51.3"), Decimal("0.4"), 102, 3),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1),
			(4, Decimal("51.2"), Decimal("0.5"), 104, 2)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(2, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345"),
			(4, "naptan:AtcoCode", "54321")
		])

	def test_modify_stop_outside(self):
		"""Test that a stop will not be added if it is not inside Britain anymore"""

		self.env.writefile("test_modify_stop_outside.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
			     <modify>
				   <node id="102" version="4" timestamp="" lat="60.2" lon="5.0">
				     <tag k="highway" v="bus_stop"/>
				     <tag k="naptan:AtcoCode" v="54321"/>
				   </node>
			     </modify>
		      </osmChange>
			""")
		self.env.run("paster", "update-planet", "test_modify_stop_outside.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(1, Decimal("52.3"), Decimal("-1.9"), 101, 2),
			(3, Decimal("53.2"), Decimal("0.1"), 103, 1)
		])
		assert table_contents(model.tags, [
			(1, "highway", "bus_stop"),
			(3, "naptan:AtcoCode", "12345")
		])
