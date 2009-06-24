NaptanMerger.FeatureControl = OpenLayers.Class(OpenLayers.Control, {

	layer: null,
	handlers: null,
	over: false,
	feature: null,
	lastPixel: null,
	draggableFeatures: null,

	EVENT_TYPES: ['click', 'clickout', 'mouseover', 'mouseout',
		'drag_start', 'drag_done', 'drag_cancelled'],

	initialize: function (layer, options) {
		this.EVENT_TYPES =
			NaptanMerger.FeatureControl.prototype.EVENT_TYPES.concat(
			OpenLayers.Control.prototype.EVENT_TYPES
		);

		OpenLayers.Control.prototype.initialize.apply(this, [options]);

		this.layer = layer;

		var featureCallbacks = {
			click: this.onClick,
			clickout: this.onClickout,
			over: this.onMouseOver,
			out: this.onMouseOut
		};

		var dragCallbacks = {
			down: this.onFeatureDown,
			move: this.onFeatureMove,
			done: this.onDragDone,
			up: this.onFeatureUp,
			out: this.onDragOut
		};

		this.handlers = {
			feature: new OpenLayers.Handler.Feature(this, this.layer, featureCallbacks),
			drag: new OpenLayers.Handler.Drag(this, dragCallbacks)
		};

		this.draggableFeatures = new Array();
	},

	destroy: function () {
		this.layer = null;
		OpenLayers.Control.prototype.destroy.apply(this, arguments);
	},

	activate: function () {
		this.handlers.feature.activate();
		return OpenLayers.Control.prototype.activate.apply(this, arguments);
	},

	deactivate: function () {
		this.handlers.feature.deactivate();
		this.handlers.drag.deactivate();
		this.over = false;
		this.feature = null;
		this.lastPixel = null;
		return OpenLayers.Control.prototype.deactivate.apply(this, arguments);
	},

	activateDragging: function (feature) {
		if (this.draggableFeatures.indexOf(feature) == -1)
		{
			this.draggableFeatures.push(feature);
			if (this.over && this.feature.id == feature.id)
				this.handlers.drag.activate();
		}
	},

	deactivateDragging: function (feature) {
		var i = this.draggableFeatures.indexOf(feature);
		if (i != -1)
		{
			this.draggableFeatures.splice(i, 1);
			if (this.over && this.feature.id == feature.id)
				this.handlers.drag.deactivate();
		}
	},

	onClick: function (feature) {
		this.events.triggerEvent("click", {
			feature: feature, 
			shiftKey: this.handlers.feature.evt.shiftKey,
			ctrlKey: this.handlers.feature.evt.ctrlKey
		});
		this.handlers.feature.evt.stop();
	},

	onClickout: function (feature) {
		this.events.triggerEvent("clickout", {feature: feature});
	},

	onMouseOver: function (feature) {
        if (!this.handlers.drag.dragging) 
		{
			this.events.triggerEvent("mouseover", {feature: feature});

			this.feature = feature;
			if (this.draggableFeatures.indexOf(feature) != -1)
				this.handlers.drag.activate();
			this.over = true;
		}
		else 
			this.over = this.feature.id == feature.id;
	},

	onMouseOut: function (feature) {
		if (!this.handlers.drag.dragging) 
		{
			this.events.triggerEvent("mouseout", {feature: feature});

			this.over = false;
			this.handlers.drag.deactivate();
			this.feature = null;
		} 
		else 
		{
			if(this.feature.id == feature.id)
				this.over = false;
		}
	},

	onFeatureDown: function (pixel) {
		this.lastPixel = pixel;
		this.events.triggerEvent('drag_start', {feature: this.feature});
	},

	onFeatureMove: function (pixel) {
		var res = this.map.getResolution();
		this.feature.geometry.move(res * (pixel.x - this.lastPixel.x),
		                           res * (this.lastPixel.y - pixel.y));
		this.layer.drawFeature(this.feature);
		this.lastPixel = pixel;
	},

	onDragDone: function (pixel) {
		this.events.triggerEvent('drag_done', {feature: this.feature});
	},

	onFeatureUp: function (pixel) {
		if (!this.over)
			this.onDragOut(pixel);
	},

	onDragOut: function (pixel) {
		this.events.triggerEvent('drag_cancelled', {feature: this.feature});

		this.handlers.drag.deactivate();
		this.over = false;
		this.feature = null;
		this.lastPixel = null;
	},

	setMap: function (map) {
		this.handlers.feature.setMap(map);
		this.handlers.drag.setMap(map);
		OpenLayers.Control.prototype.setMap.apply(this, arguments);
	},
	
	CLASS_NAME: "OpenLayers.Control.SelectFeature"
});
