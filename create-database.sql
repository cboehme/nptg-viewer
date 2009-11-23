-- Configure postGIS:
-- CREATE LANGUAGE plpgsql;
-- \i /usr/share/postgresql/contrib/lwpostgis.sql
-- \i /usr/share/postgresql/contrib/spatial_ref_sys.sql

CREATE SEQUENCE localities_id_seq;
CREATE TABLE localities (
	id INTEGER DEFAULT nextval('localities_id_seq') NOT NULL PRIMARY KEY,
	osm_id BIGINT NOT NULL UNIQUE,
	osm_version BIGINT NOT NULL CHECK (osm_version > 0),
	name VARCHAR(255),
	hidden TIMESTAMP DEFAULT NULL,
	comment VARCHAR(255) DEFAULT NULL
	);
ALTER SEQUENCE localities_id_seq OWNED BY localities.id;

SELECT AddGeometryColumn('localities', 'coords', 4326, 'POINT', 2);

CREATE INDEX localities_coords_idx ON localities USING GIST (coords);
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
