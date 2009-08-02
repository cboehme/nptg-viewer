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

	EVENT_TYPES: ['stop_click', 'stop_clickout', 'stop_mouseover', 'stop_mouseout'],

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
				cursor: 'pointer',
				graphicOpacity: 1.0
			}),
			'selected': new OpenLayers.Style({
				externalGraphic: '${type}_selected.png',
				cursor: '',
				graphicOpacity: 1.0
			}),
			'selected_highlighted': new OpenLayers.Style({
				graphicHeight: 22,
				graphicWidth: 22,
				graphicXOffset: -11,
				graphicYOffset: -11,
				externalGraphic: '${type}_selected_highlighted.png',
				cursor: '',
				graphicOpacity: 1.0
			}),
			'marked': new OpenLayers.Style({
				externalGraphic: '${type}_marked.png',
				cursor: 'pointer',
				graphicOpacity: 1.0
			}),
			'marked_highlighted': new OpenLayers.Style({
				graphicHeight: 22,
				graphicWidth: 22,
				graphicXOffset: -11,
				graphicYOffset: -11,
				externalGraphic: '${type}_marked_highlighted.png',
				cursor: 'pointer',
				graphicOpacity: 1.0
			}),
			'marked_selected': new OpenLayers.Style({
				externalGraphic: '${type}_marked_selected.png',
				cursor: '',
				graphicOpacity: 1.0
			}),
			'marked_selected_highlighted': new OpenLayers.Style({
				graphicHeight: 22,
				graphicWidth: 22,
				graphicXOffset: -11,
				graphicYOffset: -11,
				externalGraphic: '${type}_marked_selected_highlighted.png',
				cursor: '',
				graphicOpacity: 1.0
			})
		});
		var opacityLookup = {
			"deleted_nptg_locality": {graphicOpacity: 0.4},
			"deleted_osm_locality": {graphicOpacity: 0.4},
			"matched_nptg_locality": {graphicOpacity: 0.6},
			"matched_osm_locality": {},
			"plain_nptg_locality": {},
			"plain_osm_locality": {},
			"error_nptg_locality": {},
			"error_osm_locality": {}
		};
		styleMap.addUniqueValueRules("default", "type", opacityLookup);

		// Create the marker layer:
		this.markerLayer = new OpenLayers.Layer.Vector('Markers', {styleMap: styleMap});
		this.map.addLayer(this.markerLayer);

		this.map.events.register('moveend', this, this.saveMapLocation);
		this.map.events.register('moveend', this, this.getStops);

		// Add control for the marker layer:
		this.featureControl = new NaptanMerger.FeatureControl(this.markerLayer);
		this.map.addControl(this.featureControl);
		this.featureControl.activate();

		// Register event handlers for features:
		this.featureControl.events.register('click', this, function (evt) {
			var eventName = evt.feature.attributes.type + '_click';
			if (evt.feature.attributes.type.endsWith('locality'))
				eventName = 'stop_click';
			this.events.triggerEvent(eventName, {
				feature: evt.feature, 
				shiftKey: evt.shiftKey,
				ctrlKey: evt.ctrlKey
			});
		});

		this.featureControl.events.register('clickout', this, function (evt) {
			var eventName = evt.feature.attributes.type + '_clickout';
			if (evt.feature.attributes.type.endsWith('locality'))
				eventName = 'stop_clickout';
			this.events.triggerEvent(eventName, {feature: evt.feature});
		});

		this.featureControl.events.register('mouseover', this, function (evt) {
			var eventName = evt.feature.attributes.type + '_mouseover';
			if (evt.feature.attributes.type.endsWith('locality'))
				eventName = 'stop_mouseover';
			this.events.triggerEvent(eventName, {feature: evt.feature});
		});

		this.featureControl.events.register('mouseout', this, function (evt) {
			var eventName = evt.feature.attributes.type + '_mouseout';
			if (evt.feature.attributes.type.endsWith('locality'))
				eventName = 'stop_mouseout';
			this.events.triggerEvent(eventName, {feature: evt.feature});
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
		if (feature) {
			if (feature.renderIntent == 'default')
				feature.renderIntent = 'highlighted';
			else if (!feature.renderIntent.endsWith('highlighted'))
				feature.renderIntent += '_highlighted';

			this.markerLayer.drawFeature(feature);
		}
	},

	unhighlightFeature: function (feature) {
		if (feature) {
			if (feature.renderIntent == 'highlighted')
				feature.renderIntent = 'default';
			else
				feature.renderIntent = feature.renderIntent.replace(/_highlighted/, '');

			this.markerLayer.drawFeature(feature);
		}
	},

	selectFeature: function (feature) {
		if (feature) {
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
		}
	},

	unselectFeature: function (feature) {
		if (feature) {
			if (feature.renderIntent == 'selected')
				feature.renderIntent = 'default';
			else
			{
				feature.renderIntent = feature.renderIntent.replace(/_selected/, '');
				feature.renderIntent = feature.renderIntent.replace(/selected_/, '');
			}
			this.markerLayer.drawFeature(feature);
		}
	},

	markFeature: function (feature) {
		if (feature) {
			if (feature.renderIntent == 'default')
				feature.renderIntent = 'marked';
			else if (!feature.renderIntent.startsWith('marked'))
				feature.renderIntent = 'marked_' + feature.renderIntent;
			this.markerLayer.drawFeature(feature);
		}
	},

	unmarkFeature: function (feature) {
		if (feature) {
			if (feature.renderIntent == 'marked')
				feature.renderIntent = 'default';
			else
				feature.renderIntent = feature.renderIntent.replace(/marked_/, '');

			this.markerLayer.drawFeature(feature);
		}
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
				url: "localities?bbox="+bounds.toBBOX(),
				scope: this,
				success: function (request)
				{
					json = new OpenLayers.Format.JSON();
					data = json.read(request.responseText);
					this.addStops(data.localities);
					this.loadIndicator.hide();
				}
			});
			
			var deleteFeatures = new Array();
			this.markerLayer.features.each(function (stop) {
				if (!this.map.getExtent().containsLonLat(new OpenLayers.LonLat(stop.geometry.x, stop.geometry.y))) {
					deleteFeatures.push(stop);
				}
			}, this);
			this.markerLayer.destroyFeatures(deleteFeatures);
		}
		else
		{
			this.markerLayer.destroyFeatures();
		}
	},

	/**
	 * Method: findStop
	 */
	findStop: function(id)
	{
		return this.markerLayer.features.find(function(feature) { 
			return feature.attributes.type.endsWith('locality') && feature.attributes.id == id; 
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

			stop.tags['id'] = stop.id;
			stop.tags['osm_id'] = stop.osm_id;
			stop.tags['osm_version'] = stop.osm_version;

			if ('place' in stop.tags && stop.hidden) {
				stop.type = 'deleted_osm_locality';
			}
			else if('LocalityName' in stop.tags && stop.hidden) {
				stop.type = 'deleted_nptg_locality';
			}
			else if ('place' in stop.tags && stop.match_count > 1) {
				stop.type = 'error_osm_locality';
			}
			else if ('place' in stop.tags && stop.duplicate_count > 0 ) {
				stop.type = 'error_osm_locality';
			}
			else if('place' in stop.tags && (
				[
					"city", "town", "municipality", "village", "hamlet", 
					"suburb", "island", "locality", "farm"
				].indexOf(stop.tags['place']) < 0 
				|| !('name' in stop.tags))) {
				stop.type = 'error_osm_locality';
			}
			else if('LocalityName' in stop.tags && stop.match_count > 1) {
				stop.type = 'error_nptg_locality';
			}
			else if ('place' in stop.tags && stop.match_count == 0) {
				stop.type = 'plain_osm_locality';
			}
			else if ('place' in stop.tags && stop.match_count == 1) {
				stop.type = 'matched_osm_locality';
			}
			else if ('LocalityName' in stop.tags && stop.match_count == 0) {
				stop.type = 'plain_nptg_locality';
			}	
			else if ('LocalityName' in stop.tags && stop.match_count > 0) {
				stop.type = 'matched_nptg_locality';
			}
			else {
				stop.type = ''; // This should never be called
			}

			newFeatures.push(new OpenLayers.Feature.Vector(position, stop));
		}, this);

		this.markerLayer.addFeatures(newFeatures);
	},
});
