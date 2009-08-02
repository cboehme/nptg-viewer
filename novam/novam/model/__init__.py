"""The application's model objects"""
import os
from uuid import uuid4
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm.collections import column_mapped_collection
import sqlalchemy.sql.expression as sql

from novam.model import meta


def init_model(engine, planet_timestamp_file):
	"""Call me before using any of the tables or classes in the model"""

	global localities, tags

	localities = sa.Table("Localities", meta.metadata, autoload=True, autoload_with=engine)
	tags = sa.Table("Tags", meta.metadata, autoload=True, autoload_with=engine)

	# This alias makes it easier to define the *_count columns:
	neighbours = localities.alias("neighbours")

	# To distinguish if a locality is from OSM or from the NPTG dataset the sign of the
	# osm_id is used. Since NPTG nodes are not in the OSM dataset they have negative
	# ids while OSM uses positive ids.

	orm.mapper(Locality, localities, properties={
		"tags": orm.relation(Tag, collection_class=column_mapped_collection(tags.c.name), \
				lazy=False, passive_deletes=True),
		"duplicate_count": orm.column_property(sql.select(
			[sql.func.count(neighbours.c.id)],
			sql.and_(
				localities.c.hidden == None,
				neighbours.c.hidden == None,
				sql.func.sign(localities.c.osm_id) == sql.func.sign(neighbours.c.osm_id),
				localities.c.osm_id != neighbours.c.osm_id,
				localities.c.name == neighbours.c.name,
				sql.func.sqrt(
					sql.func.pow(localities.c.lat - neighbours.c.lat, 2) +
					sql.func.pow(localities.c.lon - neighbours.c.lon, 2)
				) < 0.1
			),
		).label("duplicate_count")),
		"match_count": orm.column_property(sql.select(
			[sql.func.count(neighbours.c.id)],
			sql.and_(
				localities.c.hidden == None,
				neighbours.c.hidden == None,
				sql.func.sign(localities.c.osm_id) != sql.func.sign(neighbours.c.osm_id),
				localities.c.name == neighbours.c.name,
				sql.func.sqrt(
					sql.func.pow(localities.c.lat - neighbours.c.lat, 2) +
					sql.func.pow(localities.c.lon - neighbours.c.lon, 2)
				) < 0.1
			),
		).label("match_count"))
	})
	orm.mapper(Tag, tags)

	meta.session.configure(bind=engine)
	meta.engine = engine

	meta.planet_timestamp = planet_timestamp_file
	global planet_timestamp
	planet_timestamp = _TimestampFile(meta.planet_timestamp)

localities = None

class Locality(object):
	def __init__(self, lat, lon, osm_id=None, osm_version=None, name=None, hidden=None, comment=None):
			self.lat = lat
			self.lon = lon
			self.osm_id = osm_id
			self.osm_version = osm_version
			self.name = name
			self.hidden = hidden
			self.comment = comment

	def __repr__(self):
		return "Locality(id=%s, lat=%s, lon=%s, osm_id=%s)" % (self.id, self.lat, self.lon, self.osm_id)

tags = None

class Tag(object):
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __repr__(self):
		return "Tag(locality_id=%s, name=%s, value=%s)" % (self.locality_id, self.name, self.value)

# Wrapper around the planet timestamp file:
class _TimestampFile:

	FORMAT = "%Y-%m-%dT%H:%M:%SZ"

	def __init__(self, file):
		self.__file = file
	
	def get(self):
		fh = open(self.__file, "rb")
		ts = datetime.strptime(fh.read(20), self.FORMAT)
		fh.close()
		return ts

	def set(self, timestamp):
		fh = open(self.__file, "wb")
		fh.write(timestamp.strftime(self.FORMAT))
		fh.close()

