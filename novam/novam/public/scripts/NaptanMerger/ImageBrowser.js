/**
 * Class: ImageBrowser
 */
NaptanMerger.ImageBrowser = Class.create(NaptanMerger.Widget, {

	mapControl: null,

	EVENT_TYPES: ['click', 'mouseover', 'mouseout'],

	events: null,

	image: null,
	list: null,
	feature: null,

	initialize: function(mapControl) {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.mapControl = mapControl;
		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		var caption = new Element('h2', {'class': 'ImageBrowser'});
		caption.appendChild(Text('Images'));

		this.image = new Element('img', {'class': 'ImageBrowser'});
		this.list = new Element('ol', {'class': 'ImageBrowser'});

		this.container.appendChild(caption);
		this.container.appendChild(this.image);
		this.container.appendChild(this.list);
	},

	highlightImage: function (feature) {
		var item = $(this._getItemId(feature.attributes.id));
		if (item !== null)
			item.addClassName('Highlight');
	},

	unhighlightImage: function (feature) {
		var item = $(this._getItemId(feature.attributes.id));
		if (item !== null)
			item.removeClassName('Highlight');
	},

	getImages: function(loc) {
		var request = OpenLayers.Request.GET({
			url: "images?loc="+loc.toShortString(),
			scope: this,
			success: function (request) {
				json = new OpenLayers.Format.JSON();
				data = json.read(request.responseText);
				this.mapControl.addImages(data);
				this._createList(data);
			}
		});
	},

	getImage: function(loc) {
		var request = OpenLayers.Request.GET({
			url: "images?loc="+loc.toShortString(),
			scope: this,
			success: function (request) {
				json = new OpenLayers.Format.JSON();
				data = json.read(request.responseText);
				if (data.length > 0)
				{
					this.mapControl.addImages(data.slice(0, 1));
					this.setImage(this.mapControl.findImage(data[0].id));
				}
			}
		});
	},

	setImage: function(feature) {
		if (feature)
		{
			this.image.src = 'images/show/' + feature.attributes.id;
			this.feature = feature;
			this.getImages(new OpenLayers.LonLat(feature.attributes.lon, feature.attributes.lat));
		}
		else
		{
			this.image.src = '';
			this.feature = null;
			this.list.removeChildren();
		}
	},

	setFeature: function(feature) {
		this.getImage(new OpenLayers.LonLat(feature.attributes.lon, feature.attributes.lat));
	},

	_createList: function (images) {

		function createItem(id)
		{
			var item = new Element('li', {'id': this._getItemId(id)});

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
			
			return item;
		}
		
		this.list.removeChildren();
		images.each(function(image) {
			if (this.feature.attributes.id != image.id)  // Exclude the current image
				this.list.appendChild(createItem.call(this, image.id));
		}, this);

		this.list.scrollTop = 0;
	},

	_getItemId: function (id) {
		return 'imageViewer.' + this.widgetId + '.item.' + id;
	}
});
