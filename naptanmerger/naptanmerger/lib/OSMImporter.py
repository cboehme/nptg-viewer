from xml.sax.handler import ContentHandler
from naptanmerger import model
from naptanmerger.model.meta import session

class OSMImporter(ContentHandler):
	def __init__(self):
		self.current_stop = None

	def startElement(self, name, attrs):
		if name == "node":
			self.current_stop = session.query(model.Stop).filter_by(osm_id=attrs.getValue("id")).first()
			if not self.current_stop:
				self.current_stop = model.Stop(0, 0, attrs.getValue("id"))
			else:
				for i in self.current_stop.tags:
					session.delete(self.current_stop.tags[i])
			self.current_stop.lat = attrs.getValue("lat")
			self.current_stop.lon = attrs.getValue("lon")

		elif name == "tag":
			self.current_stop.tags[attrs.getValue("k")] = model.Tag(attrs.getValue("k"), attrs.getValue("v"))

	def endElement(self, name):
		if name == "node":
			session.add(self.current_stop)
			session.commit()
