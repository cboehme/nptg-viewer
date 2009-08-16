/**
 * Class: NaptanMerger.LocalityList
 * A widget to show a list of localities
 */
NaptanMerger.LocalityList = Class.create(NaptanMerger.Widget, {
	
	model: null,
	url: null,
	list: null,
	
	initialize: function(model, title, url) {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.model = model;
		this.model.events.register("locality_updated", this, this.locality_updated);
		this.model.events.register("locality_selected", this, this.locality_selected);
		this.model.events.register("locality_unselected", this, this.locality_unselected);
		this.model.events.register("locality_highlighted", this, this.locality_highlighted);
		this.model.events.register("locality_unhighlighted", this, this.locality_unhighlighted);

		this.url = url;

		var caption = new Element("h2", {"class": "LocalityList"});
		caption.appendChild(Text(title));

		this.list = new Element("ol", {"class": "LocalityList"});

		this.container.appendChild(caption);
		this.container.appendChild(this.list);

		this._create_list(new Array());
	},

	locality_updated: function(locality) {
		if (this.model.is_locality_selected(locality.id)) {
			this.model.unmark_all_localities();
			this.get_localities(this.url+this.model.selected_locality.id);
		}
	},
	
	locality_selected: function(locality) {
		this.model.unmark_all_localities();
		this.get_localities(this.url+locality.id);
	},

	locality_unselected: function(locality) {
		this.model.unmark_all_localities();
		this._create_list([]);
	},

	locality_highlighted: function(locality) {
		var item = $(this._getItemId(locality.id));
		if (item !== null) {
			item.addClassName("Highlight");
		}
	},

	locality_unhighlighted: function(locality) {
		var item = $(this._getItemId(locality.id));
		if (item !== null) {
			item.removeClassName("Highlight");
		}
	},

	/** 
	 * Method: getLocality
	 * Querys a list of localities from the server.
	 *
	 * Parameters:
	 * url - Retrieve the list of localities from this url.
	 */
	get_localities: function(url) {
		var request = OpenLayers.Request.GET({
			url: url,
			scope: this,
			success: function (request) {
				json = new OpenLayers.Format.JSON();
				data = json.read(request.responseText);
				data.localities.each(function(locality) {
					this.model.add_locality(locality);
					this.model.mark_locality(locality.id);
				}, this);
				this._create_list(data.localities);
			}
		});
	},

	/**
	 * Method: createList
	 * Creates the list of localities
	 */
	_create_list: function(localities) {

		function createItem(locality)
		{
			var item = new Element("li", {"id": this._getItemId(locality.id)});

			item.observe("mouseover", function(evt) {
				this.model.highlight_locality(locality.id);
			}.bind(this));

			item.observe("mouseout", function (evt) {
				this.model.unhighlight_locality();
			}.bind(this));

			item.observe("click", function (evt) {
				this.model.select_locality(locality.id);
			}.bind(this));

			item.appendChild(new Element("img", {"src": get_locality_type(locality) + "_small.png"}));
			if (locality.name != "") {
				item.appendChild(Text(locality.name));
			} else {
				i = new Element("i");
				i.appendChild(Text("Unnamed"));
				item.appendChild(i);
			}
			
			return item;
		}

		this.list.removeChildren();
		if (localities.length) {
			localities.each(function(locality) {
				this.list.appendChild(createItem.call(this, locality));
			}, this);
		} else {
			var li = new Element("li");
			li.appendChild(Text("No localities found"));
			this.list.appendChild(li);
		}
	},

	_getItemId: function (id) {
		return "localityList." + this.widgetId + ".item." + id;
	},
	
});
