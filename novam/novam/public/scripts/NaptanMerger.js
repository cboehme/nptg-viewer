window.NaptanMerger = {
	_scriptName: "NaptanMerger.js",

	_getScriptLocation: function () {
		var scriptLocation = "";
		var isNM = new RegExp("(^|(.*?\\/))(" + NaptanMerger._scriptName + ")(\\?|$)");
				
		var scripts = document.getElementsByTagName('script');
		for (var i=0, len=scripts.length; i<len; i++) {
			var src = scripts[i].getAttribute('src');
			if (src) {
				var match = src.match(isNM);
				if(match) {
					scriptLocation = match[1];
					break;
				}
			}
		}
		return scriptLocation;
	}
};


var jsFiles = new Array(
	"NaptanMerger/Utilities.js",
	"NaptanMerger/WidgetContainer.js",
	"NaptanMerger/Widget.js",
	"NaptanMerger/MapControl.js",
	"NaptanMerger/WaypointViewer.js",
	"NaptanMerger/PositionChooser.js",
	"NaptanMerger/ImageBrowser.js",
	"NaptanMerger/ImageViewer.js",
	"NaptanMerger/StopSelector.js",
	"NaptanMerger/MergeSelector.js",
	"NaptanMerger/MergeDialog.js",
	"NaptanMerger/StopViewer.js",
	"NaptanMerger/StopEditor.js",
	"NaptanMerger/PositionSelector.js",
	"NaptanMerger/WaypointSelector.js",
	"NaptanMerger/FeatureControl.js",
	"NaptanMerger/ImportsFinished.js"
);

var host = NaptanMerger._getScriptLocation();
for (var i=0, len=jsFiles.length; i<len; i++)
{
	var s = document.createElement("script");
	s.src = host + jsFiles[i];
	s.type = "text/javascript";
	var h = document.getElementsByTagName("head").length ?
	        document.getElementsByTagName("head")[0] :
	        document.body;
	h.appendChild(s);
}

/*
 * Starts the application when the page and all additional 
 * scripts are loaded.
 */
function runApp(func) {
	if (runApp.readyState == 2) {
		func();
	}
	else {
		runApp.func = func;
	}
}

runApp.func = null;
runApp.readyState = 0;

runApp.importsFinished = function() {
	++runApp.readyState;
	if (runApp.readyState == 2) {
		runApp.func();
	}
}

runApp.pageLoaded = function() {
	++runApp.readyState;
	if (runApp.readyState == 2) {
		runApp.func();
	}
}

if (window.addEventListener)
	window.addEventListener("load", runApp.pageLoaded, false);
else if (window.attachEvent)
	window.attachEvent("onload", runApp.pageLoaded);
else
	window.onload = runApp.pageLoaded;
