from schema.base import Base , DB_ENGINE
import schema.models
import schema.lookup

Base.metadata.drop_all(DB_ENGINE)
Base.metadata.create_all(DB_ENGINE)