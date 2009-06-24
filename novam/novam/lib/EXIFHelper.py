# -*- coding: utf-8 -*-
#
# Copyright (C) 2006  Michael Strecke
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#
# The following functions have been extracted from
# http://svn.openstreetmap.org/applications/editors/pyosmeditor/pyosmeditor.py

from novam.lib import EXIF

def _val_fract(s):
	return float(s.num) / float(s.den)

def _val_deg(s):
	g = _val_fract(s[0])
	m = _val_fract(s[1])
	s = _val_fract(s[2])
	return g + m / 60.0 + s / 3600.0

def get_gps_info(filename):
	try:
		f = open(filename, "rb")
		tags = EXIF.process_file(f)

		lat = tags["GPS GPSLatitude"]
		lat_r = tags["GPS GPSLatitudeRef"]
		lon = tags["GPS GPSLongitude"]
		lon_r = tags["GPS GPSLongitudeRef"]
	except KeyError:
		return None

	lat = _val_deg(lat.values)
	if str(lat_r) == "S": lat = -lat
	lon = _val_deg(lon.values)
	if str(lon_r) == "W": lon = -lon

	return (lon, lat)
