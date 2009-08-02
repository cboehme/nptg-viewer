CREATE TABLE Localities (
	id BIGINT UNSIGNED AUTO_INCREMENT,
	lat DECIMAL(10,7) NOT NULL,
	lon DECIMAL(10,7) NOT NULL,
	osm_id BIGINT SIGNED,
	osm_version BIGINT UNSIGNED,
	name VARCHAR(255),
	hidden DATETIME DEFAULT NULL,
	comment VARCHAR(255) DEFAULT NULL,
	PRIMARY KEY (id),
	INDEX (lat, lon),
	INDEX (osm_id, osm_version),
	UNIQUE (osm_id),
	INDEX (name)
	)
ENGINE=InnoDB;

CREATE TABLE Tags (
	locality_id BIGINT UNSIGNED,
	name VARCHAR(255) NOT NULL,
	value TEXT NOT NULL,
	PRIMARY KEY (locality_id, name),
	FOREIGN KEY (locality_id)
		REFERENCES Localities(id)
		ON DELETE CASCADE
	)
ENGINE=InnoDB;
