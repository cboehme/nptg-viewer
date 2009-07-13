from decimal import Decimal
from xml.sax import parseString, SAXParseException
from nose import with_setup

from novam.tests import table_contents, table_is_empty
from novam.model import meta
from novam import model
from novam.lib.planet_osm import Updater

def setup_function():
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

def teardown_function():
	connection = meta.engine.connect()
	connection.execute("TRUNCATE TABLE Tags")
	connection.execute("TRUNCATE TABLE Stops")
	connection.close()
	meta.session.expunge_all()

@with_setup(setup_function, teardown_function)
def test_create_stop_inside():
	"""Test that only nodes within Britain are added"""

	updater = Updater()
	parseString(
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
		""", updater, updater)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_create_bus_stops_only():
	"""Test that only nodes tagged as highway=bus_stop or having naptan:AtcoCode
	   are added"""

	updater = Updater()
	parseString(
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
		""", updater, updater)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_dont_create_old_nodes():
	"""Verify that existing nodes are not overwritten"""

	updater = Updater()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osmChange version="0.6" generator="osmosis">
			 <create>
			   <node id="101" version="1" timestamp="" lat="52.3" lon="-1.8">
				 <tag k="highway" v="bus_stop"/>
			   </node>
			 </create>
		  </osmChange>
		""", updater, updater)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_delete_bus_stops():
	"""Test that nodes are deleted"""

	updater = Updater()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osmChange version="0.6" generator="osmosis">
			 <delete>
			   <node id="102" version="4" timestamp="" lat="53.2" lon="0.1" />
			 </delete>
		  </osmChange>
		""", updater, updater)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_delete_only_matching_stops():
	"""Verify that stops are only deleted if version+1 and id match"""

	updater = Updater()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osmChange version="0.6" generator="osmosis">
			 <delete>
			   <node id="101" version="2" timestamp="" lat="52.3" lon="-1.9" />
			 </delete>
		  </osmChange>
		""", updater, updater)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_modify_stop():
	"""Test a normal modify operation with tag, lan/lot changes"""

	updater = Updater()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osmChange version="0.6" generator="osmosis">
			 <modify>
			   <node id="102" version="4" timestamp="" lat="51.2" lon="0.5">
				 <tag k="highway" v="bus_stop"/>
				 <tag k="naptan:AtcoCode" v="54321"/>
			   </node>
			 </modify>
		  </osmChange>
		""", updater, updater)
	meta.session.commit()

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

@with_setup(setup_function, teardown_function)
def test_modify_stop_old_version():
	"""Test that an old version does not overwrite a new one"""

	updater = Updater()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osmChange version="0.6" generator="osmosis">
			 <modify>
			   <node id="102" version="2" timestamp="" lat="51.2" lon="0.5">
				 <tag k="highway" v="bus_stop"/>
				 <tag k="naptan:AtcoCode" v="54321"/>
			   </node>
			 </modify>
		  </osmChange>
		""", updater, updater)
	meta.session.commit()

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

@with_setup(setup_function, teardown_function)
def test_modify_stop_tags_removed():
	"""Verify that a stop will be removed if it does not contain bus stops tags anymore"""

	updater = Updater()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osmChange version="0.6" generator="osmosis">
			 <modify>
			   <node id="102" version="4" timestamp="" lat="51.2" lon="0.5">
				 <tag k="highway" v="not a bus stop"/>
			   </node>
			 </modify>
		  </osmChange>
		""", updater, updater)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_modify_stop_tags_add():
	"""Verify that a stop will be added if it contains bus stop tags"""

	updater = Updater()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osmChange version="0.6" generator="osmosis">
			 <modify>
			   <node id="104" version="2" timestamp="" lat="51.2" lon="0.5">
				 <tag k="highway" v="bus_stop"/>
			   </node>
			 </modify>
		  </osmChange>
		""", updater, updater)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_modify_stop_inside():
	"""Verify that a stop will be added if it is inside Britain"""

	updater = Updater()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osmChange version="0.6" generator="osmosis">
			 <modify>
			   <node id="104" version="2" timestamp="" lat="51.2" lon="0.5">
				 <tag k="naptan:AtcoCode" v="54321"/>
			   </node>
			 </modify>
		  </osmChange>
		""", updater, updater)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_modify_stop_outside():
	"""Test that a stop will not be added if it is not inside Britain anymore"""

	updater = Updater()
	parseString(
		"""<?xml version='1.0' encoding='UTF-8'?>
		   <osmChange version="0.6" generator="osmosis">
			 <modify>
			   <node id="102" version="4" timestamp="" lat="60.2" lon="5.0">
				 <tag k="highway" v="bus_stop"/>
				 <tag k="naptan:AtcoCode" v="54321"/>
			   </node>
			 </modify>
		  </osmChange>
		""", updater, updater)
	meta.session.commit()
	
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

@with_setup(setup_function, teardown_function)
def test_broken_file():
	"""Test that a broken input file does not lead to a corrupted database"""

	exception = False
	try:
		updater = Updater()
		parseString(
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
				 <modify>
				   <node id="102" version="4" timestamp="" lat="60.2" lon="5.0">
					 <tag k="highway" v="bus_stop"/>
					 <tag k="naptan:AtcoCode" v="54321"/>
				   </node>
			  </osmChange>
			""", updater, updater)
	except SAXParseException:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
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

@with_setup(setup_function, teardown_function)
def test_invalid_file():
	"""Test that an invalid input file does not lead to a corrupted database"""

	exception = False
	try:
		updater = Updater()
		parseString(
			"""<?xml version='1.0' encoding='UTF-8'?>
			   <osmChange version="0.6" generator="osmosis">
				 <modify>
				   <node id="102" version="4" timestamp="" lat="ERROR" lon="5.0">
					 <tag k="highway" v="bus_stop"/>
					 <tag k="naptan:AtcoCode" v="54321"/>
				   </node>
				 </modify>
			  </osmChange>
			""", updater, updater)
	except ValueError:
		exception = True
	meta.session.commit()

	assert exception, "The import should have failed with an exception"
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
