NaptanMerger.Model = Class.create({

	EVENT_TYPES: ["locality_added", "locality_removed", "locality_updated",
		"locality_selected", "locality_unselected", "locality_highlighted", 
		"locality_unhighlighted", "locality_marked", "locality_unmarked"],

	events: null,
	localities: null,
	selected_locality: null,
	highlighted_locality: null,
	marked_localities: null,

	initialize: function() {
		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		this.localities = new Hash();
		this.selected_locality = null;
		this.highlighted_locality = null;
		this.marked_localities = new Hash();
	},

	destroy: function() {
		this.clear_localities();
		this.marked_localities = null;
		this.hightlighted_locality = null;
		this.selected_locality = null;
		this.localities = null;
		this.events = null;
	},

	has_locality: function(id) {
		return this.localities.get(id) !== undefined;
	},

	add_locality: function(locality) {
		if (!this.has_locality(locality.id)) {
			this.localities.set(locality.id, locality);
			this.events.triggerEvent("locality_added", locality);
		} else {
			this.localities.set(locality.id, locality);
			if (this.is_locality_selected(locality.id)) {
				this.selected_locality = locality;
			}
			if (this.is_locality_highlighted(locality.id)) {
				this.highlighted_locality = locality;
			}
			if (this.is_locality_marked(locality.id)) {
				this.marked_localities.set(locality.id, locality);
			}
			this.events.triggerEvent("locality_updated", locality);
		}
	},

	remove_locality: function(id) {
		var locality = this.localities.unset(id);
		if (locality !== undefined) {
			if (this.is_locality_selected(id)) {
				this.unselect_locality();
			}
			if (this.is_locality_highlighted(id)) {
				this.unhighlight_locality();
			}
			this.unmark_locality(id);
			this.events.triggerEvent("locality_removed", locality);
		}
	},

	update_locality: function(locality) {
		if(this.has_locality(locality.id)) {
			this.localities.set(locality.id, locality);
			if (this.is_locality_selected(locality.id)) {
				this.selected_locality = locality;
			}
			if (this.is_locality_highlighted(locality.id)) {
				this.highlighted_locality = locality;
			}
			if (this.is_locality_marked(locality.id)) {
				this.marked_localities.set(locality.id, locality);
			}
			this.events.triggerEvent("locality_updated", locality);
		} else {
			this.localities.set(localities.id, locality);
			this.events.triggerEvent("locality_added", locality);
		}
	},

	clear_localities: function() {
		this.localities.each(function(locality) {
			this.remove_locality(locality[0]);
		}, this);
	},

	is_locality_selected: function(id) {
		return this.selected_locality !== null 
			&& this.selected_locality.id == id;
	},

	select_locality: function(id) {
		if (!this.is_locality_selected(id)) {
			this.unselect_locality();
			var locality = this.localities.get(id);
			if (locality !== undefined) {
				this.selected_locality = locality;
				this.events.triggerEvent("locality_selected", locality);
			}
		}
	},

	unselect_locality: function() {
		if (this.selected_locality !== null) {
			var locality = this.selected_locality;
			this.selected_locality = null;
			this.events.triggerEvent("locality_unselected", locality);
		}
	},

	is_locality_highlighted: function(id) {
		return this.highlighted_locality !== null 
			&& this.highlighted_locality.id == id;
	},

	highlight_locality: function(id) {
		if (!this.is_locality_highlighted(id)) {
			this.unhighlight_locality();
			var locality = this.localities.get(id);
			if (locality !== undefined) {
				this.highlighted_locality = locality;
				this.events.triggerEvent("locality_highlighted", locality);
			}
		}
	},

	unhighlight_locality: function() {
		if (this.highlighted_locality !== null) {
			var locality = this.highlighted_locality;
			this.highlighted_locality = null;
			this.events.triggerEvent("locality_unhighlighted", locality);
		}
	},

	is_locality_marked: function(id) {
		return this.marked_localities.get(id) !== undefined;
	},

	mark_locality: function (id) {
		if (!this.is_locality_marked(id)) {
			var locality = this.localities.get(id);
			if (locality !== undefined) {
				this.marked_localities.set(locality.id, locality);
				this.events.triggerEvent("locality_marked", locality);
			}
		}
	},

	unmark_locality: function(id) {
		var locality = this.marked_localities.get(id);
		if (locality !== undefined) {
			this.marked_localities.unset(id);
			this.events.triggerEvent("locality_unmarked", locality);
		}
	},

	unmark_all_localities: function() {
		this.marked_localities.each(function(locality) {
			this.unmark_locality(locality[0])
		}, this);
	}
});
