CREATE SEQUENCE localities_id_seq;

CREATE TABLE localities (
	id INTEGER DEFAULT nextval('localities_id_seq') NOT NULL PRIMARY KEY,
	lat DECIMAL(10,7) NOT NULL,
	lon DECIMAL(10,7) NOT NULL,
	osm_id BIGINT NOT NULL UNIQUE,
	osm_version BIGINT NOT NULL CHECK (osm_version > 0),
	name VARCHAR(255),
	hidden TIMESTAMP DEFAULT NULL,
	comment VARCHAR(255) DEFAULT NULL
);

CREATE INDEX localities_lat_lon_idx ON localities (lat, lon);
CREATE INDEX localities_lon_lat_idx ON localities (lon, lat);
CREATE INDEX localities_osm_id_osm_version_idx ON localities (osm_id, osm_version);
CREATE INDEX localities_name_idx ON localities (name);

CREATE TABLE tags (
	locality_id INTEGER NOT NULL
		REFERENCES localities(id) ON DELETE CASCADE,
	name VARCHAR(255) NOT NULL,
	value VARCHAR(65535) NOT NULL,  -- based on MySQL's TEXT type
	PRIMARY KEY (locality_id, name)
	);

VACUUM ANALYZE;
