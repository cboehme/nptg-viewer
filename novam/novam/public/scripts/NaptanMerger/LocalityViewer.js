/**
 * Class: NaptanMerger.LocalityViewer
 * A widget to show a locality and allow to hide/unhide it.
 */
NaptanMerger.LocalityViewer = Class.create(NaptanMerger.Widget, {
	
	model: null,
	details: null,
	comment: null,
	commentLabel: null,
	commentInput: null,
	toggleButton: null,

	initialize: function(model) {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.model = model;
		this.model.events.register("locality_highlighted", this, this.locality_highlighted);
		this.model.events.register("locality_unhighlighted", this, this.locality_unhighlighted);
		this.model.events.register("locality_selected", this, this.locality_selected);
		this.model.events.register("locality_unselected", this, this.locality_unselected);
		this.model.events.register("locality_updated", this, this.locality_updated);

		var caption = new Element("h2", {"class": "LocalityViewer"});
		caption.appendChild(Text("Locality Details"));
	
		this.details = new Element("div", {"class": "LocalityViewerDetails"});

		this.commentLabel = new Element("label", {"for": "comment_input_"+this.widgetId});
		this.commentLabel.appendChild(Text("Reason for hiding"));

		this.commentInput = new Element("input", {"type": "text", "id": "comment_input_"+this.widgetId});
		this.commentInput.observe("focus", function(evt) {
			this.commentLabel.hide();
		}.bind(this));
		this.commentInput.observe("blur", function(evt) {
			if (this.commentInput.value == "") {
				this.commentLabel.show();
			}
		}.bind(this));
				
		this.comment = new Element("div", {"class": "LocalityViewerComment"});
		this.comment.appendChild(this.commentLabel);
		this.comment.appendChild(this.commentInput);

		this.toggleButton = new Element("button", {
			"class": "LocalityViewer",
			"type": "button"
		});
		this.toggleButton.observe("click", function(evt) {
			if (this.model.selected_locality.hidden !== null) {
				this._unhide_locality();
			} else {
				this._hide_locality();
			}
		}.bind(this));

		this.container.appendChild(caption);
		this.container.appendChild(this.details);
		this.container.appendChild(this.comment);
		this.container.appendChild(this.toggleButton);

		this.set_locality(null);
	},

	set_locality: function(locality) {

		function append_item(list, key, value) {
			var dt = new Element("dt");
			var dd = new Element("dd");

			dt.appendChild(Text(key));
			dd.appendChild(Text(value));

			list.appendChild(dt);
			list.appendChild(dd);
		}
		
		this.details.removeChildren();
		if (locality === null) {
			this.details.appendChild(Text("No locality selected"));
			this.toggleButton.hide();
			this.comment.hide();
		} else {
			var caption_text = "Unnamed";
			var type_text = "";
			if ("name" in locality.tags) {
				caption_text = locality.tags["name"];
				if ("place" in locality.tags) {
					type_text = locality.tags["place"].capitalize();
				}
			} else if ("LocalityName" in locality.tags) {
				caption_text = locality.tags["LocalityName"];
				type_text = locality.tags["SourceLocalityType"];
			}
			var element = new Element("h3");
			element.appendChild(new Element("img", {"src": get_locality_type(locality) + "_small.png"}));
			element.appendChild(Text(caption_text));
			this.details.appendChild(element);

			element = new Element("p");
			element.appendChild(Text(type_text));
			this.details.appendChild(element);

			if (locality.hidden != null) {
				element = new Element("p", {"class": "HiddenLocality"});
				var b = new Element("b");
				b.appendChild(Text("This locality has been hidden:"));
				element.appendChild(b);
				element.appendChild(new Element("br"));
				var i = new Element("i");
				element.appendChild(i);
				if (locality.comment != "") {
					i.appendChild(Text(locality.comment));
				} else {
					i.appendChild(Text("No comment"));
				}
				this.details.appendChild(element);
			}
	
			element = new Element("h3");
			element.appendChild(new Element("img", {"src": "tag.png"}));
			element.appendChild(Text("Detailed Tag List"));
			this.details.appendChild(element);

			var list = new Element("dl");
			this.details.appendChild(list);

			var tags = [];
			for (tag in locality.tags) {
				tags.push(tag);
			}
			tags.sort();
			for (var i = 0; i < tags.length; ++i) {
				tag = tags[i];
				append_item.call(this, list, tag+": ", locality.tags[tag]);
			}

			this.toggleButton.show();
			if (locality.hidden != null) {
				this.toggleButton.replaceChildren(Text("Unhide"));
				this.comment.hide();
			} else {
				this.toggleButton.replaceChildren(Text("Hide"));
				this.commentInput.value = "";
				this.commentLabel.show();
				this.comment.show();
			}
		}
	},

	locality_highlighted: function(locality) {
		this.set_locality(locality);
	},

	locality_unhighlighted: function(locality) {
		this.set_locality(this.model.selected_locality);
	},

	locality_selected: function(locality) {
		this.set_locality(locality);
	},

	locality_unselected: function(locality) {
		this.set_locality(this.model.highlighted_locality);
	},

	locality_updated: function(locality) {
		if ((this.model.selected_locality !== null 
			&& this.model.selected_locality.id == locality.id)
			|| (this.model.highlighted_locality !== null
			&& this.model.highlighted_locality.id == locality.id))
		{
			this.set_locality(locality);
		}
	},

	_hide_locality: function() {
		var form = "comment=" + encodeURIComponent(this.commentInput.value) + "\r\n";
		var request = OpenLayers.Request.POST({
			url: "localities/hide/"+this.model.selected_locality.id,
			data: form,
			headers: {"Content-Type": "application/x-www-form-urlencoded"},
			scope: this,
			success: function (request) {
				json = new OpenLayers.Format.JSON();
				data = json.read(request.responseText);
				if (data.localities != null) {
					data.localities.each(function (locality) {
						this.model.update_locality(locality);
					}, this);
				}
			},
			failure: function (request) {
			}
		});
	},

	_unhide_locality: function() {
		var form = "";
		var request = OpenLayers.Request.POST({
			url: "localities/unhide/"+this.model.selected_locality.id,
			data: form,
			headers: {"Content-Type": "application/x-www-form-urlencoded"},
			scope: this,
			success: function (request) {
				json = new OpenLayers.Format.JSON();
				data = json.read(request.responseText);
				if (data.localities != null) {
					data.localities.each(function (locality) {
						this.model.update_locality(locality);
					}, this);
				}
			},
			failure: function (request) {
			}
		});
	}
});
