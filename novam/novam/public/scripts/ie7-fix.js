/*
 * (c) 2009 Christoph Böhme <christoph@b3e.net>
 * 
 * This file is part of Novam.
 * 
 * Novam is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Novam is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */

/*
 * IE 7 does not provide correct width/height values if they were not set explicitly.
 * Since OpenLayers requires these values we set them here.
 */
function correct_dimensions()
{
	var panel = $("mapPanel");
	var map = $("map");

	map.style.width = panel.offsetWidth + "px";
	map.style.height = panel.offsetHeight + "px";
}

window.attachEvent("onload", correct_dimensions);
window.attachEvent("onresize", correct_dimensions);
