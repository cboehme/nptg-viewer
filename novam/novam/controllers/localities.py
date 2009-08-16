import logging

from pylons import request, response, session, tmpl_context as c
from pylons.decorators import jsonify
from pylons.decorators.rest import restrict
import sqlalchemy.sql.expression as sql
from datetime import datetime

from novam.lib.base import BaseController
from novam import model
from novam.model.meta import session
from novam.lib.utilities import strip_control_chars

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
				locality.hidden == None,
				model.Locality.hidden == None,
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
				locality.hidden == None,
				model.Locality.hidden == None,
				sql.func.sign(model.Locality.osm_id) != sql.func.sign(locality.osm_id),
				model.Locality.name == locality.name,
				sql.func.sqrt(
					sql.func.pow(model.Locality.lat-locality.lat, 2)
					+sql.func.pow(model.Locality.lon-locality.lon, 2)
				) < 0.1,
			))

		localities_struct = []
		for locality in localities_query.all():
			hidden = None
			if locality.hidden:
				hidden = locality.hidden.strftime("%c")
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
				"hidden": hidden,
				"comment": locality.comment,
				"duplicate_count": locality.duplicate_count,
				"match_count": locality.match_count,
				"tags": tags_struct
			})

		return {"localities": localities_struct}

	@jsonify
	def show(self, id):
		locality = session.query(model.Locality).filter_by(id=id).one()
		
		hidden = None
		if locality.hidden:
			hidden = locality.hidden.strftime("%c")
		locality_struct = {
			"id": locality.id,
			"lat": float(locality.lat),
			"lon": float(locality.lon),
			"osm_id": locality.osm_id,
			"osm_version": locality.osm_version,
			"name": locality.name,
			"hidden": hidden,
			"comment": locality.comment,
			"duplicate_count": locality.duplicate_count,
			"match_count": locality.match_count,
			"tags": {}
		}
		for tag in locality.tags:
			locality_struct["tags"][tag] = locality.tags[tag].value
	
		return locality_struct
	
	@restrict("POST")
	@jsonify
	def hide(self, id):
		localities_struct = []
		try:
			comment = strip_control_chars(request.POST.getone("comment"))

			result = session.execute(
				model.localities.update(
					values={"hidden": datetime.now, "comment": comment}
				).where(sql.and_(
					model.localities.c.id == id,
					model.localities.c.hidden == None
				))
			).rowcount
			session.commit()

			locality = session.query(model.Locality).filter_by(id=id).one()

			localities_query = session.query(model.Locality)
			localities_query = localities_query.filter(sql.and_(
				model.Locality.hidden == None,
				sql.or_(
					sql.and_(
						sql.func.sign(model.Locality.osm_id) == sql.func.sign(locality.osm_id),
						model.Locality.osm_id != locality.osm_id
					),
					sql.func.sign(model.Locality.osm_id) != sql.func.sign(locality.osm_id),
				),
				model.Locality.name == locality.name,
				sql.func.sqrt(
					sql.func.pow(model.Locality.lat-locality.lat, 2)
					+sql.func.pow(model.Locality.lon-locality.lon, 2)
				) < 0.1,
			))

			for locality in [locality] + localities_query.all():
				hidden = None
				if locality.hidden:
					hidden = locality.hidden.strftime("%c")
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
					"hidden": hidden,
					"comment": locality.comment,
					"duplicate_count": locality.duplicate_count,
					"match_count": locality.match_count,
					"tags": tags_struct
				})
		except:
			return {"localities": None}

		return {"localities": localities_struct}


	@restrict("POST")
	@jsonify
	def unhide(self, id):
		localities_struct = []
		try:
			result = session.execute(
				model.localities.update(
					values={"hidden": None, "comment": None}
				).where(model.localities.c.id == id)
			).rowcount
			session.commit()

			locality = session.query(model.Locality).filter_by(id=id).one()

			localities_query = session.query(model.Locality)
			localities_query = localities_query.filter(sql.and_(
				model.Locality.hidden == None,
				sql.or_(
					sql.and_(
						sql.func.sign(model.Locality.osm_id) == sql.func.sign(locality.osm_id),
						model.Locality.osm_id != locality.osm_id
					),
					sql.func.sign(model.Locality.osm_id) != sql.func.sign(locality.osm_id),
				),
				model.Locality.name == locality.name,
				sql.func.sqrt(
					sql.func.pow(model.Locality.lat-locality.lat, 2)
					+sql.func.pow(model.Locality.lon-locality.lon, 2)
				) < 0.1,
			))

			for locality in [locality] + localities_query.all():
				hidden = None
				if locality.hidden:
					hidden = locality.hidden.strftime("%c")
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
					"hidden": hidden,
					"comment": locality.comment,
					"duplicate_count": locality.duplicate_count,
					"match_count": locality.match_count,
					"tags": tags_struct
				})
		except:
			return {"localities": None}

		return {"localities": localities_struct}
