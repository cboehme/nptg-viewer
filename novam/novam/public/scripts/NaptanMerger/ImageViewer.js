/**
 * Class: NaptanMerger.ImageViewer
 * A widget to show an image.
 */
NaptanMerger.ImageViewer = Class.create(NaptanMerger.Widget, {

	image: null,
	
	initialize: function() {
		NaptanMerger.Widget.prototype.initialize.call(this);

		var caption = new Element('h2', {'class': 'ImageViewer'});
		caption.appendChild(Text('Image'));

		var div = new Element('div', {'class': 'ImageViewer'});

		this.image = new Element('img');
		div.appendChild(this.image);

		this.container.appendChild(caption);
		this.container.appendChild(div);

		this.setImage(null);
	},

	setImage: function(feature) {
		
		if (!feature)
			this.image.src = '';
		else
			this.image.src = 'images/show/' + feature.attributes.id;
	}
});
