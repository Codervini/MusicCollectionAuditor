import dotenv
from sqlalchemy import (
    Column, Text, Boolean, SmallInteger, Numeric,
    String, TIMESTAMP, ARRAY, Index, text, create_engine, Enum,
    UniqueConstraint, ForeignKey, select , event
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, base
from sqlalchemy.sql import func
import enum  # Python's built-in enum — used to define the values
import hashlib
from mca_tools.machine_identifier import  machine_id
from schema.base import Base, DB_ENGINE, SESSION_MANAGER
import schema.models.meta_processor_universe as mp
import mca_tools.enums as mca_enum
from mca_tools.generate_uuidv7 import generate_uuidv7
# #----- Constants -----------------------------------------------------------------
# CONFIG_CONSTANTS = dotenv.dotenv_values(".env")
# DB_ENGINE = create_engine(f"postgresql+psycopg://{CONFIG_CONSTANTS['DB_USERNAME']}:{CONFIG_CONSTANTS['DB_PASSWORD']}@localhost:5432/mcamusicdb")
# SESSION_MANAGER = sessionmaker(bind=DB_ENGINE)
MACHINE_ID = machine_id()
# Base = declarative_base()
# # class Base(base):
# #     pass


#------------Tools-----------------------------------------------------------------------------

def db_init():
    Base.metadata.create_all(DB_ENGINE)
def drop_all_table_cascade():
    Base.metadata.drop_all(DB_ENGINE)

def count_table_rows(table):
    with SESSION_MANAGER() as session:
        count = session.scalar(select(func.count()).select_from(text(table)))
        return count




class Song:
    def __init__(self,  
                file_path:str, 
                source_artist:str = None, source_title:str = None,
                source_track_mbid:str = None, source_album_mbid:str = None,
                track_mbid_valid:bool = None, album_mbid_valid:bool = None):

        if not MACHINE_ID:
            print("Something is wrong with machine ID, aborting!!")
        elif MACHINE_ID:  
            # Keys to uniquely find a file in db
            self.MACHINE_ID = MACHINE_ID
            self.file_path =  file_path
            self.id = generate_uuidv7()
            


            table_file_hash = self.fetch_file_hash_in_db()
            # table_file_path = self.fetch_column_data(Meta_Processor_Table.file_path)
            table_machine_id = self.fetch_column_data(mp.MetaProcessorRuns.machine_id)

            if table_file_hash and table_machine_id:
                print("Row already present")
                self.update_last_scanned_at()
                self.check_and_validate_if_hash_in_db_changed_externally()
            else:
                with SESSION_MANAGER() as session:
                    record = mp.MetaProcessorRuns(

                        # id = self.id
                        # mca_pid = pass
                        # file_universe_id = pass
                        # machine_id = self.MACHINE_ID,
                        # trigger = pass
                        # triggered_by_user_id = pass
                        # session_id = pass
                        # current_stage = pass
                        # current_phase = pass
                        # current_step = pass
                        # is_duplicate_of = pass

                        # file_path  = self.file_path,
                        # file_hash = self.calculate_file_hash(),
                        # status  = mca_enum.ProcessorStatus.pending,
                        # current_stage = mca_enum.PipelineStage.read_file,

                        # #Source file info
                        # source_track_mbid   = source_track_mbid,
                        # source_album_mbid = source_album_mbid,
                        # source_artist = source_artist,
                        # source_title  = source_title,

                        # #Source Validation
                        # has_track_mbid  = bool(source_track_mbid),
                        # has_album_mbid   = bool(source_album_mbid),
                        # has_artist_and_title_tags = bool(source_artist and source_title),
                        # track_mbid_valid  = track_mbid_valid,
                        # album_mbid_valid  = album_mbid_valid
                    )
                    session.add(record)
                    session.commit()

    # Basic functions
    # def fetch_column_data(self, column, table):
    #     with SESSION_MANAGER() as session:
    #         command = select(column).where(
    #             Meta_Processor_Table.machine_id == self.MACHINE_ID,
    #             Meta_Processor_Table.file_path == self.file_path
    #         )
    #         return session.execute(command).scalar_one_or_none()
        
    # def set_multiple_columns_data(self, value_column:list[tuple[str|enum.Enum|Meta_Processor_Table]]):
    #     with SESSION_MANAGER() as session:
    #         select_command = select(Meta_Processor_Table).where(
    #             Meta_Processor_Table.machine_id == self.MACHINE_ID,
    #             Meta_Processor_Table.file_path  == self.file_path
    #         )
    #         row = session.execute(select_command).scalar_one_or_none()
    #         if row:
    #             for value, column in value_column:
    #                 setattr(row, column.key, value)     # row.column = value        
    #             row.last_scanned_at = func.now() 
    #         else:
    #             print("No row found", row)
    #         session.commit()

    # def set_column_data(self, value, column):
    #     with SESSION_MANAGER() as session:
    #         select_command = select(Meta_Processor_Table).where(
    #             Meta_Processor_Table.machine_id == self.MACHINE_ID,
    #             Meta_Processor_Table.file_path  == self.file_path
    #         )
    #         row = session.execute(select_command).scalar_one_or_none()
    #         if row:
    #             setattr(row, column.key, value)     # row.column = value        
    #             row.last_scanned_at = func.now() 
    #         else:
    #             print("No row found", row)
    #         session.commit()

    
    # def update_last_scanned_at(self):
    #     with SESSION_MANAGER() as session:
    #         select_command = select(Meta_Processor_Table).where(
    #             Meta_Processor_Table.machine_id == self.MACHINE_ID,
    #             Meta_Processor_Table.file_path  == self.file_path
    #         )
    #         row = session.execute(select_command).scalar_one_or_none()
    #         if row:
    #             print(row)
    #             row.last_scanned_at = func.now()
    #         else:
    #             print("No row found", row)
    #         session.commit()



    # def calculate_file_hash(self):
    #     with open(self.file_path,"rb") as f:
    #         return hashlib.sha256(f.read()).hexdigest()
    

    # def truncate_table():
    #     pass

    # # Derived Functions
    # def check_and_validate_if_hash_in_db_changed_externally(self):
    #     file_hash  = self.calculate_file_hash()
    #     file_hash_in_db = self.fetch_column_data(Meta_Processor_Table.file_hash)
    #     if file_hash_in_db and file_hash_in_db != file_hash: #Hash changed externally
    #         self.set_multiple_columns_data([
    #             (HashChangedBy.external, Meta_Processor_Table.hash_changed_by),
    #             (file_hash_in_db, Meta_Processor_Table.last_known_hash),
    #             (file_hash, Meta_Processor_Table.file_hash)
    #         ])
    #         return True
    #     return False
   
    # def fetch_file_hash_in_db(self):
    #     return self.fetch_column_data(Meta_Processor_Table.file_hash)



