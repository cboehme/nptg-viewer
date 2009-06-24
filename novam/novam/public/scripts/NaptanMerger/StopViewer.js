/**
 * Class: NaptanMerger.StopViewer
 * A widget to show a bus stop and allow merging it.
 */
NaptanMerger.StopViewer = Class.create(NaptanMerger.Widget, {
	
	list: null,

	initialize: function() {
		NaptanMerger.Widget.prototype.initialize.call(this);

		var caption = new Element('h2', {'class': 'StopViewer'});
		caption.appendChild(Text('Bus Stop'));

		this.list = new Element('dl', {'class': 'StopViewer'});

		this.container.appendChild(caption);
		this.container.appendChild(this.list);

		this.setStop(null);
	},

	setStop: function(feature) {

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
			appendItem.call(this, 'No Stop Selected', '');
		else
		{
			for (tag in feature.attributes.tags)
			{
				if (tag.substring(0,7) == "naptan:")
					shortenedTag = tag.substring(7);
				else
					shortenedTag = tag;
				appendItem.call(this, shortenedTag+': ', feature.attributes.tags[tag]);
			}
		}
	}
});
