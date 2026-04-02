from schema.base import Base , DB_ENGINE
from schema.models import *
from schema.lookup import *
import schema.models, schema.lookup


# print(Base.metadata.tables)
Base.metadata.drop_all(DB_ENGINE)
Base.metadata.create_all(DB_ENGINE)