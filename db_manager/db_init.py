from db_manager.db_connector import Base , DB_ENGINE
import db_manager.definition
import db_manager.lookup

Base.metadata.drop_all(DB_ENGINE)
Base.metadata.create_all(DB_ENGINE)