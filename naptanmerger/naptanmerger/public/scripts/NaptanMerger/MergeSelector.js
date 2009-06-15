/**
 * Class: NaptanMerger.MergeSelector
 * A widget to select a stop from a list ordered by similarity
 * with a given stop.
 */
NaptanMerger.MergeSelector = Class.create(NaptanMerger.Widget, {

	mapControl: null,

	EVENT_TYPES: ['click', 'mouseover', 'mouseout'],

	events: null,

	list: null,
	
	/**
	 * Constructor: NaptanMerger.MergeSelector
	 * Create a MergeSelector widget.
	 */
	initialize: function(mapControl) {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.mapControl = mapControl;
		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		var caption = new Element('h2', {'class': 'MergeSelector'});
		caption.appendChild(Text('Similar Bus Stops'));

		this.list = new Element('ol', {'class': 'MergeSelector'});

		this.container.appendChild(caption);
		this.container.appendChild(this.list);
	},

	highlightStop: function (feature) {
		var item = $(this._getItemId(feature.attributes.id));
		if (item !== null)
			item.addClassName('Highlight');
	},

	unhighlightStop: function (feature) {
		var item = $(this._getItemId(feature.attributes.id));
		if (item !== null)
			item.removeClassName('Highlight');
	},
	
	/** 
	 * Method: getStops
	 * Querys a list of stops from the server.
	 *
	 * Parameters:
	 * feature - {OpenLayers.Feature} a bus stop feature.
	 */
	getStops: function(feature) {
		var request = OpenLayers.Request.GET({
			url: "osmdata?stop="+feature.attributes.id,
			scope: this,
			success: function (request) {
				json = new OpenLayers.Format.JSON();
				data = json.read(request.responseText);
				this.mapControl.addStops(data);
				this._createList(data);
			}
		});
	},

	/**
	 * Method: createList
	 * Creates the list of stops
	 */
	_createList: function (stops) {

		function createItem(id, text)
		{
			var item = new Element('li', {'id': this._getItemId(id)});

			item.observe('mouseover', function (evt) {
				feature = this.mapControl.findStop(id);
				if (feature != undefined)
					this.events.triggerEvent('mouseover', {'feature': feature});
			}.bind(this));

			item.observe('mouseout', function (evt) {
				feature = this.mapControl.findStop(id);
				if (feature != undefined)
					this.events.triggerEvent('mouseout', {'feature': feature});
			}.bind(this));

			item.observe('click', function(evt) {
				feature = this.mapControl.findStop(id);
				if (feature != undefined)
					this.events.triggerEvent('click', {'feature': feature});
			}.bind(this));

			if (text != '')
				item.appendChild(Text(text));
			else
			{
				i = new Element('i');
				i.appendChild(Text('Unnamed'));
				item.appendChild(i);
			}
			
			return item;
		}

		this.list.removeChildren();
		stops.each(function(stop) {
			this.list.appendChild(createItem.call(this, stop.id, this._getStopName(stop)));
		}, this);
	},

	_getItemId: function (id) {
		return 'mergeSelector.' + this.widgetId + '.item.' + id;
	},
	
	/* TODO: This function should be provided by the stop */
	_getStopName: function (stop) {
		var name = '';

		if ('name' in stop.tags)
			name = stop.tags["name"];
		else{
			if ('naptan:Street' in stop.tags)
				name = stop.tags['naptan:Street'];
		
			if ('naptan:CommonName' in stop.tags)
			{
				if (name != '')
					name += ': ';
				name += stop.tags['naptan:CommonName'];
			}
		}

		if (name != '' && ('naptan:Indicator' in stop.tags))
			name += ' ('+stop.tags['naptan:Indicator']+')';

		return name;
	}
});
