import logging
from xml.sax import parse, SAXException

from pylons.decorators import jsonify
import sqlalchemy.sql.expression as sql

from naptanmerger.lib.base import *
from naptanmerger.lib.GPXImporter import GPXImporter
from naptanmerger import model
from naptanmerger.model.meta import session

log = logging.getLogger(__name__)

class WaypointsController(BaseController):

	@jsonify
	def index(self):
		
		waypoints_query = session.query(model.Waypoint)

		if "bbox" in request.GET:
			bbox_str = request.GET.get("bbox")
			bbox = bbox_str.split(",")
			waypoints_query = waypoints_query.filter(sql.and_(
				model.Waypoint.lat.between(bbox[1], bbox[3]),
				model.Waypoint.lon.between(bbox[0], bbox[2])
			))
		elif "loc" in request.GET:
			loc_str = request.GET.get("loc")
			loc = [float(l.strip()) for l in loc_str.split(",")]
			waypoints_query = waypoints_query.filter(
				sql.func.sqrt(sql.func.pow(model.Waypoint.lat-loc[1], 2)
				+sql.func.pow(model.Waypoint.lon-loc[0], 2)
				) < 0.005
			).order_by(sql.func.sqrt(sql.func.pow(model.Waypoint.lat-loc[1], 2)
				+sql.func.pow(model.Waypoint.lon-loc[0], 2)
				)).limit(10)

		waypoints_struct = []
		for waypoint in waypoints_query.all():
			waypoints_struct.append({
				"id": waypoint.id,
				"lat": float(waypoint.lat),
				"lon": float(waypoint.lon),
				"name": waypoint.name
			})

		return waypoints_struct

	def importdata(self):
		try:
			# Add a content-type based decision where to import the
			# data from:
			parse(request.params["gpxdata"].file, GPXImporter())
			#parse(request.body, GPXImporter())
			return "OK"
		except SAXException, e:
			return "Failed: %s" % e.getMessage()

	def import_form(self):
		return render("/waypoints/import_form.mako")
