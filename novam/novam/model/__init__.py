"""The application's model objects"""
import os
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm.collections import column_mapped_collection

from novam.model import meta


def init_model(engine, image_store):
	"""Call me before using any of the tables or classes in the model"""
	## Reflected tables must be defined and mapped here
	#global reflected_table
	#reflected_table = sa.Table("Reflected", meta.metadata, autoload=True,
	#							autoload_with=engine)
	#orm.mapper(Reflected, reflected_table)

	global stops, tags, waypoints

	stops = sa.Table("Stops", meta.metadata, autoload=True, autoload_with=engine)
	tags = sa.Table("Tags", meta.metadata, autoload=True, autoload_with=engine)
	waypoints = sa.Table("Waypoints", meta.metadata, autoload=True, autoload_with=engine)
	images = sa.Table("Images", meta.metadata, autoload=True, autoload_with=engine)
	
	orm.mapper(Stop, stops, properties={
		"tags": orm.relation(Tag, collection_class=column_mapped_collection(tags.c.name), \
				lazy=False, passive_deletes=True)
	})
	orm.mapper(Tag, tags)
	orm.mapper(Waypoint, waypoints)
	orm.mapper(Image, images)

	meta.session.configure(bind=engine)
	meta.engine = engine

	meta.image_store = image_store


## Non-reflected tables may be defined and mapped at module level
#foo_table = sa.Table("Foo", meta.metadata,
#	 sa.Column("id", sa.types.Integer, primary_key=True),
#	 sa.Column("bar", sa.types.String(255), nullable=False),
#	 )
#
#class Foo(object):
#	 pass
#
#orm.mapper(Foo, foo_table)


## Classes for reflected tables may be defined here, but the table and
## mapping itself must be done in the init_model function
#reflected_table = None
#
#class Reflected(object):
#	 pass

stops = None

class Stop(object):
	def __init__(self, lat, lon, osm_id=None, osm_version=None):
			self.lat = lat
			self.lon = lon
			self.osm_id = osm_id
			self.osm_version = osm_version

	def __repr__(self):
		return "Stop(id=%s, lat=%s, lon=%s, osm_id=%s)" % (self.id, self.lat, self.lon, self.osm_id)

tags = None

class Tag(object):
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __repr__(self):
		return "Tag(stop_id=%s, name=%s, value=%s)" % (self.stop_id, self.name, self.value)

waypoints = None

class Waypoint(object):
	def __init__(self, lat, lon, name=None):
		self.lat = lat
		self.lon = lon
		self.name = name

	def __repr__(self):
		return "Waypoint(id=%s, lat=%s, lon=%s, name=%s)" % (self.id, self.lat, self.lon, self.name)

images = None

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
