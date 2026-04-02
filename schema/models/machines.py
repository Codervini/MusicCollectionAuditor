from schema.base import Base
from sqlalchemy import (
    Column , text, String
)
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy.sql import func


class Machines(Base):
    __tablename__ = "machines"
    
    id = Column(String(64), primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, server_default=text("uuidv7()"))
    mca_pid = Column(String(1024), unique=True, nullable=False)
