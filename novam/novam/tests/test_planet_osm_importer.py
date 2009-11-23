from decimal import Decimal
from xml.sax import parseString, SAXParseException
from sqlalchemy.exc import IntegrityError 
from geoalchemy import *
from nose import with_setup

from novam.tests import table_contents, table_is_empty
from novam.model import meta
from novam import model
from novam.lib.planet_osm import Importer

def setup_function():
	connection = meta.engine.connect()
	connection.execute("DELETE FROM Tags")
	connection.execute("DELETE FROM Localities")
	connection.execute("ALTER SEQUENCE localities_id_seq RESTART WITH 1")
	connection.execute(
		model.localities.insert().values(coords=WKTSpatialElement("POINT(-1.9 52.3)"), \
			osm_id=123, osm_version=2)
	)
	connection.execute(
		model.tags.insert().values(locality_id=1, name="place", value="village")
	)
	connection.close()
	meta.session.expunge_all()

def teardown_function():
	connection = meta.engine.connect()
	connection.execute("DELETE FROM Tags")
	connection.execute("DELETE FROM Localities")
	connection.execute("ALTER SEQUENCE localities_id_seq RESTART WITH 1")
	connection.close()
	meta.session.expunge_all()

@with_setup(setup_function, teardown_function)
def test_standard_import():
	"""Test that only nodes either having a place or a NptgLocalityCode
	   tag are imported."""


	importer = Importer()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osm version='0.6' generator='JOSM'>
			 <node id='1' version='1' lat='52.2551' lon='-1.9660'>
			   <tag k='name' v='I am a node' />
			 </node>
			 <node id='3' version='1' lat='52.0440' lon='-2.3962'>
			  <tag k='NptgLocalityCode' v='1002' />
			  <tag k='othertag' v='is there' />
			   <tag k='name' v='NPTGLocality' />
			 </node>
			 <node id='4' version='1' lat='52.2934' lon='-2.3571'>
			   <tag k='place' v='village' />
			   <tag k='name' v='OSMLocality' />
			 </node>
		   </osm>
		""", importer, importer)
	meta.session.commit()

	# FIXME: The order of the inserts does not actually matter. So we should not
	# check the value of the id field:
	assert table_contents(model.localities, [
		(2, 3, 1, "NPTGLocality", None, None, WKTSpatialElement("POINT(-2.3962 52.0440)")),
		(3, 4, 1, "OSMLocality", None, None, WKTSpatialElement("POINT(-2.3571 52.2934)")) 
	])
	assert table_contents(model.tags, [
		(2, "NptgLocalityCode", "1002"),
		(2, "othertag", "is there"),
		(2, "name", "NPTGLocality"),
		(3, "place", "village"),
		(3, "name", "OSMLocality")
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

	assert table_is_empty(model.localities)
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
	assert table_contents(model.localities, [(1, 123, 2, None, None, WKTSpatialElement("POINT(-1.9 52.3)"))])
	assert table_contents(model.tags, [(1, "place", "village")])
	
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
			       <tag k='NptgLocalityCode' v='1002' />
			       <tag k='name' v='yes' />
			     </node>
			     <node id='4' version='1' lat='52.2934' lon='-2.3571'>
			   </osm>
			""", importer, importer)
	except SAXParseException:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
	assert table_contents(model.localities, [(1, 123, 2, None, None, WKTSpatialElement("POINT(-1.9 52.3)"))])
	assert table_contents(model.tags, [(1, "place", "village")])
	
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
			       <tag k='NptgLocalityCode' v='1002' />
			       <tag k='name' v='yes' />
			     </node>
			     <node id='4' version='1' lat='52.2934' lon='-2.3571'>
				   <tag k='place' v='village' />
				 </node>
			     <node id='4' version='1' lat='52.2934' lon='-2.3571'>
				   <tag k='place' v='city' />
				 </node>
			   </osm>
			""", importer, importer)
	except IntegrityError:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
	assert table_contents(model.localities, [(1, 123, 2, None, None, WKTSpatialElement("POINT(-1.9 52.3)"))])
	assert table_contents(model.tags, [(1, "place", "village")])

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
			       <tag k='NptgLocalityCode' v='1002' />
			       <tag k='name' v='yes' />
			     </node>
			     <node id='4' version='1' lat='52.2934' lon='-2.3571'>
				   <tag k='place' v='village' />
				 </node>
			     <node id='4' version='1' lat='52.2934' lon='-2.3571'>
				   <tag k='place' v='village' />
				 </node>
			   </osm>
			""", importer, importer)
	except IntegrityError:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
	assert table_contents(model.localities, [(1, 123, 2, None, None, WKTSpatialElement("POINT(-1.9 52.3)"))])
	assert table_contents(model.tags, [(1, "place", "village")])


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
			  <tag k='NptgLocalityCode' v='1002' />
			  <tag k='name' v='NPTGLoc' />
			 </node>
			 <node id='4' version='1' lat='52.2934' lon='-2.3571'>
			   <tag k='place' v='village'>
			   <tag k='name' v='OSMLoc1' />
			     <unexpected-tag>Blabla</unexpected-tag>
			   </tag>
			 </node>
			 <unexpected-tag>
			   <node id='9' version='2' lat='52.23' lon='-2.3'>
			     <tag k='place' v='city' />
			     <tag k='name' v='OSMLoc2' />
			   </node>	
			 </unexpected-tag>
		   </osm>
		""", importer, importer)
	meta.session.commit()
	
	# FIXME: The order of the inserts does not actually matter. So we should not
	# check the value of the id field:
	assert table_contents(model.localities, [
		(2, 3, 1, "NPTGLoc", None, None, WKTSpatialElement("POINT(-2.3962 52.0440)")),
		(3, 4, 1, None, None, None, WKTSpatialElement("POINT(-2.3571 52.2934)")) 
	])
	assert table_contents(model.tags, [
		(2, "NptgLocalityCode", "1002"),
		(2, "name", "NPTGLoc"),
		(3, "place", "village")
	])

