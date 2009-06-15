/**
 * Class: NaptanMerger.MergeDialog
 * A widget to show a bus stop and allow merging it.
 */
NaptanMerger.MergeDialog = Class.create(NaptanMerger.Widget, {
	
	EVENT_TYPES: ['merge', 'cancelled'],

	events: null,
	
	list: null,
	mergeButton: null,
	cancelButton: null,

	initialize: function() {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		var caption = new Element('h2', {'class': 'MergeDialog'});
		caption.appendChild(Text('Merge Bus Stops'));

		this.list = new Element('dl', {'class': 'MergeDialog'});

		this.mergeButton = new Element('button', {
			'class': 'MergeDialog OkButton',
			'type': 'button'
		});
		this.mergeButton.observe('click', function (evt) {
			this.events.triggerEvent('merge');
		}.bind(this));
		this.mergeButton.appendChild(Text("Merge"));

		this.cancelButton = new Element('button', {
			'class': 'MergeDialog CancelButton',
			'type': 'button'
		});
		this.cancelButton.appendChild(Text("Cancel"));
		this.cancelButton.observe('click', function (evt) {
			this.events.triggerEvent('cancelled');
		}.bind(this));

		this.container.appendChild(caption);
		this.container.appendChild(this.list);
		this.container.appendChild(this.mergeButton);
		this.container.appendChild(this.cancelButton);

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
			appendItem.call(this, 'No stop selected', '');
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
