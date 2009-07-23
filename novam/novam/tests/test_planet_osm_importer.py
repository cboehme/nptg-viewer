from decimal import Decimal
from xml.sax import parseString, SAXParseException
from sqlalchemy.exc import IntegrityError 
from nose import with_setup

from novam.tests import table_contents, table_is_empty
from novam.model import meta
from novam import model
from novam.lib.planet_osm import Importer

def setup_function():
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

def teardown_function():
	connection = meta.engine.connect()
	connection.execute("TRUNCATE TABLE Tags")
	connection.execute("TRUNCATE TABLE Stops")
	connection.close()
	meta.session.expunge_all()

@with_setup(setup_function, teardown_function)
def test_standard_import():
	"""Test that only nodes either tagged as highway=bus stop_or having a
	   naptan:AtcoCode tag are imported."""

	importer = Importer()
	parseString(
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
		""", importer, importer)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_no_node_import():
	"""Test that no weird things happen if the input file contains no nodes"""

	importer = Importer()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osm version='0.6' generator='JOSM' />
		""", importer, importer)
	meta.session.commit()

	assert table_is_empty(model.stops)
	assert table_is_empty(model.tags)
	
@with_setup(setup_function, teardown_function)
def test_empty_import():
	"""Test that a completely empty input file fails without doing damage to the database"""
	
	exception = False
	try:
		importer = Importer()
		parseString("", importer, importer)
	except SAXParseException:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
	assert table_contents(model.stops, [(1, Decimal("52.3"), Decimal("-1.9"), 123, 2)])
	assert table_contents(model.tags, [(1, "highway", "bus_stop")])
	
@with_setup(setup_function, teardown_function)
def test_broken_import():
	"""Test that a broken import file does not corrupt the database"""
	
	exception = False
	try:
		importer = Importer()
		parseString(
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
			   </osm>
			""", importer, importer)
	except SAXParseException:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
	assert table_contents(model.stops, [(1, Decimal("52.3"), Decimal("-1.9"), 123, 2)])
	assert table_contents(model.tags, [(1, "highway", "bus_stop")])
	
@with_setup(setup_function, teardown_function)
def test_invalid_import():
	"""Test that an invalid import file does not corrupt the database"""
	
	exception = False
	try:
		importer = Importer() 
		parseString(
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
			     <node id='4' version='1' lat='52.2934' lon='-2.3571'>
				   <tag k='highway' v='bus_stop' />
				 </node>
			   </osm>
			""", importer, importer)
	except IntegrityError:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
	assert table_contents(model.stops, [(1, Decimal("52.3"), Decimal("-1.9"), 123, 2)])
	assert table_contents(model.tags, [(1, "highway", "bus_stop")])


@with_setup(setup_function, teardown_function)
def test_unexpected_input():
	"""Test that unknown or unexpected parts of the xml input are ignored"""

	importer = Importer()
	parseString(
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
			   <tag k='highway' v='bus_stop'>
			     <unexpected-tag>Blabla</unexpected-tag>
			   </tag>
			 </node>
			 <unexpected-tag>
			   <node id='9' version='2' lat='52.23' lon='-2.3'>
			     <tag k='highway' v='bus_stop' />
			   </node>	
			 </unexpected-tag>
		   </osm>
		""", importer, importer)
	meta.session.commit()
	
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

