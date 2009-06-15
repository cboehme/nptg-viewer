import os
from uuid import uuid4

from sqlalchemy import Table
from sqlalchemy import orm
from sqlalchemy.orm.collections import column_mapped_collection
import sqlalchemy.sql.expression as sql

from naptanmerger.model import meta


class Stop(object):
	def __init__(self, lat, lon, osm_id=None):
		self.lat = lat
		self.lon = lon
		self.osm_id = osm_id

	def __repr__(self):
		return "Stop(id=%s, lat=%s, lon=%s, osm_id=%s)" % (self.id, self.lat, self.lon, self.osm_id)

class Tag(object):
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __repr__(self):
		return "Tag(stop_id=%s, name=%s, value=%s)" % (self.stop_id, self.name, self.value)

class Waypoint(object):
	def __init__(self, lat, lon, name=None):
		self.lat = lat
		self.lon = lon
		self.name = name

	def __repr__(self):
		return "Waypoint(id=%s, lat=%s, lon=%s, name=%s)" % (self.id, self.lat, self.lon, self.name)

class Image(object):
	def __init__(self, lat=None, lon=None):
		self.lat = lat
		self.lon = lon
		self.file_id = unicode(uuid4())

	def _get_file_path(self):
		if not os.path.exists(meta.image_store):
			os.makedirs(meta.image_store)
		return os.path.join(meta.image_store, self.file_id)

	file_path = property(_get_file_path)

	def __repr__(self):
		return "Image(id=%s, lat=%s, lon=%s, file_id=%s)" % (self.id, self.lat, self.lon, self.file_id)

stops = None
tags = None
waypoints = None
images = None

def init_model(engine, image_store):
	"""Call me before using any of the tables or classes in the model."""

	meta.engine = engine

	session = orm.sessionmaker(bind=meta.engine, autoflush=True, transactional=True)
	meta.session = orm.scoped_session(session)

	meta.image_store = image_store

	global stops, tags, waypoints

	stops = Table("Stops", meta.metadata, autoload=True, autoload_with=engine)
	tags = Table("Tags", meta.metadata, autoload=True, autoload_with=engine)
	waypoints = Table("Waypoints", meta.metadata, autoload=True, autoload_with=engine)
	images = Table("Images", meta.metadata, autoload=True, autoload_with=engine)
	
	orm.mapper(Stop, stops, properties={
		"tags": orm.relation(Tag, collection_class=column_mapped_collection(tags.c.name), lazy=False, passive_deletes=True)
	})

	orm.mapper(Tag, tags)

	orm.mapper(Waypoint, waypoints)

	orm.mapper(Image, images)
