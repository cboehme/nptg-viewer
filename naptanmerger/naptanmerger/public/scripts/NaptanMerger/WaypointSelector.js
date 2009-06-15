/**
 * Class: NaptanMerger.WaypointSelector
 * A widget to select a waypoint from a list ordered by proximity to 
 * some location.
 */
NaptanMerger.WaypointSelector = Class.create(NaptanMerger.Widget, {
	
	mapControl: null,

	EVENT_TYPES: ['click', 'mouseover', 'mouseout'],

	events: null,

	list: null,
	
	initialize: function(mapControl) {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.mapControl = mapControl;
		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		var caption = new Element('h2', {'class': 'WaypointSelector'});
		caption.appendChild(Text('Select Waypoint'));

		this.list = new Element('ol', {'class': 'WaypointSelector'});

		this.container.appendChild(caption);
		this.container.appendChild(this.list);
	},

	highlightWaypoint: function (feature) {
		var item = $(this._getItemId(feature.attributes.id));
		if (item !== null)
			item.addClassName('Highlight');
	},

	unhighlightWaypoint: function (feature) {
		var item = $(this._getItemId(feature.attributes.id));
		if (item !== null)
			item.removeClassName('Highlight');
	},

	/** 
	 * Method: getWaypoints
	 * Querys a list of stops from the server.
	 *
	 * Parameters:
	 * loc - {OpenLayers.LatLon} Location around which waypoints 
	 *     should be retrieved.
	 */
	getWaypoints: function(loc) {
		var request = OpenLayers.Request.GET({
			url: "waypoints?loc="+loc.toShortString(),
			scope: this,
			success: function (request) {
				json = new OpenLayers.Format.JSON();
				data = json.read(request.responseText);
				this.mapControl.addWaypoints(data);
				this._createList(data);
			}
		});
	},

	/**
	 * Method: createList
	 * Creates the list of waypoints
	 */
	_createList: function (waypoints) {

		function createItem(id, text)
		{
			var item = new Element('li', {'id': this._getItemId(id)});

			item.observe('mouseover', function (evt) {
				feature = this.mapControl.findWaypoint(id);
				if (feature != undefined)
					this.events.triggerEvent('mouseover', {'feature': feature});
			}.bind(this));

			item.observe('mouseout', function (evt) {
				feature = this.mapControl.findWaypoint(id);
				if (feature != undefined)
					this.events.triggerEvent('mouseout', {'feature': feature});
			}.bind(this));

			item.observe('click', function(evt) {
				feature = this.mapControl.findWaypoint(id);
				if (feature != undefined)
					this.events.triggerEvent("click", {"feature": feature});
			}.bind(this));

			item.appendChild(Text(text));
			
			return item;
		}

		this.list.removeChildren();
		waypoints.each(function(waypoint) {
			this.list.appendChild(createItem.call(this, waypoint.id, waypoint.name));
		}, this);
	},

	_getItemId: function (id) {
		return 'waypointSelector.' + this.widgetId + '.item.' + id;
	}
});
