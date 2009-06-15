/**
 * Class: NaptanMerger.WaypointViewer
 * A widget to show the properties of a waypoint.
 */
NaptanMerger.WaypointViewer = Class.create(NaptanMerger.Widget, {

	list: null,
	
	initialize: function() {
		NaptanMerger.Widget.prototype.initialize.call(this);

		var caption = new Element('h2', {'class': 'WaypointViewer'});
		caption.appendChild(Text('Waypoint'));

		this.list = new Element('dl', {'class': 'WaypointViewer'});

		this.container.appendChild(caption);
		this.container.appendChild(this.list);

		this.setWaypoint(null);
	},

	setWaypoint: function(feature) {

		function appendItem(key, value) {
			var dt = new Element('dt');
			var dd = new Element('dd');

			dt.appendChild(Text(key));
			dd.appendChild(Text(value));

			this.list.appendChild(dt);
			this.list.appendChild(dd);
		}

		this.list.removeChildren();
		if (feature === null)
			appendItem.call(this, 'No waypoint selected.', '');
		else
		{
			appendItem.call(this, 'Name: ', feature.attributes.name);
			appendItem.call(this, 'Position: ', feature.attributes.lat + ", " + feature.attributes.lon);
		}
	}
});
