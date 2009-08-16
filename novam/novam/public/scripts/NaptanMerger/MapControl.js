/**
 * Class: NaptanMerger.MapControl
 */
NaptanMerger.MapControl = Class.create({

	EPSG4326: new OpenLayers.Projection("EPSG:4326"),
	EPSG900913: new OpenLayers.Projection("EPSG:900913"),

	HIGHLIGHTED: "_highlighted",
	UNHIGHLIGHTED: "",
	SELECTED: "_selected",
	UNSELECTED: "",
	MARKED: "_marked",
	UNMARKED: "",

	model: null,
	map: null,
	marker_layer: null,
	feature_control: null,
	load_indicator: null,

	initialize: function(container, model) {

		this.model = model;
		this.model.events.register("locality_added", this, this.locality_added);
		this.model.events.register("locality_removed", this, this.locality_removed);
		this.model.events.register("locality_updated", this, this.locality_updated);
		this.model.events.register("locality_selected", this, this.locality_selected);
		this.model.events.register("locality_unselected", this, this.locality_unselected);
		this.model.events.register("locality_highlighted", this, this.locality_highlighted);
		this.model.events.register("locality_unhighlighted", this, this.locality_unhighlighted);
		this.model.events.register("locality_marked", this, this.locality_marked);
		this.model.events.register("locality_unmarked", this, this.locality_unmarked);

		this.map = new OpenLayers.Map(container, {
			controls: [
				new OpenLayers.Control.Navigation(),
				new OpenLayers.Control.PanZoomBar()
			],
			units: 'm',
			projection: this.EPSG900913,
			displayProjection: this.EPSG4326
		});

		// Create load indicator:
		this.load_indicator = new Element("div", {"class": "MapLoadIndicator"});
		this.load_indicator.appendChild(Text("Loading ..."));
		$(container).appendChild(this.load_indicator);
		this.load_indicator.hide();
		
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
				externalGraphic: '${type}${selected}${marked}${highlighted}.png',
				cursor: 'pointer'
			})
		});

		var opacityLookup = {
			"deleted_nptg_locality": {graphicOpacity: 0.6},
			"deleted_osm_locality": {graphicOpacity: 0.6},
			"matched_nptg_locality": {graphicOpacity: 0.6},
			"matched_osm_locality": {},
			"plain_nptg_locality": {},
			"plain_osm_locality": {},
			"error_nptg_locality": {},
			"error_osm_locality": {}
		};
		styleMap.addUniqueValueRules("default", "type", opacityLookup);

		var sizeLookup = {
			"_highlighted": {
				graphicHeight: 22,
				graphicWidth: 22,
				graphicXOffset: -11,
				graphicYOffset: -11,
			},
			"": {}
		};
		styleMap.addUniqueValueRules("default", "highlighted", sizeLookup);

		var pointerLookup = {
			"_selected": {cursor: ''},
			"": {}
		};
		styleMap.addUniqueValueRules("default", "selected", pointerLookup);

		// Create the marker layer:
		this.marker_layer = new OpenLayers.Layer.Vector('Markers', {styleMap: styleMap});
		this.map.addLayer(this.marker_layer);

		this.map.events.register('moveend', this, this.save_map_location);
		this.map.events.register('moveend', this, this.get_localities);

		// Add control for the marker layer:
		this.feature_control = new NaptanMerger.FeatureControl(this.marker_layer);
		this.map.addControl(this.feature_control);
		this.feature_control.activate();

		// Register event handlers for features:
		this.feature_control.events.register("click", this, function (evt) {
			this.model.select_locality(evt.feature.attributes.id);
		});

		this.feature_control.events.register("clickout", this, function (evt) {
			this.model.unselect_locality();
		});

		this.feature_control.events.register("mouseover", this, function (evt) {
			this.model.highlight_locality(evt.feature.attributes.id);
		});

		this.feature_control.events.register("mouseout", this, function (evt) {
			this.model.unhighlight_locality();
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
		this.map.setCenter(loc.transform(
			this.EPSG4326, this.map.getProjectionObject()), zoom);
	},

	destroy: function() {
		this.markerControl = null;
		this.marker_layer = null;
		this.map = null;
		this.model = null;
	},

	save_map_location: function() {
		var loc = this.map.getCenter().clone().transform(
			this.map.getProjectionObject(), this.EPSG4326);
		var zoom = this.map.getZoom();

		var decimals = Math.pow(10, Math.floor(zoom/3));

		loc.lat = Math.round(loc.lat * decimals) / decimals;
		loc.lon = Math.round(loc.lon * decimals) / decimals;

		setCookie("map_location", loc.lat+":"+loc.lon+":"+zoom);
	},

	get_localities: function() {
		if (this.map.getZoom() > 11)
		{
			var bounds = this.map.getExtent().clone();
			bounds = bounds.transform(this.EPSG900913, this.EPSG4326);

			this.load_indicator.show();

			var request = OpenLayers.Request.GET({
				url: "localities?bbox="+bounds.toBBOX(),
				scope: this,
				success: function(request) {
					json = new OpenLayers.Format.JSON();
					data = json.read(request.responseText);
					data.localities.each(function (locality) {
						this.model.add_locality(locality);
					}, this);
					this.load_indicator.hide();
				}
			});
		
			// Remove localities which are outside the viewport:
			var removeFeatures = Array();
			this.marker_layer.features.each(function(locality) {
				if (!this.map.getExtent().containsLonLat(
					new OpenLayers.LonLat(locality.geometry.x, locality.geometry.y))
					&& !this.model.is_locality_selected(locality.attributes.id)
					&& !this.model.is_locality_highlighted(locality.attributes.id)
					&& !this.model.is_locality_marked(locality.attributes.id)) {
					removeFeatures.push(locality.attributes.id);
				}
			}, this);
			removeFeatures.each(this.model.remove_locality, this.model);
		} else {
			this.model.clear_localities();
		}
	},

	locality_added: function(locality) {

		var position = new OpenLayers.Geometry.Point(locality.lon, locality.lat);
		position = position.transform(this.EPSG4326, this.EPSG900913);

		var attributes = new Object();
		attributes.id = locality.id;
		attributes.type = get_locality_type(locality);
		attributes.highlighted = this.UNHIGHLIGHTED;
		attributes.selected = this.UNSELECTED;
		attributes.marked = this.UNMARKED;

		this.marker_layer.addFeatures([new OpenLayers.Feature.Vector(position, attributes)]);
	},

	locality_removed: function(locality) {
		this.marker_layer.destroyFeatures([this._find_locality(locality.id)]);
	},

	locality_updated: function(locality) {
		var feature = this._find_locality(locality.id);
		feature.attributes.type = get_locality_type(locality);
		this.marker_layer.drawFeature(feature);
	},
	
	locality_highlighted: function(locality) {
		var feature = this._find_locality(locality.id);
		feature.attributes.highlighted = this.HIGHLIGHTED;
		this.marker_layer.drawFeature(feature);
	},

	locality_unhighlighted: function(locality) {
		var feature = this._find_locality(locality.id);
		feature.attributes.highlighted = this.UNHIGHLIGHTED;
		this.marker_layer.drawFeature(feature);
	},

	locality_selected: function(locality) {
		var feature = this._find_locality(locality.id);
		feature.attributes.selected = this.SELECTED;
		this.marker_layer.drawFeature(feature);
	},

	locality_unselected: function(locality) {
		var feature = this._find_locality(locality.id);
		feature.attributes.selected = this.UNSELECTED;
		this.marker_layer.drawFeature(feature);
	},

	locality_marked: function(locality) {
		var feature = this._find_locality(locality.id);
		feature.attributes.marked = this.MARKED;
		this.marker_layer.drawFeature(feature);
	},

	locality_unmarked: function(locality) {
		var feature = this._find_locality(locality.id);
		feature.attributes.marked = this.UNMARKED;
		this.marker_layer.drawFeature(feature);
	},

	_find_locality: function(id)
	{
		return this.marker_layer.features.find(function(feature) { 
			return feature.attributes.id == id; 
		});
	}
});
