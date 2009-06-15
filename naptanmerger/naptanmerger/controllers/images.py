import logging
import shutil
import mimetypes

from pylons.decorators import jsonify
import sqlalchemy.sql.expression as sql

from naptanmerger.lib.base import *
from naptanmerger import model
from naptanmerger.model.meta import session
from naptanmerger.lib import EXIFHelper

log = logging.getLogger(__name__)

class ImagesController(BaseController):

	@jsonify
	def index(self):
		
		images_query = session.query(model.Image)

		if "bbox" in request.GET:
			bbox_str = request.GET.get("bbox")
			bbox = bbox_str.split(",")
			images_query = images_query.filter(sql.and_(
				model.Image.lat.between(bbox[1], bbox[3]),
				model.Image.lon.between(bbox[0], bbox[2])
			))
		elif "loc" in request.GET:
			loc_str = request.GET.get("loc")
			loc = [float(l.strip()) for l in loc_str.split(",")];
			images_query = images_query.filter(
				sql.func.sqrt(sql.func.pow(model.Image.lat-loc[1], 2)
				+sql.func.pow(model.Image.lon-loc[0], 2)
				) < 0.005
			).order_by(sql.func.sqrt(sql.func.pow(model.Image.lat-loc[1], 2)
				+sql.func.pow(model.Image.lon-loc[0], 2)
				)).limit(10)

		images_struct = []
		for image in images_query.all():
			images_struct.append({
				"id": image.id,
				"lat": float(image.lat),
				"lon": float(image.lon)
			})

		return images_struct

	def show(self, id):
		image = session.query(model.Image).filter_by(id=id).one()
		fh = open(image.file_path, 'rb')
		data = fh.read()
		fh.close()
		mime_type = mimetypes.guess_type(image.file_path)
		if mime_type[0] is not None:
			response.content_type = mime_type[0]
		else:
			response.content_type = "application/octet-stream"
		return data

	def importdata(self):
		upload = request.params["image"]
		image = model.Image()
		fh = open(image.file_path, "wb")
		shutil.copyfileobj(upload.file, fh)
		upload.file.close()
		fh.close()

		pos = EXIFHelper.get_gps_info(image.file_path)
		if not pos:
			return "Error"
		image.lat = pos[1]
		image.lon = pos[0]

		session.add(image)
		session.commit()
		return "OK"

	def import_form(self):
		return render("/images/import_form.mako")
