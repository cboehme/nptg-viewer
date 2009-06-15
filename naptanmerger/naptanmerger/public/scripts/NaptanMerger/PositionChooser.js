/**
 * Class: NaptanMerger.PositionChooser
 * A widget to mark a position in a list ordered by proximity to 
 * some location.
 */
NaptanMerger.PositionChooser = Class.create(NaptanMerger.Widget, {

	mapControl: null,

	EVENT_TYPES: ['change', 'mouseover', 'mouseout'],

	events: null,

	list: null,

	requesting: null,
	doChoosePosition: null,
	baseLocation: null,
	locations: null,
	
	initialize: function(mapControl) {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.mapControl = mapControl;
		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		var caption = new Element('h2', {'class': 'PositionChooser'});
		caption.appendChild(Text('Choose Position'));

		this.list = new Element('ol', {'class': 'PositionChooser'});

		this.requesting = false;
		this.doChoosePosition = undefined;
		this.locations = new Array();

		this.container.appendChild(caption);
		this.container.appendChild(this.list);
	},

	highlightPosition: function (feature) {
		if (feature === null)
			$(this._getItemId('text', 0)).addClassName('Highlight');
		else
		{
			if(feature.attributes.type == 'waypoint')
				type = 'text';
			else
				type = 'image';
			var item = $(this._getItemId(type, feature.attributes.id));
			if (item !== null)
				item.addClassName('Highlight');
		}
	},

	unhighlightPosition: function (feature) {
		if (feature === null)
			$(this._getItemId('text', 0)).removeClassName('Highlight');
		else
		{
			if(feature.attributes.type == 'waypoint')
				type = 'text';
			else
				type = 'image';
			var item = $(this._getItemId(type, feature.attributes.id));
			if (item !== null)
				item.removeClassName('Highlight');
		}
	},

	choosePosition: function (feature) {
		if (this.requesting)
			this.doChoosePosition = feature;
		else
		{
			if (!feature)
			{
				$(this._getRadioId('text', 0)).checked = true;
				this.events.triggerEvent('change', {'feature': null});
			}
			else
			{
				var type;
				if (feature.attributes.type == 'waypoint')
					type = 'text';
				else
					type = 'image';

				var input = $(this._getRadioId(type, feature.attributes.id));
				if (!input)
				{
					// If the selected feature is not in the list yet then add it:
					var dist = Math.sqrt(Math.pow(this.baseLocation.lon-feature.attributes.lon, 2) 
						+ Math.pow(this.baseLocation.lat-feature.attributes.lat, 2));
					var i = -1;
					this.locations.each(function (l) {
						if(l.dist <= dist)
							++i;
					});
					
					var el = null;
					if (feature.attributes.type == 'waypoint')
						el = this._createItem('text', feature.attributes.id, feature.attributes.name);
					else
						el = this._createItem('image', feature.attributes.id);
					this.list.insertAfter(el, this.locations[i].el);

					this.locations.splice(i+1, 0, {dist: dist, el: el});

					input = $(this._getRadioId(type, feature.attributes.id));
				}
				input.checked = true;
				this.events.triggerEvent('change', {'feature': feature});
			}
		}
	},
	
	/** 
	 * Method: getPositions
	 * Querys a list of positions from the server.
	 *
	 * Parameters:
	 * loc - {OpenLayers.LatLon} Location around which positions 
	 *     should be retrieved.
	 */
	getPositions: function(loc) {
		this.baseLocation = loc;
		this.requesting = true;
		var request = OpenLayers.Request.GET({
			url: "positions?loc="+loc.toShortString(),
			scope: this,
			success: function (request) {
				this.requesting = false;
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

	_createItem: function (type, id, text) {
		var input = new Element('input', {
			'type': 'radio',
			'name': 'positions',
			'value': id,
			'id': this._getRadioId(type, id)
		});

		if (id == 0)
		{
			input.observe('change', function(evt) {
				this.events.triggerEvent('change', {'feature': null});
			}.bind(this));
		}
		else
		{
			input.observe('change', function(evt) {
				var feature = this.mapControl.findWaypoint(id);
				if (feature != undefined)
					this.events.triggerEvent('change', {'feature': feature});
			}.bind(this));
		}

		var label = new Element('label', {'htmlFor': this._getRadioId(type, id)});
		if (type == 'text')
			label.appendChild(Text(text));
		else if (type == 'image')
			label.appendChild(new Element('img', {'src': 'images/show/'+id}))
		
		var item = new Element('li', {'id': this._getItemId(type, id)});

		if (id == 0)
		{
			item.observe('mouseover', function (evt) {
				this.events.triggerEvent('mouseover', {'feature': null});
			}.bind(this));

			item.observe('mouseout', function (evt) {
				this.events.triggerEvent('mouseout', {'feature': null});
			}.bind(this));
			
			// Clicking anywhere on a list entry should select this entry:
			item.observe('click', function(evt) {
				$(this._getRadioId('text', 0)).checked = true;
				this.events.triggerEvent('change', {'feature': null});
			}.bind(this));
		}
		else 
		{ 
			if (type == 'text')
			{
				item.observe('mouseover', function (evt) {
					var feature = this.mapControl.findWaypoint(id);
					if (feature != undefined)
						this.events.triggerEvent('mouseover', {'feature': feature});
				}.bind(this));

				item.observe('mouseout', function (evt) {
					var feature = this.mapControl.findWaypoint(id);
					if (feature != undefined)
						this.events.triggerEvent('mouseout', {'feature': feature});
				}.bind(this));

				// Clicking anywhere on a list entry should select this entry:
				item.observe('click', function(evt) {
					$(this._getRadioId('text', id)).checked = true;
					var feature = this.mapControl.findWaypoint(id);
					if (feature != undefined)
						this.events.triggerEvent('change', {'feature': feature});
				}.bind(this));
			}
			else if (type == 'image')
			{
				item.observe('mouseover', function (evt) {
					var feature = this.mapControl.findImage(id);
					if (feature != undefined)
						this.events.triggerEvent('mouseover', {'feature': feature});
				}.bind(this));

				item.observe('mouseout', function (evt) {
					var feature = this.mapControl.findImage(id);
					if (feature != undefined)
						this.events.triggerEvent('mouseout', {'feature': feature});
				}.bind(this));

				// Clicking anywhere on a list entry should select this entry:
				item.observe('click', function(evt) {
					$(this._getRadioId('image', id)).checked = true;
					var feature = this.mapControl.findImage(id);
					if (feature != undefined)
						this.events.triggerEvent('change', {'feature': feature});
				}.bind(this));
			}
		}

		item.appendChild(input);
		item.appendChild(Text(' '));
		item.appendChild(label);
		
		return item;
	},

	/**
	 * Method: createList
	 * Creates the list of positions
	 */
	_createList: function (positions) {

		this.list.removeChildren();
		this.locations = new Array();

		// Create a dummy entry which represents the current position of
		// the stop:
		var el = this._createItem('text', 0, 'Current position');
		this.list.appendChild(el);
		this.locations.push({dist: 0, el: el});
		
		positions.each(function (position) {
			if (position.type == 'waypoint')
				el = this._createItem('text', position.id, position.name);
			else
				el = this._createItem('image', position.id);
			this.list.appendChild(el);
			this.locations.push({
				dist: Math.sqrt(Math.pow(this.baseLocation.lon-position.lon, 2) 
					+ Math.pow(this.baseLocation.lat-position.lat, 2)),
				el: el
			});
		}, this);

		if (this.doChoosePosition !== undefined)
		{
			this.choosePosition(this.doChoosePosition);
			this.doChoosePosition = undefined;
		}
	},

	_getItemId: function (type, id) {
		return 'positionChooser.' + this.widgetId + '.item.' + type + "_" + id;
	},

	_getRadioId: function (type, id) {
		return 'positionChooser.' + this.widgetId + '.radio.' + type + "_" + id;
	}
});
