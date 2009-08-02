/**
 * Class: NaptanMerger.LocalityViewer
 * A widget to show a locality and allow to hide/unhide it.
 */
NaptanMerger.LocalityViewer = Class.create(NaptanMerger.Widget, {
	
	list: null,

	initialize: function() {
		NaptanMerger.Widget.prototype.initialize.call(this);

		var caption = new Element('h2', {'class': 'LocalityViewer'});
		caption.appendChild(Text('Locality'));

		this.list = new Element('dl', {'class': 'LocalityViewer'});

		this.container.appendChild(caption);
		this.container.appendChild(this.list);

		this.setLocality(null);
	},

	setLocality: function(feature) {

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
			appendItem.call(this, 'No Locality Selected', '');
		else
		{
			var tags = [];
			for(tag in feature.attributes.tags)
				tags.push(tag);
			tags.sort();
			for (var i = 0; i < tags.length; ++i)
			{
				tag = tags[i];
				appendItem.call(this, tag+': ', feature.attributes.tags[tag]);
			}
		}
	}
});
