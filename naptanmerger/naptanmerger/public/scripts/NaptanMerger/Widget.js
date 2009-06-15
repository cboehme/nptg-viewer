/**
 * Class: NaptanMerger.Widget
 * Base class for widgets. Provides embedding and unhinging functionality.
 */
NaptanMerger.Widget = Class.create({
	
	widgetId: null,
	container: null,
	containerObj: null,

	initialize: function() {
		this.widgetId = uniqueId();
		this.container = document.createDocumentFragment();
		this.containerObj = null;
	},

	destroy: function() {
		this.containerObj = null;
		this.container = null;
	},
	
	/**
	 * Method: embed
	 * Embeds the widget within another DOM element.
	 *
	 * Parameters:
	 * widgetContainer - {NaptanMerger.WidgetContainer} Container into which
	 *     the widget will be embedded.
	 */
	embed: function(widgetContainer) {
		if (this.containerObj !== widgetContainer)
		{
			// Remove widget from its current container:
			if(this.containerObj)
				this.containerObj.unhingeWidget()
			
			// Clear target:
			widgetContainer.unhingeWidget();

			// Set new widget container:
			this.containerObj = widgetContainer;
			this.containerObj.embedWidget(this);

			// Move nodes into the new container:
			while (this.container.hasChildNodes())
				this.containerObj.element.appendChild(this.container.removeChild(this.container.firstChild));
			this.container = this.containerObj.element;
		}
	},

	/**
	 * Method: unhinge
	 * Removes the widget from its container.  This is the counterpart 
	 * to embed.
	 */
	unhinge: function() {
		if (this.containerObj)
		{
			// Remove from widget container:
			// Set this.containerObj to null first because
			// WidgetContainer.unhinge() will call unhinge()
			// too and we do not want to unhinge the widget 
			// twice:
			var containerObj = this.containerObj;
			this.containerObj = null;
			containerObj.unhingeWidget();

			// Move nodes into a document fragment:
			var container = document.createDocumentFragment();
			while (this.container.hasChildNodes())
				container.appendChild(this.container.removeChild(this.container.firstChild));
			this.container = container;
		}
	},
	
	/**
	 * Method: isEmbedded
	 * Return true if the widget is currently embedded in the page. A widget is
	 * considered to be embedded if the container is not a document fragment node.
	 */
	isEmbedded: function() {
		return this.containerObj !== null;
	}
});
