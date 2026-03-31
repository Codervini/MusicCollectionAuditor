import dotenv
from mca_tools.machine_identifier import  machine_id
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase ,sessionmaker

#----- Constants -----------------------------------------------------------------
CONFIG_CONSTANTS = dotenv.dotenv_values("/home/vinish/Desktop/MusicCollectionAuditor/data/config/.env")
DB_ENGINE = create_engine(f"postgresql+psycopg://{CONFIG_CONSTANTS['DB_USERNAME']}:{CONFIG_CONSTANTS['DB_PASSWORD']}@localhost:5432/mcamusicdb")
SESSION_MANAGER = sessionmaker(bind=DB_ENGINE)
MACHINE_ID = machine_id()



class Base(DeclarativeBase):
    pass
