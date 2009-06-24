var current_stop = null;
var current_merge_stop = null;
var current_waypoint = null;
var current_image = null;

var stop_list = new Array();
var merge_stop_list = new Array();
var waypoint_list = new Array();
var image_list = new Array();

/*
 * Remove all markers which are neither on the map nor in one 
 * of the lists (*_list) nor currently selected (current_*).
 */
function clean_markers()
{
	var unused_features = Array();

	markers.features.each(function(feature) {
		function compare_id(item) { 
			return item.attributes.id == feature.attributes.id; 
		}
		
		switch (feature.attributes.type)
		{
			case "stop":
				if (stop_list.find(compare_id) != undefined)  return;
				if (merge_stop_list.find(compare_id) != undefined)  return;
				if (current_stop && current_stop.attributes.id == feature.attributes.id)  return;
				if (current_merge_stop && current_merge_stop.attributes.id == feature.attributes.id)  return;
				break;
			case "waypoint":
				if (waypoint_list.find(compare_id) != undefined)  return;
				if (current_waypoint && current_waypoint.attributes.id == feature.attributes.id)  return;
				break;
			case "image":
				if (image_list.find(compare_id) != undefined)  return;
				if (current_image && current_image.attributes.id == feature.attributes.id)  return;
				break;
		}

		if (map.getExtent().intersectsBounds(feature.geometry.getBounds()))  return;

		unused_features.push(feature);
	});

	markers.destroyFeatures(unused_features);
}

function show_stop(stop)
{
}

function merge_stop()
{
	$('merged_stop_id').value = current_similar_stop.attributes.id;

	if ('name' in current_similar_stop.attributes.tags)
		$('tag_name').value = current_similar_stop.attributes.tags['name'];

	if ('naptan:CommonName' in current_similar_stop.attributes.tags)
		$('tag_naptan_commonname').value = current_similar_stop.attributes.tags['naptan:CommonName'];

	if ('naptan:Street' in current_similar_stop.attributes.tags)
		$('tag_naptan_street').value = current_similar_stop.attributes.tags['naptan:Street'];
}

function select_stop(stop)
{
	current_stop = stop;
	show_stop(stop);
	query_merge_stop_list();
	query_waypoint_list();
	
	var caption = 'Bus Stop';
	if (stop.attributes.state == "plain_osm_stop")
		caption = 'OSM Stop';
	else if (stop.attributes.state == "plain_naptan_stop")
		caption = "NaPTAN Stop";
	else if (stop.attributes.state == "merged_stop")
		caption = "Merged Stop";
	else if (stop.attributes.state == "finished_stop")
		caption = "Finished Stop";
	else if (stop.attributes.state == "no_physical_stop")
		caption = "No Physical Stop";

	$("selected_item").replaceContent(Text(caption));
}

function select_waypoint(waypoint)
{
	current_waypoint = waypoint;
	show_waypoint(waypoint);
	query_stop_list();

	$("selected_item").replaceContent(Text("Waypoint"));
}
