/**
 * Class: NaptanMerger.LocalityList
 * A widget to show a list of localities
 */
NaptanMerger.LocalityList = Class.create(NaptanMerger.Widget, {
	
	mapControl: null,

	EVENT_TYPES: ['click', 'mouseover', 'mouseout'],

	events: null,

	localities: null,

	list: null,
	
	initialize: function(mapControl, title) {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.mapControl = mapControl;
		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		var caption = new Element('h2', {'class': 'LocalityList'});
		caption.appendChild(Text(title));

		this.list = new Element('ol', {'class': 'LocalityList'});

		this.container.appendChild(caption);
		this.container.appendChild(this.list);
	},

	highlightLocality: function (feature) {
		var item = $(this._getItemId(feature.attributes.id));
		if (item !== null)
			item.addClassName('Highlight');
	},

	unhighlightLocality: function (feature) {
		var item = $(this._getItemId(feature.attributes.id));
		if (item !== null)
			item.removeClassName('Highlight');
	},
	
	/** 
	 * Method: getLocality
	 * Querys a list of localities from the server.
	 *
	 * Parameters:
	 * url - Retrieve the list of localities from this url.
	 */
	getLocalities: function(url) {
		this._unmarkLocalities();
		var request = OpenLayers.Request.GET({
			url: url,
			scope: this,
			success: function (request) {
				json = new OpenLayers.Format.JSON();
				data = json.read(request.responseText);
				this.mapControl.addStops(data.localities);
				this._markLocalities(data.localities);
				this._createList(data.localities);
			}
		});
	},

	_markLocalities: function (localities) {
		this.localities = localities;
		if (localities) {
			this.localities.each(function(locality) {
				this.mapControl.markFeature(this.mapControl.findStop(locality.id));
			}, this);
		}
	},

	_unmarkLocalities: function () {
		if (this.localities) {
			this.localities.each(function(locality) {
				this.mapControl.unmarkFeature(this.mapControl.findStop(locality.id));
			}, this);
			this.localities = null;
		}
	},

	/**
	 * Method: createList
	 * Creates the list of localities
	 */
	_createList: function (localities) {

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

			item.observe('click', function (evt) {
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
		localities.each(function(locality) {
			this.list.appendChild(createItem.call(this, locality.id, locality.name));
		}, this);
	},

	_getItemId: function (id) {
		return 'stopSelector.' + this.widgetId + '.item.' + id;
	},
	
});
