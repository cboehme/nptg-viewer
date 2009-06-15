"""SQLAlchemy Metadata and session object"""

from sqlalchemy import MetaData

__all__ = ['engine', 'metadata', 'session']

#SQLAlchemy database engine. Updated by model.init_model().
engine = None

# SQLAlchemy session manager.  Updated by model.init_model().
session = None

# Global metadata. If you have multiple databases with overlapping table.
# names, you'll need a metadata for each database.
metadata = MetaData()

# Directory where uploaded images are stored.  Updated by model.init_model().
image_store = None
