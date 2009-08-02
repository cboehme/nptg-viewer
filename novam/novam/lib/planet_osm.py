from xml.sax import parse
from xml.sax.handler import ContentHandler, ErrorHandler
from gzip import GzipFile
from urllib2 import urlopen
from StringIO import StringIO
from bz2 import BZ2Decompressor
import sqlalchemy.sql.expression as sql
import logging
import re

from novam import model
from novam.model.meta import session
from novam.lib.geometry_utils import point_in_polygon

log = logging.getLogger(__name__)

class _TransactionHandling(object):
	def __init__(self):
		self._transactions = 0
	
	def __del__(self):
		self._rollback_all()

	def _begin(self):
		session.begin_nested()
		self._transactions += 1
	
	def _commit(self):
		session.commit()
		self._transactions -= 1

	def _rollback(self):
		session.rollback()
		self._transactions -= 1

	def _rollback_all(self):
		while self._transactions:
			self._rollback()
	

class Importer(_TransactionHandling, ContentHandler, ErrorHandler):
	"""Import all localities from a planet file into the database
	"""

	def __init__(self, delete=True):
		_TransactionHandling.__init__(self)
		self.delete = delete

	def __del__(self):
		_TransactionHandling.__del__(self)
	
	def startDocument(self):
		self.valid_path = [True]
		self.current_locality = None
		self.is_locality = False
		self._begin()

	def endDocument(self):
		self._commit()

	def startElement(self, name, attrs):
		try:
			if self.valid_path[-1]:
				if len(self.valid_path) == 1 and name == "osm":
					if self.delete:
						session.execute(model.localities.delete())
					self.valid_path.append(True)
				elif len(self.valid_path) == 2 and name == "node":
					self.current_locality = model.Locality(
						attrs.getValue("lat"), attrs.getValue("lon"),
						attrs.getValue("id"), attrs.getValue("version")
					)
					self._begin()
					session.add(self.current_locality)
					self.is_locality = False
					self.valid_path.append(True)
				elif len(self.valid_path) == 3 and name == "tag":
					key, val = attrs.getValue("k"), attrs.getValue("v")
					print key+":", repr(val), type(val)
					self.current_locality.tags[key] = model.Tag(key, val)
					self.is_locality = self.is_locality \
						or (key == "source" and val == "nptg_import") \
						or key == "place"
					self.valid_path.append(True)
				else:
					self.valid_path.append(False)
			else:
				self.valid_path.append(False)
		except:
			self._rollback_all()
			raise

	def endElement(self, name):
		try:
			if self.valid_path[-1] and name == "node":
				if self.is_locality:
					if "name" in self.current_locality.tags:
						self.current_locality.name = self.current_locality.tags["name"].value
					elif "LocalityName" in self.current_locality.tags:
						self.current_locality.name = self.current_locality.tags["LocalityName"].value
					self._commit()
				else:
					self._rollback()
				self.current_locality = None
			del self.valid_path[-1]
		except:
			self._rollback_all()
			raise

	def error(self, exception):
		self._rollback_all()
		raise exception

	def fatalError(self, exception):
		self._rollback_all()
		raise exception


class Updater(_TransactionHandling, ContentHandler, ErrorHandler):
	"""Update the current database with an osm changeset file
	"""

	__MODE_NONE = 0
	__MODE_CREATE = 1
	__MODE_MODIFY = 2
	__MODE_DELETE = 3

	def __init__(self):
		_TransactionHandling.__init__(self)

		# Rough outline of the UK. That should be in a config file
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

	def __del__(self):
		_TransactionHandling.__del__(self)
		
	def startDocument(self):
		self.valid_path = [True]
		self.mode = self.__MODE_NONE
		self.current_locality = None
		self.is_locality = False
		self.locality_deleted = False
		self._begin()

	def endDocument(self):
		self._commit()

	def startElement(self, name, attrs):
		try:
			if self.valid_path[-1]:
				if len(self.valid_path) == 1 and name  == "osmChange":
					self.valid_path.append(True)

				elif len(self.valid_path) == 2 and name == "create":
					self.mode = self.__MODE_CREATE
					self.valid_path.append(True)
				elif len(self.valid_path) == 2 and name == "modify":
					self.mode = self.__MODE_MODIFY
					self.valid_path.append(True)
				elif len(self.valid_path) == 2 and name == "delete":
					self.mode = self.__MODE_DELETE
					self.valid_path.append(True)

				elif len(self.valid_path) == 3 and name == "node":
					if self.mode == self.__MODE_DELETE:
						self._begin()
						session.execute(model.localities.delete().where(sql.and_(
							model.localities.c.osm_id == attrs.getValue("id"),
							model.localities.c.osm_version == int(attrs.getValue("version")) - 1
						)))
						self.locality_deleted = True

					if self.mode == self.__MODE_MODIFY:
						node = session.query(model.Locality).filter(sql.and_(
							model.localities.c.osm_id == attrs.getValue("id"),
							model.localities.c.osm_version < attrs.getValue("version")
							)).enable_eagerloads(False).first()
						if node:
							self._begin()
							session.execute(model.localities.delete().where(
								model.localities.c.osm_id == attrs.getValue("id"))
							)
							self.locality_deleted = True

					if self.mode in (self.__MODE_CREATE, self.__MODE_MODIFY):
						lon, lat = float(attrs.getValue("lon")), float(attrs.getValue("lat"))
						if point_in_polygon(lon, lat, self.area):
							node = session.query(model.Locality).filter_by(
								osm_id=attrs.getValue("id")
							).enable_eagerloads(False).first()
							if not node:
								self.current_locality = model.Locality(
									attrs.getValue("lat"), attrs.getValue("lon"),
									attrs.getValue("id"), attrs.getValue("version")
								)
								self._begin()
								session.add(self.current_locality)
								self.is_locality = False
					self.valid_path.append(True)

				elif len(self.valid_path) == 4 and name == "tag":
					if self.current_locality:
						key, val = attrs.getValue("k"), attrs.getValue("v")
						self.current_locality.tags[key] = model.Tag(key, val)
						self.is_locality = self.is_locality \
							or (key == "source" and val == "nptg_import") \
							or key == "place"
					self.valid_path.append(True)

				else:
					self.valid_path.append(False)
			else:
				self.valid_path.append(False)
		except:
			self._rollback_all()
			raise

	def endElement(self, name):
		try:
			if self.valid_path[-1]:
				if name in ("create", "modify", "delete"):
					self.mode = self.__MODE_NONE
				elif name == "node":
					if self.current_locality:
						if self.is_locality:
							if "name" in self.current_locality.tags:
								self.current_locality.name = self.current_locality.tags["name"].value
							elif "LocalityName" in self.current_locality.tags:
								self.current_locality.name = self.current_locality.tags["LocalityName"].value
							self._commit()
						else:
							self._rollback()
					if self.locality_deleted:
						self._commit()
						self.locality_deleted = False
					self.current_locality = None
			del self.valid_path[-1]
		except:
			self._rollback_all()
			raise

	def error(self, exception):
		self._rollback_all()
		raise exception

	def fatalError(self, exception):
		self._rollback_all()
		raise exception


class _StreamDecompressor:
	__READ_LEN = 8192  # This value can be tuned depending on the data source

	def __init__(self, stream):
		self.__stream = stream
		self.__decompressor = BZ2Decompressor()
		self.__buffer = ""

	def read(self, n=None):
		if n == None:
			ret = self.__buffer \
				+ self.__decompressor.decompress(self.__stream.read())
			self.__buffer = ""
			return ret
		else:
			try:
				while len(self.__buffer) < n:
					self.__buffer = self.__buffer \
						+ self.__decompressor.decompress(self.__stream.read(self.__READ_LEN))
			except EOFError:
				n = len(self.__buffer)
			except:
				raise

			ret = self.__buffer[:n]
			self.__buffer = self.__buffer[n:]
			return ret


def load(url, timestamp, handler):
	log.info("Loading planet dump/diff from %s.", url)	
	fh = urlopen(url)
	headers = fh.info()
	if ("content-type" in headers and headers["content-type"] == "application/x-gzip") \
		or re.search(r"\.gz$", fh.geturl()):
		buffered_fh = StringIO(fh.read())
		unzipped_fh = GzipFile(fileobj=buffered_fh)
		parse(unzipped_fh, handler, handler)
		unzipped_fh.close()
		buffered_fh.close()
	elif ("content-type" in headers and headers["content-type"] == "application/x-bzip2") \
		or re.search(r"\.bz2$", fh.geturl()):
		parse(_StreamDecompressor(fh), handler, handler)
	else:
		parse(fh, handler, handler)
	model.planet_timestamp.set(timestamp)
	fh.close()
	log.info("Dump/diff successfully loaded.")
