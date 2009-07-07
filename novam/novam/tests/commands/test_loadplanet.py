from decimal import Decimal
from unittest import TestCase
from scripttest import TestFileEnvironment
from pylons import config

from novam.tests import table_contents, table_is_empty
from novam.model import meta
from novam import model

class TestLoadPlanetCommand(TestCase):

	def __init__(self, *args, **kwargs):
		self.env = TestFileEnvironment("./test-output")
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

	def tearDown(self):
		connection = meta.engine.connect()
		connection.execute("TRUNCATE TABLE Tags")
		connection.execute("TRUNCATE TABLE Stops")
		connection.close()

	def test_standard_import(self):
		"""Test that only nodes either tagged as highway=bus stop_or having a
		   naptan:AtcoCode tag are imported."""

		self.env.writefile("test_standard_import.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osm version='0.6' generator='JOSM'>
				 <node id='1' version='1' lat='52.2551' lon='-1.9660'>
				   <tag k='name' v='I am a node' />
				 </node>
				 <node id='3' version='1' lat='52.0440' lon='-2.3962'>
				  <tag k='naptan:AtcoCode' v='1002' />
				  <tag k='shelter' v='yes' />
				 </node>
				 <node id='4' version='1' lat='52.2934' lon='-2.3571'>
				   <tag k='highway' v='bus_stop' />
				 </node>
			   </osm>
			""")
		self.env.run("paster", "load-planet", "test_standard_import.osm", config['__file__'])
		
		# FIXME: The order of the inserts does not actually matter. So we should not
		# check the value of the id field:
		assert table_contents(model.stops, [
			(2, Decimal("52.0440"), Decimal("-2.3962"), 3, 1),
			(3, Decimal("52.2934"), Decimal("-2.3571"), 4, 1) 
		])
		assert table_contents(model.tags, [
			(2, "naptan:AtcoCode", "1002"),
			(2, "shelter", "yes"),
			(3, "highway", "bus_stop")
		])

	def test_no_node_import(self):
		"""Test that no weird things happen if the input file contains 
		   no nodes."""

		self.env.writefile("test_no_node_import.osm", \
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osm version='0.6' generator='JOSM' />
			""")
		self.env.run("paster", "load-planet", "test_no_node_import.osm", config['__file__'])

		assert table_is_empty(model.stops)
		assert table_is_empty(model.tags)
		
	def test_empty_import(self):
		"""Test that a completely empty input file fails without doing damage
		   to the database."""

		self.env.writefile("test_empty_import.osm", "")
		result = self.env.run("paster", "load-planet", "test_empty_import.osm", config['__file__'], expect_error=True)

		assert result.returncode == 1, "Returncode should be 1"

		assert table_contents(model.stops, [(1, Decimal("52.3"), Decimal("-1.9"), 123, 2)])
		assert table_contents(model.tags, [(1, "highway", "bus_stop")])
