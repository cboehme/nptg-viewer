from decimal import Decimal
from datetime import datetime
from xml.sax import SAXParseException
from scripttest import TestFileEnvironment
from nose import with_setup

from novam.tests import table_contents, table_is_empty
from novam.model import meta
from novam import model
import novam.lib.planet_osm as planet

_initial_timestamp = datetime(2001, 3, 5, 10, 13, 30)
_new_timestamp = datetime(2002, 2, 20, 4, 5, 23)

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

	model.planet_timestamp.set(_initial_timestamp)

def teardown_function():
	connection = meta.engine.connect()
	connection.execute("TRUNCATE TABLE Tags")
	connection.execute("TRUNCATE TABLE Stops")
	connection.close()
	meta.session.expunge_all()

@with_setup(setup_function, teardown_function)
def test_uncompressed_import():
	"""Load a local uncompressed file"""

	env = TestFileEnvironment("./test_output")
	env.writefile("test_uncompressed_import.osm", \
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
	
	planet.load("file:./test_output/test_uncompressed_import.osm", _new_timestamp, planet.Importer())
	meta.session.commit()
	
	# FIXME: The order of the inserts does not actually matter. So we should not
	# check the value of the id field:
	assert model.planet_timestamp.get() == _new_timestamp
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
def test_gzip_import():
	"""Load a local gzip file"""

	env = TestFileEnvironment("./test_output")
	env.writefile("test_gzip_import.osm", \
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
	env.run("gzip", "test_gzip_import.osm")

	planet.load("file:./test_output/test_gzip_import.osm.gz", _new_timestamp, planet.Importer())
	meta.session.commit()
	
	# FIXME: The order of the inserts does not actually matter. So we should not
	# check the value of the id field:
	assert model.planet_timestamp.get() == _new_timestamp
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
def test_bzip2_import():
	"""Load a local bzip2 file"""

	env = TestFileEnvironment("./test_output")
	env.writefile("test_bzip2_import.osm", \
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
	env.run("bzip2", "test_bzip2_import.osm")

	planet.load("file:./test_output/test_bzip2_import.osm.bz2", _new_timestamp, planet.Importer())
	meta.session.commit()
	
	# FIXME: The order of the inserts does not actually matter. So we should not
	# check the value of the id field:
	assert model.planet_timestamp.get() == _new_timestamp
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
def test_non_existing_file():
	"""Try loading a non existing file"""

	exception = False
	try:
		planet.load("file:./test_output/test_non_existing_file.osm", _new_timestamp, planet.Importer())
	except:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
	assert model.planet_timestamp.get() == _initial_timestamp
	assert table_contents(model.stops, [(1, Decimal("52.3"), Decimal("-1.9"), 123, 2)])
	assert table_contents(model.tags, [(1, "highway", "bus_stop")])

@with_setup(setup_function, teardown_function)
def test_broken_gzip_import():
	"""Load a broken local gzip file"""

	env = TestFileEnvironment("./test_output")
	env.writefile("test_broken_gzip_import.osm", \
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
	   </osm>
	""")
	env.run("gzip", "test_broken_gzip_import.osm")

	exception = False
	try:
		planet.load("file:./test_output/test_broken_gzip_import.osm.gz", _new_timestamp, planet.Importer())
	except:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
	assert model.planet_timestamp.get() == _initial_timestamp
	assert table_contents(model.stops, [(1, Decimal("52.3"), Decimal("-1.9"), 123, 2)])
	assert table_contents(model.tags, [(1, "highway", "bus_stop")])

@with_setup(setup_function, teardown_function)
def test_uncompressed_url():
	"""Load an uncompressed url"""

	planet.load("http://mmercia.quirm.de/novam-tests/test_uncompressed_url.osm", _new_timestamp, planet.Importer())
	meta.session.commit()
	
	# FIXME: The order of the inserts does not actually matter. So we should not
	# check the value of the id field:
	assert model.planet_timestamp.get() == _new_timestamp
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
def test_gzip_url():
	"""Load a gzip url"""

	planet.load("http://mmercia.quirm.de/novam-tests/test_gzip_url.osm.gz", _new_timestamp, planet.Importer())
	meta.session.commit()
	
	# FIXME: The order of the inserts does not actually matter. So we should not
	# check the value of the id field:
	assert model.planet_timestamp.get() == _new_timestamp
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
def test_bzip2_url():
	"""Load a bzip2 url"""

	planet.load("http://mmercia.quirm.de/novam-tests/test_bzip2_url.osm.bz2", _new_timestamp, planet.Importer())
	meta.session.commit()
	
	# FIXME: The order of the inserts does not actually matter. So we should not
	# check the value of the id field:
	assert model.planet_timestamp.get() == _new_timestamp
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
def test_broken_gzip_url():
	"""Load a gzip url"""

	exception = False
	try:
		planet.load("http://mmercia.quirm.de/novam-tests/test_broken_gzip_url.osm.gz", _new_timestamp, planet.Importer())
	except:
		exception = True
	meta.session.commit()
	
	assert exception, "The import should have failed with an exception"
	assert model.planet_timestamp.get() == _initial_timestamp
	assert table_contents(model.stops, [(1, Decimal("52.3"), Decimal("-1.9"), 123, 2)])
	assert table_contents(model.tags, [(1, "highway", "bus_stop")])

@with_setup(setup_function, teardown_function)
def test_non_existing_url():
	"""Try loading a non existing url"""

	exception = False
	try:
		planet.load("http://mmercia.quirm.de/novam-tests/non-existing.osm", _new_timestamp, planet.Importer())
	except:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
	assert model.planet_timestamp.get() == _initial_timestamp
	assert table_contents(model.stops, [(1, Decimal("52.3"), Decimal("-1.9"), 123, 2)])
	assert table_contents(model.tags, [(1, "highway", "bus_stop")])
