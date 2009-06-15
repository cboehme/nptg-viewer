from xml.sax.handler import ContentHandler
from naptanmerger import model
from naptanmerger.model.meta import session

class GPXImporter(ContentHandler):
	def __init__(self):
		self.current_waypoint = None
		self.reading_name = False

	def startElement(self, name, attrs):
		if name == "wpt":
			self.current_waypoint = model.Waypoint(attrs.getValue("lat"), attrs.getValue("lon"), "")

		elif name == "name" and self.current_waypoint is not None:
			self.reading_name = True

	def endElement(self, name):
		if name == "wpt":
			session.add(self.current_waypoint)
			session.commit()
		elif name == "name":
			self.reading_name = False

	def characters(self, content):
		if self.reading_name:
			self.current_waypoint.name = self.current_waypoint.name + content
