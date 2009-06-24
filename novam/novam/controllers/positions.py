import logging
import math

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons.decorators import jsonify
import sqlalchemy.sql.expression as sql

from novam.lib.base import BaseController, render
from novam import model
from novam.model.meta import session

log = logging.getLogger(__name__)

class PositionsController(BaseController):

	@jsonify
	def index(self):
		
		waypoints_query = session.query(model.Waypoint)
		images_query = session.query(model.Image)

		if "bbox" in request.GET:
			bbox_str = request.GET.get("bbox")
			bbox = bbox_str.split(",")
			waypoints_query = waypoints_query.filter(sql.and_(
				model.Waypoint.lat.between(bbox[1], bbox[3]),
				model.Waypoint.lon.between(bbox[0], bbox[2])
			))
			images_query = images_query.filter(sql.and_(
				model.Image.lat.between(bbox[1], bbox[3]),
				model.Image.lon.between(bbox[0], bbox[2])
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
			images_query = images_query.filter(
				sql.func.sqrt(sql.func.pow(model.Image.lat-loc[1], 2)
				+sql.func.pow(model.Image.lon-loc[0], 2)
				) < 0.005
			).order_by(sql.func.sqrt(sql.func.pow(model.Image.lat-loc[1], 2)
				+sql.func.pow(model.Image.lon-loc[0], 2)
				)).limit(10)


		positions_struct = []
		for waypoint in waypoints_query.all():
			positions_struct.append({
				"type": "waypoint",
				"id": waypoint.id,
				"lat": float(waypoint.lat),
				"lon": float(waypoint.lon),
				"name": waypoint.name
			})
		for image in images_query.all():
			positions_struct.append({
				"type": "image",
				"id": image.id,
				"lat": float(image.lat),
				"lon": float(image.lon)
			})

		if "loc" in request.GET:
			positions_struct.sort(key=lambda x: math.sqrt(math.pow(x["lat"]-loc[1], 2) + math.pow(x["lon"]-loc[0] ,2)))

		return positions_struct
