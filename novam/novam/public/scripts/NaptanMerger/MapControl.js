/** 
 * Constant: EPSG4326
 * Projection used by the server for all markers.
 */
NaptanMerger.EPSG4326 = new OpenLayers.Projection("EPSG:4326");

/**
 * Constant: EPSG900913
 * Display projection used by the map.
 */
NaptanMerger.EPSG900913 = new OpenLayers.Projection("EPSG:900913");

/**
 * Class: NaptanMerger.MapControl
 */
NaptanMerger.MapControl = Class.create({

	map: null,
	markerLayer: null,
	featureControl: null,
	loadIndicator: null,

	EVENT_TYPES: ['stop_click', 'waypoint_click', 'image_click',
		'stop_clickout', 'waypoint_clickout', 'image_clickout', 
		'stop_mouseover', 'waypoint_mouseover', 'image_mouseover',
		'stop_mouseout', 'waypoint_mouseout', 'image_mouseout',
		'drag_start', 'drag_done', 'drag_cancelled'],

	events: null,

	/**
	 * Constructor: NaptanMerger.Map
	 * Constructor for a new NaptanMerger.Map instance.
	 *
	 * Parameters:
	 * container - {string} Id of an element on your page that will contain
	 *     the map.
	 */
	initialize: function(container) {

		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		this.map = new OpenLayers.Map(container, {
			controls: [
				new OpenLayers.Control.Navigation(),
				new OpenLayers.Control.PanZoomBar()
			],
			units: 'm',
			projection: NaptanMerger.EPSG900913,
			displayProjection: NaptanMerger.EPSG4326
		});

		this.loadIndicator = new Element("div", {"class": "MapLoadIndicator"});
		this.loadIndicator.appendChild(Text("Loading ..."));
		$(container).appendChild(this.loadIndicator);
		this.loadIndicator.hide();
		
		// Create a mapnik base layer:
		var mapnik = new OpenLayers.Layer.OSM.Mapnik("OpenStreetMap", {
			displayOutsideMaxExtent: true,
			wrapDateLine: true
		});
		this.map.addLayer(mapnik);
		
		// Define styling for the marker layer:
		var styleMap = new OpenLayers.StyleMap({
			'default': new OpenLayers.Style({
				graphicHeight: 16,
				graphicWidth: 16,
				graphicXOffset: -8,
				graphicYOffset: -8,
				externalGraphic: '${type}.png',
				cursor: 'pointer'
			}),
			'highlighted': new OpenLayers.Style({
				graphicHeight: 22,
				graphicWidth: 22,
				graphicXOffset: -11,
				graphicYOffset: -11,
				externalGraphic: '${type}_highlighted.png',
				cursor: 'pointer'
			}),
			'selected': new OpenLayers.Style({
				externalGraphic: '${type}_selected.png',
				cursor: ''
			}),
			'selected_highlighted': new OpenLayers.Style({
				graphicHeight: 22,
				graphicWidth: 22,
				graphicXOffset: -11,
				graphicYOffset: -11,
				externalGraphic: '${type}_selected_highlighted.png',
				cursor: ''
			}),
			'marked': new OpenLayers.Style({
				externalGraphic: '${type}_marked.png',
				cursor: ''
			}),
			'marked_highlighted': new OpenLayers.Style({
				graphicHeight: 22,
				graphicWidth: 22,
				graphicXOffset: -11,
				graphicYOffset: -11,
				externalGraphic: '${type}_marked_highlighted.png',
				cursor: ''
			}),
			'marked_selected': new OpenLayers.Style({
				externalGraphic: '${type}_marked_selected.png',
				cursor: ''
			}),
			'marked_selected_highlighted': new OpenLayers.Style({
				graphicHeight: 22,
				graphicWidth: 22,
				graphicXOffset: -11,
				graphicYOffset: -11,
				externalGraphic: '${type}_marked_selected_highlighted.png',
				cursor: ''
			}),
			'deleted': new OpenLayers.Style({
				externalGraphic: '${type}_deleted.png',
				cursor: ''
			})
		});

		// Create the marker layer:
		this.markerLayer = new OpenLayers.Layer.Vector('Markers', {styleMap: styleMap});
		this.map.addLayer(this.markerLayer);

		this.map.events.register('moveend', this, this.saveMapLocation);
		this.map.events.register('moveend', this, this.getStops);
		this.map.events.register('moveend', this, this.getWaypoints);
		this.map.events.register('moveend', this, this.getImages);

		// Add control for the marker layer:
		this.featureControl = new NaptanMerger.FeatureControl(this.markerLayer);
		this.map.addControl(this.featureControl);
		this.featureControl.activate();

		// Register event handlers for features:
		this.featureControl.events.register('click', this, function (evt) {
			var eventName = evt.feature.attributes.type + '_click';
			if (evt.feature.attributes.type.endsWith('stop'))
				eventName = 'stop_click';
			this.events.triggerEvent(eventName, {
				feature: evt.feature, 
				shiftKey: evt.shiftKey,
				ctrlKey: evt.ctrlKey
			});
		});

		this.featureControl.events.register('clickout', this, function (evt) {
			var eventName = evt.feature.attributes.type + '_clickout';
			if (evt.feature.attributes.type.endsWith('stop'))
				eventName = 'stop_clickout';
			this.events.triggerEvent(eventName, {feature: evt.feature});
		});

		this.featureControl.events.register('mouseover', this, function (evt) {
			var eventName = evt.feature.attributes.type + '_mouseover';
			if (evt.feature.attributes.type.endsWith('stop'))
				eventName = 'stop_mouseover';
			this.events.triggerEvent(eventName, {feature: evt.feature});
		});

		this.featureControl.events.register('mouseout', this, function (evt) {
			var eventName = evt.feature.attributes.type + '_mouseout';
			if (evt.feature.attributes.type.endsWith('stop'))
				eventName = 'stop_mouseout';
			this.events.triggerEvent(eventName, {feature: evt.feature});
		});

		this.featureControl.events.register('drag_start', this, function (evt) {
			this.events.triggerEvent('drag_start', {feature: evt.feature});
		});

		this.featureControl.events.register('drag_done', this, function (evt) {
			this.events.triggerEvent('drag_done', {feature: evt.feature});
		});

		this.featureControl.events.register('drag_cancelled', this, function (evt) {
			this.events.triggerEvent('drag_cancelled', {feature: evt.feature});
		});

		
		// Load previous map location:
		var loc = new OpenLayers.LonLat(-1.902, 52.477);
		var zoom = 15;
		cookie = getCookie("map_location");
		if (cookie != null)
		{
			v = cookie.split(":");
			loc.lat = Number(v[0]);
			loc.lon = Number(v[1]);
			zoom = Number(v[2]);
		}
		this.map.setCenter(loc.transform(NaptanMerger.EPSG4326, this.map.getProjectionObject()), zoom);
			
		// Load features:
		this.getStops();
		this.getWaypoints();
		this.getImages();
	},

	destroy: function() {
		this.markerControl = null;
		this.markerLayer = null;
		this.map = null;

		this.events = null;
	},

	saveMapLocation: function() {
		var loc = this.map.getCenter().clone().transform(this.map.getProjectionObject(), NaptanMerger.EPSG4326);
		var zoom = this.map.getZoom();

		var decimals = Math.pow(10, Math.floor(zoom/3));

		loc.lat = Math.round(loc.lat * decimals) / decimals;
		loc.lon = Math.round(loc.lon * decimals) / decimals;

		setCookie("map_location", loc.lat+":"+loc.lon+":"+zoom);
	},
	
	highlightFeature: function (feature) {
		if (feature.renderIntent == 'default')
			feature.renderIntent = 'highlighted';
		else if (!feature.renderIntent.endsWith('highlighted'))
			feature.renderIntent += '_highlighted';

		this.markerLayer.drawFeature(feature);
	},

	unhighlightFeature: function (feature) {
		if (feature.renderIntent == 'highlighted')
			feature.renderIntent = 'default';
		else
			feature.renderIntent = feature.renderIntent.replace(/_highlighted/, '');

		this.markerLayer.drawFeature(feature);
	},

	selectFeature: function (feature) {
		if (feature.renderIntent.endsWith('highlighted'))
		{
			if (feature.renderIntent.startsWith('marked'))
				feature.renderIntent = 'marked_selected_highlighted';
			else
				feature.renderIntent = 'selected_highlighted';
		}
		else
		{
			if (feature.renderIntent.startsWith('marked'))
				feature.renderIntent = 'marked_selected';
			else
				feature.renderIntent = 'selected';
		}

		this.markerLayer.drawFeature(feature);
	},

	unselectFeature: function (feature) {
		if (feature.renderIntent == 'selected')
			feature.renderIntent = 'default';
		else
		{
			feature.renderIntent = feature.renderIntent.replace(/_selected/, '');
			feature.renderIntent = feature.renderIntent.replace(/selected_/, '');
		}
		this.markerLayer.drawFeature(feature);
	},

	markFeature: function (feature) {
		if (feature.renderIntent == 'default')
			feature.renderIntent = 'marked';
		else if (!feature.renderIntent.startsWith('marked'))
			feature.renderIntent = 'marked_' + feature.renderIntent;
		this.markerLayer.drawFeature(feature);
	},

	unmarkFeature: function (feature) {
		if (feature.renderIntent == 'marked')
			feature.renderIntent = 'default';
		else
			feature.renderIntent = feature.renderIntent.replace(/marked_/, '');

		this.markerLayer.drawFeature(feature);
	},

	activateDragging: function (feature) {
		this.featureControl.activateDragging(feature);
	},

	deactivateDragging: function (feature) {
		this.featureControl.deactivateDragging(feature);
	},

	getStops: function() {
		if (this.map.getZoom() > 11)
		{
			var bounds = this.map.getExtent().clone();
			bounds = bounds.transform(NaptanMerger.EPSG900913, NaptanMerger.EPSG4326);

			this.loadIndicator.show();

			var request = OpenLayers.Request.GET({
				url: "osmdata?bbox="+bounds.toBBOX(),
				scope: this,
				success: function (request)
				{
					json = new OpenLayers.Format.JSON();
					data = json.read(request.responseText);
					this.addStops(data);
					this.loadIndicator.hide();
				}
			});
		}
	},

	getWaypoints: function() {
		if (this.map.getZoom() > 14)
		{
			var bounds = this.map.getExtent().clone();
			bounds = bounds.transform(NaptanMerger.EPSG900913, NaptanMerger.EPSG4326);

			var request = OpenLayers.Request.GET({
				url: "waypoints?bbox="+bounds.toBBOX(),
				scope: this,
				success: function(request)
				{
					json = new OpenLayers.Format.JSON();
					data = json.read(request.responseText);
					this.addWaypoints(data);
				}
			});
		}
	},

	getImages: function() {
		if (this.map.getZoom() > 14)
		{
			var bounds = this.map.getExtent().clone();
			bounds = bounds.transform(NaptanMerger.EPSG900913, NaptanMerger.EPSG4326);

			var request = OpenLayers.Request.GET({
				url: "images?bbox="+bounds.toBBOX(),
				scope: this,
				success: function(request)
				{
					json = new OpenLayers.Format.JSON();
					data = json.read(request.responseText);
					this.addImages(data);
				}
			});
		}
	},

	/**
	 * Method: findStop
	 */
	findStop: function(id)
	{
		return this.markerLayer.features.find(function(feature) { 
			return feature.attributes.type.endsWith('stop') && feature.attributes.id == id; 
		});
	},
	
	/**
	 * Method: findWaypoint
	 */
	findWaypoint: function(id)
	{
		return this.markerLayer.features.find(function(feature) { 
			return feature.attributes.type == 'waypoint' && feature.attributes.id == id; 
		});
	},

	/**
	 * Method: findImage
	 */
	findImage: function(id)
	{
		return this.markerLayer.features.find(function(feature) { 
			return feature.attributes.type == 'image' && feature.attributes.id == id; 
		});
	},

	/**
	 * Method: addStops
	 * Add stops to the marker layer on the map.
	 *
	 * Parameters:
	 * stops - {Array of Stops} List of stops to add to the map.
	 */
	addStops: function(stops) {
		var newFeatures = new Array();

		stops.each(function(stop) {
			if (this.findStop(stop.id) != undefined)  return;

			var position = new OpenLayers.Geometry.Point(stop.lon, stop.lat);
			position = position.transform(NaptanMerger.EPSG4326, NaptanMerger.EPSG900913);

			/*if ('highway' in stop.tags 
				&& 'naptan:AtcoCode' in stop.tags 
				&& !('naptan:unverified' in stop.tags)
				&& 'route_ref' in stop.tags
				&& 'shelter' in stop.tags)
					stop.type = 'finished_stop';
			else if (!('highway' in stop.tags)
				&& 'naptan:AtcoCode' in stop.tags 
				&& 'naptan:unverified' in stop.tags)
					stop.type = 'plain_naptan_stop';
			else if ('highway' in stop.tags
				&& !('naptan:AtcoCode' in stop.tags))
					stop.type = 'plain_osm_stop';
			else if (!('highway' in stop.tags)
				&& 'naptan:AtcoCode' in stop.tags 
				&& stop.tags['physically_present'] == 'no')
					stop.type = 'no_physical_stop';
			else
				stop.type = 'merged_stop';
			*/
			stop.type = 'plain_naptan_stop';

			newFeatures.push(new OpenLayers.Feature.Vector(position, stop));
		}, this);

		this.markerLayer.addFeatures(newFeatures);
	},

	/**
	 * Method: addWaypoints
	 * Add waypoints to the marker layer on the map.
	 *
	 * Parameters:
	 * waypoints - {Array of Waypoints} List of waypoints to add to the map.
	 */
	addWaypoints: function(waypoints) {
		var newFeatures = new Array();

		waypoints.each(function(waypoint) {
			if (this.findWaypoint(waypoint.id) != undefined)  return;
			
			var position = new OpenLayers.Geometry.Point(waypoint.lon, waypoint.lat);
			position = position.transform(NaptanMerger.EPSG4326, NaptanMerger.EPSG900913);

			waypoint.type = "waypoint";
			
			newFeatures.push(new OpenLayers.Feature.Vector(position, waypoint));
		}, this);

		this.markerLayer.addFeatures(newFeatures);
	},

	/**
	 * Method: addImages
	 * Add images to the marker layer.
	 *
	 * Parameters:
	 * images - {Array of Images} List of images to add to the map.
	 */
	addImages: function(images) {
		var newFeatures = new Array();

		images.each(function(image) {
			if (this.findImage(image.id) != undefined)  return;

			var position = new OpenLayers.Geometry.Point(image.lon, image.lat);
			position = position.transform(NaptanMerger.EPSG4326, NaptanMerger.EPSG900913);

			image.type = "image";
			
			newFeatures.push(new OpenLayers.Feature.Vector(position, image));
		}, this);

		this.markerLayer.addFeatures(newFeatures);
	}
});
