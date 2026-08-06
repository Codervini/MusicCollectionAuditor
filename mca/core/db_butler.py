import dotenv
from sqlalchemy import (
    Column, Text, Boolean, SmallInteger, Numeric,
    String, TIMESTAMP, ARRAY, Index, text, create_engine, Enum,
    UniqueConstraint, ForeignKey, select , event, inspect, MetaData , Table, update
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, base
from sqlalchemy.sql import func
import enum  
import hashlib
from mca_tools.machine_identifier import  machine_id
from schema.base import Base, DB_ENGINE, SESSION_MANAGER
import schema.models.meta_processor_universe as mp
import mca_tools.enums as mca_enum
from mca_tools.pid_enums import TableName as tb
from mca_tools.utils import generate_uuidv7
# from schema.mca_table_stats import record_row_count
import math
from pprint import pprint
from schema.models.file_universe import *
from schema.lookup.file_universe_lookup import *
from sqlalchemy.dialects.postgresql import insert
from mca.core.logger import set_logger
# #----- Constants -----------------------------------------------------------------

MACHINE_ID = machine_id()
logger =  set_logger(__name__)
# record_row_count()
#------------Tools-----------------------------------------------------------------------------

def db_init():
    Base.metadata.create_all(DB_ENGINE)
def drop_all_table_cascade():
    Base.metadata.drop_all(DB_ENGINE)

def count_table_rows(table):
    with SESSION_MANAGER() as session:
        count = session.scalar(select(func.count()).select_from(text(table)))
        return count

def get_fk_keys_in_table(table):
    '''Returns foreign keys column in current table with the refernced tablename and id
    { fk_column: (refernced_table, id) }'''
    keys = inspect(DB_ENGINE).get_foreign_keys(table)
    di = {}
    for i in keys:
        di[i["constrained_columns"][0]] = (i["referred_table"],i["referred_columns"][0])
    return di

def get_value_in_a_referenced_table_column(current_table, current_table_pk, fk_key, column ):
    metadata = MetaData()
    current = Table(
        current_table,
        metadata,
        autoload_with=DB_ENGINE
    )
    fk_info = get_fk_keys_in_table(current_table)
    ref_table_name, ref_pk_column = fk_info[fk_key]
    referenced = Table(
        ref_table_name,
        metadata,
        autoload_with=DB_ENGINE
    )

    current_pk_column = list(current.primary_key.columns)[0]
    with SESSION_MANAGER() as session:
        fk_value = session.execute(
            select(current.c[fk_key])
            .where(current_pk_column == current_table_pk)
        ).scalar_one()

        return session.execute(
            select(referenced.c[column])
            .where(referenced.c[ref_pk_column] == fk_value)
        ).scalar_one_or_none()

# get_value_in_a_referenced_table_column("meta_processor_runs",)

def get_column_data_with_id(tablename, id, column):
     with SESSION_MANAGER() as session:
            command = select(column).where(tablename.id == id)
            return session.execute(command).scalar_one_or_none()

# a = get_fk_keys_in_table(tb.MPR.value)
# pprint(a)


def insert_multiple_columns_data(table, column_value: dict, conflict_columns: list[str] | None = None):
    with SESSION_MANAGER() as session:
        stmt = insert(table).values(**column_value)

        if conflict_columns:
            stmt = stmt.on_conflict_do_nothing(
                index_elements=conflict_columns
            )
        else:
            stmt = stmt.on_conflict_do_nothing()
        logger.debug(session.execute(stmt))
        session.commit()

def fetch_id_by_value(table,identifying_column,value):
    with SESSION_MANAGER() as session:
        stmt = select(table.id).where(getattr(table, identifying_column) == value)
        result = session.execute(stmt)
        data = result.scalar_one_or_none()
        logger.debug(data)
        return data

def get_all_values_of_a_column_in_tb(table,column,sort_column_asc = None):
    with SESSION_MANAGER() as session:
        stmt = select(getattr(table,column)).order_by(sort_column_asc and getattr(table,sort_column_asc)) 
        result = session.execute(stmt)
        data = result.scalars().all()
        logger.debug(data)
        return data
def update_multiple_columns_data(table,id_column,id_value,column_value: dict):
    with SESSION_MANAGER() as session:
        stmt = update(table).where(getattr(table,id_column) == id_value).values(**column_value)
        result = session.execute(stmt)
        # data = result.scalar_one_or_none()
        logger.debug(result)
        session.commit()
def get_all_values_of_multiple_column_in_tb(table:Base,columns:list,sort_column_asc = None):
    with SESSION_MANAGER() as session:
        stmt = select(*[getattr(table,column) for column in columns]).order_by( sort_column_asc and getattr(table,sort_column_asc))
        result = session.execute(stmt)
        data = result.all()
        pprint(data)
        logger.debug(data)
    return data
get_all_values_of_multiple_column_in_tb(Artists,["id","name","mbid"],"created_at")
# pprint(get_all_values_of_a_column_in_tb(Artists,"mbid"))
# print(fetch_id_by_value(GenderLookup,"Mixe Group"))
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



