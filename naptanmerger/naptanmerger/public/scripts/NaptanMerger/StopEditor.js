/**
 * Class: NaptanMerger.StopEditor
 * A widget to edit a bus stop
 */
NaptanMerger.StopEditor = Class.create(NaptanMerger.Widget, {
	
	EVENT_TYPES: ['saved', 'cancelled'],

	events: null,

	form: null,
	tagInputs: null,
	mergedStopInput: null,
	positionLatInput: null,
	positionLonInput: null,
	saveButton: null,
	cancelButton: null,

	modified: false,

	feature: null,

	initialize: function() {
		NaptanMerger.Widget.prototype.initialize.call(this);

		this.events = new OpenLayers.Events(this, null, this.EVENT_TYPES);

		var caption = new Element('h2', {'class': 'StopEditor'});
		caption.appendChild(Text('Edit Bus Stop'));

		this.form = new Element('form', {
			'class': 'StopEditor', 
			'action': ''
		});

		this._createFormFields();

		this.mergedStopInput = this._createHiddenField('mergedStop', 'mergedStop');
		this.positionLatInput = this._createHiddenField('positionLat', 'positionLat');
		this.positionLonInput = this._createHiddenField('positionLon', 'positionLon');

		this.saveButton = new Element('button', {
			'class': 'StopEditor OkButton', 
			'type': 'button'
		});
		this.saveButton.observe('click', function (evt) {
			this.save();
		}.bind(this));
		this.saveButton.appendChild(Text("Save"));

		this.cancelButton = new Element('button', {
			'class': 'StopEditor CancelButton',
			'type': 'button'
		});
		this.cancelButton.observe('click', function (evt) {
			this.cancel();
		}.bind(this));
		this.cancelButton.appendChild(Text("Cancel"));

		this.container.appendChild(caption);
		this.container.appendChild(this.form);
		this.container.appendChild(this.saveButton);
		this.container.appendChild(this.cancelButton);

		this.setStop(null);
	},

	_createHiddenField: function(id, name) {
		var input = new Element('input', {
			'type': 'hidden',
			'id': this._getElementId(id),
			'name': name,
			'value': ''
		});

		this.form.appendChild(input);

		return input;
	},

	_createFormFields: function() {

		function createFieldSet(caption)
		{
			var fieldSet = new Element('fieldset');
			var legend = new Element('legend');

			legend.appendChild(Text(caption));
			fieldSet.appendChild(legend);
			this.form.appendChild(fieldSet);

			return fieldSet;
		}

		function createTextbox(parentNode, id, caption, name, separatorTool)
		{
			var label = new Element('label', {
				'class': 'TextboxLabel',
				'htmlFor': this._getElementId(id)
			});
			if (typeof(caption) == 'string')
				label.appendChild(Text(caption));
			else
				label.appendChild(caption);

			this.tagInputs[id] = new Element('input', {
				'type': 'text',
				'id': this._getElementId(id),
				'name': name,
				'value': ''
			});

			this.tagInputs[id].observe('change', function (evt) {
				this._setModified(true);
			}.bind(this));

			parentNode.appendChild(label);
			parentNode.appendChild(this.tagInputs[id]);
			
			if (separatorTool)
			{
				var button = new Element('button', {
					'type': 'button'
				});
				button.observe('click', function (evt) {
					var el = this.tagInputs[id];
					var sep = el.value.substring(el.selectionStart, el.selectionEnd);
					el.value = replaceSeparators(el.value, sep, true);
					this._setModified(true);
				}.bind(this));

				button.appendChild(new Element('img', {
					'src': 'separator-button.png'
				}));

				parentNode.appendChild(button);
			}

			parentNode.appendChild(new Element('br'));  // TODO: Remove this and replace it by css:after properties
		}

		function createCheckbox(parentNode, id, caption, name, value)
		{
			var label = new Element('label', {
				'class': 'CheckboxLabel',
				'htmlFor': this._getElementId(id)
			});
			if (typeof(caption) == 'string')
				label.appendChild(Text(caption));
			else
				label.appendChild(caption);

			this.tagInputs[id] = new Element('input', {
				'type': 'checkbox',
				'id': this._getElementId(id),
				'name': name,
				'value': value
			});

			this.tagInputs[id].observe('change', function (evt) {
				this._setModified(true);
			}.bind(this));

			parentNode.appendChild(this.tagInputs[id]);
			parentNode.appendChild(label);
			parentNode.appendChild(new Element('br'));  // TODO: Remove this and replace it by css:after properties
		}

		function createCombobox(parentNode, id, caption, name, values)
		{
			var label = new Element('label', {
				'class': 'ComboboxLabel',
				'htmlFor': this._getElementId(id)
			});
			if (typeof(caption) == 'string')
				label.appendChild(Text(caption));
			else
				label.appendChild(caption);

			this.tagInputs[id] = new Element('select', {
				'id': this._getElementId(id),
				'name': name,
				'size': 1
			});
			for (var key in values)
			{
				var option = new Element('option', {'value': key});
				this.tagInputs[id].appendChild(option);
				option.appendChild(Text(values[key]));
			}

			this.tagInputs[id].observe('change', function (evt) {
				this._setModified(true);
			}.bind(this));

			parentNode.appendChild(label);
			parentNode.appendChild(this.tagInputs[id]);
			parentNode.appendChild(new Element('br'));  // TODO: Remove this and replace it by css:after properties
		}

		
		var tristateValues = {
			'': 'Not set', 
			'yes': 'Yes', 
			'no': 'No'
		};
		
		// Clear form:
		this.form.removeChildren();
		this.tagInputs = {};

		// Basic properties:
		var fieldSet = createFieldSet.call(this, 'Basic properties');

		createCheckbox.call(this, fieldSet, 'busStop', 'Tag as bus stop', 'highway', 'bus_stop');
		createCheckbox.call(this, fieldSet, 'verified', 
			concatElements('Bus stop ', Element.wrap(Text('not'), 'em'), ' verified'), 
			'naptan:unverified', 'yes'); 
		createCheckbox.call(this, fieldSet, 'physicallyPresent', 
			concatElements('Physically ', Element.wrap(Text('not'), 'em'), ' present'), 
			'physically_present', 'no');
		createCheckbox.call(this, fieldSet, 'customaryStop', 'Customary Stop', 'customary_stop', 'yes');

		// Names:
		fieldSet = createFieldSet.call(this, 'Stop names');

		createTextbox.call(this, fieldSet, 'name', 'Name', 'name');
		createTextbox.call(this, fieldSet, 'commonName', 'Common name', 'naptan:CommonName');
		createTextbox.call(this, fieldSet, 'indicator', 'Indicator', 'naptan:Indicator');
		createTextbox.call(this, fieldSet, 'localRef', 'Local ref.', 'local_ref');
		createTextbox.call(this, fieldSet, 'street', 'Street', 'naptan:Street');

		// Routes:
		fieldSet = createFieldSet.call(this, 'Bus routes');

		createTextbox.call(this, fieldSet, 'routes', 'Routes', 'route', true);
		createTextbox.call(this, fieldSet, 'towards', 'Towards', 'towards');

		// Stop features:
		fieldSet = createFieldSet.call(this, 'Stop features');

		createCheckbox.call(this, fieldSet, 'layby', 'Layby', 'layby', 'yes');
		createCheckbox.call(this, fieldSet, 'infoBoard', 'Electronic information board', 'electronic_information_board', 'yes');
		createCombobox.call(this, fieldSet, 'shelter', 'Shelter', 'shelter', tristateValues);

		// Reference codes:
		fieldSet = createFieldSet.call(this, 'Reference codes');

		createTextbox.call(this, fieldSet, 'adminAreaRef', 'Admin. area', 'naptan:AdministrativeAreaRef');
		createTextbox.call(this, fieldSet, 'plusbusZoneRef', 'Plusbus zone', 'naptan:PlusbusZoneRef');
		createTextbox.call(this, fieldSet, 'atcoCode', 'Atco code', 'naptan:AtcoCode');
		createTextbox.call(this, fieldSet, 'assetRef', 'Asset ref.', 'asset_ref');
		createTextbox.call(this, fieldSet, 'naptanCode', 'NaPTAN code', 'naptan:NaptanCode');

		// Other tags:
		fieldSet = createFieldSet.call(this, 'Other tags');

		createTextbox.call(this, fieldSet, 'source', 'Source', 'source', true);
	},

	_setModified: function(value) {
		this.modified = value;
		this.saveButton.disabled = !this.modified;
	},

	setStop: function(feature) {

		this.feature = feature;

		for (var id in this.tagInputs)
		{
			this.form.findLabelFor(this.tagInputs[id]).removeClassName('MergeConflict');
			this.form.findLabelFor(this.tagInputs[id]).removeClassName('MergedValue');
		}

		this._setModified(false);

		if (feature === null)
		{
			this.form.disable();
			
			for (var el in this.tagInputs)
			{
				if (this.tagInputs[el].type == 'checkbox')
					this.tagInputs[el].checked = false;
				else
					this.tagInputs[el].value = '';
			}

			this.mergedStopInput.value = '';
			this.positionLonInput.value = '';
			this.positionLatInput.value = '';
		}
		else
		{
			this.form.enable();

			for (var i in this.tagInputs)
			{
				el = this.tagInputs[i];
				if (el.type == 'checkbox')
					el.checked = feature.attributes.tags[el.name] == el.value;
				else
				{
					if (feature.attributes.tags[el.name] !== undefined)
						el.value = feature.attributes.tags[el.name];
					else
						el.value = '';
				}
			}

			this.mergedStopInput.value = '';
			this.positionLonInput.value = feature.attributes.lon;
			this.positionLatInput.value = feature.attributes.lat;
		}
	},

	updateStopPosition: function(lon, lat) {
		if (this.positionLonInput.value != lon || this.positionLatInput.value != lat)
			this._setModified(true);

		this.positionLonInput.value = lon;
		this.positionLatInput.value = lat;
	},

	save: function() {
		this.events.triggerEvent('saved');
	},

	cancel: function() {
		this.events.triggerEvent('cancelled');
	},

	mergeStops: function (feature)
	{
		function joinTexts(element)
		{
			var currentValue = element.value;
			var newValue = feature.attributes.tags[element.name];

			if(newValue !== undefined && !newValue.blank())
			{
				if (currentValue.blank())
				{
					element.value = replaceSeparators(newValue);
				}
				else
				{
					currentValue = replaceSeparators(currentValue);
					newValue = replaceSeparators(newValue);
					combinedValue = currentValue + ';' + newValue;
					element.value = combinedValue.split(';').uniq().join(';');
				}
				findLabelFor(element).addClassName('MergedValue');
			}
		}

		function mergeTexts(element)
		{
			var currentValue = element.value;
			var originalValue = this.feature.attributes.tags[element.name];
			var newValue = feature.attributes.tags[element.name];

			if (newValue !== undefined && !newValue.blank())
			{
				if (currentValue.blank())
				{
					element.value = newValue;
					findLabelFor(element).addClassName('MergedValue');
				}
				else
				{
					var box = new Element('div', {'class': 'ConflictTool'});
					
					var list = new Element('dl');
					list.observe('mousedown', function (evt) {
						evt.stop();
					}.bind(this));
					box.appendChild(list);

					var el = new Element('dt');
					el.appendChild(Text('Original value'));
					list.appendChild(el);
					el = new Element('dd');
					el.appendChild(Text(originalValue));
					el.observe('mousedown', function (evt) {
						evt.stop();
					}.bind(this));

					list.appendChild(el);

					el = new Element('dt');
					el.appendChild(Text('New value'));
					list.appendChild(el);
					el = new Element('dd');
					el.appendChild(Text(newValue));
					list.appendChild(el);
					
					box.style.position = "absolute";
					box.style.display = "none";
					
					element.parentNode.insertAfter(box, element);
					box.clonePosition(element, {setHeight: false, offsetTop: element.getHeight()});

					element.observe('focus', function (evt) {
						box.show();
					});

					element.observe('blur', function (evt) {
						box.hide();
					});

					findLabelFor(element).addClassName('MergeConflict');
				}
			}
		}

		function mergeCheckboxes(element)
		{
			var newValue = feature.attributes.tags[element.name];

			if (newValue !== undefined)
			{
				if (!element.checked)
				{
					element.checked = true;
					findLabelFor(element).addClassName('MergedValue');
				}
			}
		}

		function mergeComboboxes(element)
		{
		}

		feature.attributes.type = feature.attributes.type.replace(/plain_/, 'deleted_');
	
		this.mergedStopInput.value = feature.attributes.id;
		this._setModified(true);

		// Basic properties:
		mergeCheckboxes.call(this, this.tagInputs.busStop);
		mergeCheckboxes.call(this, this.tagInputs.verified);
		mergeCheckboxes.call(this, this.tagInputs.physicallyPresent);
		mergeCheckboxes.call(this, this.tagInputs.customaryStop);

		// Names:
		mergeTexts.call(this, this.tagInputs.name);
		mergeTexts.call(this, this.tagInputs.commonName);
		mergeTexts.call(this, this.tagInputs.indicator);
		mergeTexts.call(this, this.tagInputs.localRef);
		mergeTexts.call(this, this.tagInputs.street);

		// Routes:
		joinTexts.call(this, this.tagInputs.routes); 
		mergeTexts.call(this, this.tagInputs.towards);

		// Stop features:
		mergeCheckboxes.call(this, this.tagInputs.layby);
		mergeCheckboxes.call(this, this.tagInputs.infoBoard);
		mergeCheckboxes.call(this, this.tagInputs.shelter);

		// Reference codes:
		mergeTexts.call(this, this.tagInputs.adminAreaRef);
		mergeTexts.call(this, this.tagInputs.plusbusZoneRef);
		mergeTexts.call(this, this.tagInputs.atcoCode);
		mergeTexts.call(this, this.tagInputs.assetRef);
		mergeTexts.call(this, this.tagInputs.naptanCode);
		
		// Other tags:
		joinTexts.call(this, this.tagInputs.source);
	},

	_getElementId: function(id) {
		return 'stopEditor.' + this.widgetId + "." + id;
	}
});
