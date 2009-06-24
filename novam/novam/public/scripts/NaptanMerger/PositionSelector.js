/**
 * Class: NaptanMerger.PositionSelector
 * A widget to select a position from a list ordered by proximity to 
 * some location.
 */
NaptanMerger.PositionSelector = Class.create(NaptanMerger.Widget, {
	
	mapControl: null,

	EVENT_TYPES: ['click', 'mouseover', 'mouseout'],

	events: null,

	list: null,
	
	initialize: function(mapControl) {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.mapControl = mapControl;
		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		var caption = new Element('h2', {'class': 'PositionSelector'});
		caption.appendChild(Text('Select Position'));

		this.list = new Element('ol', {'class': 'PositionSelector'});

		this.container.appendChild(caption);
		this.container.appendChild(this.list);
	},

	highlightWaypoint: function (feature) {
		var item = $(this._getItemId(feature.attributes.type, feature.attributes.id));
		if (item !== null)
			item.addClassName('Highlight');
	},

	unhighlightWaypoint: function (feature) {
		var item = $(this._getItemId(feature.attributes.type, feature.attributes.id));
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
			url: "positions?loc="+loc.toShortString(),
			scope: this,
			success: function (request) {
				json = new OpenLayers.Format.JSON();
				data = json.read(request.responseText);
				data.each(function (x) {
					if (x.type == 'image')
						this.mapControl.addImages([x]);
					else if (x.type == 'waypoint')
						this.mapControl.addWaypoints([x]);
				});
				this._createList(data);
			}
		});
	},

	/**
	 * Method: createList
	 * Creates the list of waypoints
	 */
	_createList: function (positions) {

		function createItem(type, id, text)
		{
			var item = new Element('li', {'id': this._getItemId(type, id)});

			if (type == 'waypoint')
			{
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
			}
			else if (type == 'image')
			{
				item.observe('mouseover', function (evt) {
					feature = this.mapControl.findImage(id);
					if (feature != undefined)
						this.events.triggerEvent('mouseover', {'feature': feature});
				}.bind(this));

				item.observe('mouseout', function (evt) {
					feature = this.mapControl.findImage(id);
					if (feature != undefined)
						this.events.triggerEvent('mouseout', {'feature': feature});
				}.bind(this));

				item.observe('click', function(evt) {
					feature = this.mapControl.findImage(id);
					if (feature != undefined)
						this.events.triggerEvent("click", {"feature": feature});
				}.bind(this));

				item.appendChild(new Element('img', {'src': 'images/show/'+id}));
			}
			
			return item;
		}

		this.list.removeChildren();
		positions.each(function(position) {
			if (position.type == 'waypoint')
				this.list.appendChild(createItem.call(this, position.type, position.id, position.name));
			else if (position.type == 'image')
				this.list.appendChild(createItem.call(this, position.type, position.id));
		}, this);
	},

	_getItemId: function (type, id) {
		return 'waypointSelector.' + this.widgetId + '.item.' + type + '_' + id;
	}
});
