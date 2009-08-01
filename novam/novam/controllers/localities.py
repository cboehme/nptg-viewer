import logging

from pylons import request, response, session, tmpl_context as c
from pylons.decorators import jsonify
import sqlalchemy.sql.expression as sql

from novam.lib.base import BaseController
from novam import model
from novam.model.meta import session

log = logging.getLogger(__name__)

class LocalitiesController(BaseController):

	@jsonify
	def index(self):
		localities_query = session.query(model.Locality)

		if "bbox" in request.GET:
			bbox_str = request.GET.get("bbox")
			bbox = bbox_str.split(",")
			localities_query = localities_query.filter(sql.and_(
				model.Locality.lat.between(bbox[1], bbox[3]),
				model.Locality.lon.between(bbox[0], bbox[2])
			))

		elif "duplicates_of" in request.GET:
			locality_id = request.GET.get("duplicates_of")
			locality = session.query(model.Locality).filter_by(id=locality_id).one()
			
			localities_query = localities_query.filter(sql.and_(
				sql.func.sign(model.Locality.osm_id) == sql.func.sign(locality.osm_id),
				model.Locality.osm_id != locality.osm_id,
				model.Locality.name == locality.name,
				sql.func.sqrt(
					sql.func.pow(model.Locality.lat-locality.lat, 2)
					+sql.func.pow(model.Locality.lon-locality.lon, 2)
				) < 0.1,
			))

		elif "matches_with" in request.GET:
			locality_id = request.GET.get("matches_with")
			locality = session.query(model.Locality).filter_by(id=locality_id).one()
			
			localities_query = localities_query.filter(sql.and_(
				sql.func.sign(model.Locality.osm_id) != sql.func.sign(locality.osm_id),
				model.Locality.name == locality.name,
				sql.func.sqrt(
					sql.func.pow(model.Locality.lat-locality.lat, 2)
					+sql.func.pow(model.Locality.lon-locality.lon, 2)
				) < 0.1,
			))

		localities_struct = []
		for locality in localities_query.all():
			tags_struct = {}
			for tag in locality.tags:
				tags_struct[tag] = locality.tags[tag].value
			localities_struct.append({
				"id": locality.id,
				"lat": float(locality.lat),
				"lon": float(locality.lon),
				"osm_id": locality.osm_id,
				"osm_version": locality.osm_version,
				"name": locality.name,
				"duplicate_count": locality.duplicate_count,
				"match_count": locality.match_count,
				"tags": tags_struct
			})

		return {"localities": localities_struct}

	@jsonify
	def show(self, id):
		locality = session.query(model.Locality).filter_by(id=id).one()
		
		locality_struct = {
			"id": locality.id,
			"lat": float(locality.lat),
			"lon": float(locality.lon),
			"osm_id": locality.osm_id,
			"osm_version": locality.osm_version,
			"name": locality.name,
			"duplicate_count": locality.duplicate_count,
			"match_count": locality.match_count,
			"tags": {}
		}
		for tag in stop.tags:
			locality_struct["tags"][tag] = stop.tags[tag].value
	
		return locality_struct
