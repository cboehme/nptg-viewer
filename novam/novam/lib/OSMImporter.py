from xml.sax.handler import ContentHandler
import sqlalchemy.sql.expression as sql
import logging

from novam import model
from novam.model.meta import session
from novam.lib.point_in_polygon import point_in_polygon

log = logging.getLogger(__name__)

class OSMImporter(ContentHandler):
	def __init__(self):
		self.current_stop = None
		self.is_bus_stop = False

	def startElement(self, name, attrs):
		
		if name == "osm":
			session.execute(model.stops.delete())

		elif name == "node":
			self.current_stop = model.Stop(attrs.getValue("lat"), attrs.getValue("lon"), \
				attrs.getValue("id"), attrs.getValue("version"))
			session.begin_nested()
			session.add(self.current_stop)
			self.is_bus_stop = False

		elif self.current_stop and name == "tag":
			key, val = attrs.getValue("k"), attrs.getValue("v")
			self.current_stop.tags[key] = model.Tag(key, val)
			self.is_bus_stop = self.is_bus_stop or (key == "naptan:AtcoCode" or (key == "highway" and val == "bus_stop"))

	def endElement(self, name):
		if name == "osm":
			session.commit()

		if name == "node":
			if self.is_bus_stop:
				session.commit()
			else:
				session.rollback()
			self.current_stop = None


MODE_NONE = 0
MODE_CREATE = 1
MODE_MODIFY = 2
MODE_DELETE = 3

class OSMUpdater(ContentHandler):
	def __init__(self):
		# Outline of the UK. That should be in a config file
		# but since the Naptan Merger is UK-only anyway ...
		self.area = [
			(-6.4751, 55.4158),
			(-9.3693, 58.2456),
			(-2.6793, 59.8226),
			(-1.4621, 61.3153),
			(0.22388, 61.0546),
			(-1.5652, 58.3303),
			(3.71526, 50.8435),
			(-7.8687, 48.5117),
			(-4.7319, 54.4629),
			(-5.854, 53.8513),
			(-6.2797, 54.1105),
			(-6.6316, 54.0277),
			(-6.648, 54.175),
			(-6.8434, 54.3192),
			(-7.0388, 54.4127),
			(-7.1541, 54.2244),
			(-7.2113, 54.293),
			(-7.8544, 54.2094),
			(-8.1625, 54.4575),
			(-7.9244, 54.6716),
			(-7.858, 54.7372),
			(-7.7195, 54.6014),
			(-7.5448, 54.747),
			(-7.3555, 55.034)
		]

		self.mode = MODE_NONE
		self.current_stop = None
		self.is_bus_stop = False
		self.stop_deleted = False

	def startElement(self, name, attrs):
		if name == "create":
			self.mode = MODE_CREATE
		elif name == "modify":
			self.mode = MODE_MODIFY
		elif name == "delete":
			self.mode = MODE_DELETE

		elif name == "node":	
			if self.mode == MODE_DELETE:
				session.begin_nested()
				session.execute(model.stops.delete().where(sql.and_(
					model.stops.c.osm_id == attrs.getValue("id"),
					model.stops.c.osm_version == attrs.getValue("version")
					)))
				self.stop_deleted = True

			if self.mode == MODE_MODIFY:
				session.begin_nested()
				session.execute(model.stops.delete().where(
					model.stops.c.osm_id == attrs.getValue("id"))
					)
				self.stop_deleted = True

			if self.mode in (MODE_CREATE, MODE_MODIFY):
				lon, lat = float(attrs.getValue("lon")), float(attrs.getValue("lat"))
				if point_in_polygon(lon, lat, self.area):
					node = session.query(model.Stop).filter_by(osm_id=attrs.getValue("id")).first()
					if not node:
						self.current_stop = model.Stop(attrs.getValue("lat"), attrs.getValue("lon"), \
							attrs.getValue("id"), attrs.getValue("version"))
						session.begin_nested()
						session.add(self.current_stop)
						self.is_bus_stop = False

		elif self.current_stop and name == "tag":
			key, val = attrs.getValue("k"), attrs.getValue("v")
			self.current_stop.tags[key] = model.Tag(key, val)
			self.is_bus_stop = self.is_bus_stop or (key == "naptan:AtcoCode" or (key == "highway" and val == "bus_stop"))

	def endElement(self, name):
		if name == "osmChange":
			session.commit()
		elif name in ("create", "modify", "delete"):
			self.mode = MODE_NONE
		elif name == "node":
			if self.current_stop:
				if self.is_bus_stop:
					session.commit()
				else:
					session.rollback()
			if self.stop_deleted:
				session.commit()
				self.stop_deleted = False
			self.current_stop = None
