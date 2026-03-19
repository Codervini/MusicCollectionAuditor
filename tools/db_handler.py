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
from machine_identifier import  machine_id
#----- Constants -----------------------------------------------------------------
CONFIG_CONSTANTS = dotenv.dotenv_values(".env")
DB_ENGINE = create_engine(f"postgresql+psycopg://{CONFIG_CONSTANTS['DB_USERNAME']}:{CONFIG_CONSTANTS['DB_PASSWORD']}@localhost/mcamusicdb")
SESSION_MANAGER = sessionmaker(bind=DB_ENGINE)
MACHINE_ID = machine_id()
Base = declarative_base()
# class Base(base):
#     pass

class ProcessorStatus(enum.Enum):
    pending    = "pending"
    processing = "processing"
    completed  = "completed"
    failed     = "failed"
    skipped    = "skipped"
    duplicate  = "duplicate"

class PipelineStage(enum.Enum):
    read_file    = "read_file"
    acoustid     = "acoustid"
    merge_enrich = "merge_enrich"
    artwork      = "artwork"
    finalize     = "finalize"

class HashChangedBy(enum.Enum):
    software = "software"
    external = "external"

class AcoustidResult(enum.Enum):
    found     = "found"
    not_found = "not_found"

class ServiceResult(enum.Enum):
    fully_found     = "fully_found"
    partially_found = "partially_found"
    not_found       = "not_found"

class SaveType(enum.Enum):
    full       = "full"
    incomplete = "incomplete"


# ── Table ─────────────────────────────────────────────────────────────────────

class Meta_Processor_Table(Base):
    __tablename__ = "meta_processor"

    _EMPTY_PAYLOADS = text("""
        '{
            "itunes":   {},
            "lastfm":   {},
            "spotify":  {},
            "discogs":  {},
            "audiodb":  {},
            "deezer":   {},
            "youtube":  {}
        }'::jsonb
    """)

    # ── Identity & file ──────────────────────────────────────────────
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    machine_id        = Column(String(64), nullable=False)
    file_path         = Column(Text, nullable=False)
    file_hash         = Column(String(64), nullable=False)          # SHA-256 current
    last_known_hash   = Column(String(64))                          # SHA-256 before external change
    hash_changed_by   = Column(                                     # who last changed the hash
        Enum(HashChangedBy, name="hash_changed_by"),
        nullable=True
    )
    is_duplicate_of   = Column(UUID(as_uuid=True), ForeignKey("meta_processor.id"), nullable=True)
    created_at        = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at        = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    last_scanned_at   = Column(TIMESTAMP(timezone=True))            # updated every scan

    # ── Pipeline state ───────────────────────────────────────────────
    status = Column(
        Enum(ProcessorStatus, name="processor_status"),
        nullable=False,
        server_default="pending"
    )
    current_stage = Column(
        Enum(PipelineStage, name="pipeline_stage"),
        nullable=True
    )
    save_type = Column(
        Enum(SaveType, name="save_type"),
        nullable=True
    )

    # ── Error tracking ───────────────────────────────────────────────
    error_message   = Column(Text)                                  # human readable summary
    error_stage     = Column(                                       # which stage failed
        Enum(PipelineStage, name="pipeline_stage"),
        nullable=True
    )
    error_type      = Column(String(69))                            # network | timeout | parsing | db | unknown
    error_traceback = Column(Text)                                  # full Python traceback
    last_failed_at  = Column(TIMESTAMP(timezone=True))              # when last failure occurred
    retry_count     = Column(SmallInteger, server_default=text("0"))

    # ── Source tags (READ_FILE) ──────────────────────────────────────
    source_track_mbid         = Column(String(36))
    source_album_mbid         = Column(String(36))
    source_artist             = Column(Text)
    source_title              = Column(Text)
    has_track_mbid            = Column(Boolean, server_default=text("false"))
    has_album_mbid            = Column(Boolean, server_default=text("false"))
    has_artist_and_title_tags = Column(Boolean, server_default=text("false"))
    track_mbid_valid          = Column(Boolean)                     # NULL = unchecked
    album_mbid_valid          = Column(Boolean)

    # ── Fingerprint (AcoustID) ───────────────────────────────────────
    acoustid_fingerprint = Column(Text)
    acoustid_score       = Column(Numeric(4, 3))                    # 0.000–1.000
    acoustid_result      = Column(
        Enum(AcoustidResult, name="acoustid_result"),
        nullable=True
    )

    # ── Resolved metadata ────────────────────────────────────────────
    resolved_mbid         = Column(String(36))
    resolved_artist       = Column(Text)
    resolved_title        = Column(Text)
    resolved_album        = Column(Text)
    resolved_year         = Column(SmallInteger)
    resolved_track_number = Column(SmallInteger)
    resolved_genre        = Column(ARRAY(Text))                     # multiple genres
    resolved_isrc         = Column(String(12))
    resolution_source     = Column(String(32))                      # which service won

    # ── Search results per service (MERGE_ENRICH) ────────────────────
    mb_search_result = Column(Enum(ServiceResult, name="service_result"), nullable=True)
    itunes_result    = Column(Enum(ServiceResult, name="service_result"), nullable=True)
    lastfm_result    = Column(Enum(ServiceResult, name="service_result"), nullable=True)
    spotify_result   = Column(Enum(ServiceResult, name="service_result"), nullable=True)
    discogs_result   = Column(Enum(ServiceResult, name="service_result"), nullable=True)
    audiodb_result   = Column(Enum(ServiceResult, name="service_result"), nullable=True)
    deezer_result    = Column(Enum(ServiceResult, name="service_result"), nullable=True)
    youtube_result   = Column(Enum(ServiceResult, name="service_result"), nullable=True)

    service_payloads = Column(JSONB, nullable=False, server_default=_EMPTY_PAYLOADS)

    # ── Artwork ───────────────────────────────────────────────────────
    has_artwork        = Column(Boolean, server_default=text("false"))
    artwork_source     = Column(String(32))
    artwork_url        = Column(Text)
    artwork_local_path = Column(Text)
    art_caa_result     = Column(Boolean)
    art_itunes_result  = Column(Boolean)
    art_spotify_result = Column(Boolean)
    art_audiodb_result = Column(Boolean)
    art_discogs_result = Column(Boolean)
    art_deezer_result  = Column(Boolean)
    art_lastfm_result  = Column(Boolean)

    # ── Manual review ─────────────────────────────────────────────────
    needs_manual_review  = Column(Boolean, server_default=text("false"))
    manual_review_reason = Column(Text)
    manual_reviewed_at   = Column(TIMESTAMP(timezone=True))
    manual_reviewed_by   = Column(Text)
    manual_has_artwork   = Column(Boolean)

    # ── Indexes ───────────────────────────────────────────────────────
    __table_args__ = (

        # Composite unique — one row per file per machine
        UniqueConstraint("machine_id", "file_path", name="uq_machine_file"),

        # Normal indexes
        Index("ix_meta_processor_machine_id",       "machine_id"),
        Index("ix_meta_processor_source_track_mbid", "source_track_mbid"),
        Index("ix_meta_processor_resolved_mbid",     "resolved_mbid"),
        Index("ix_meta_processor_file_hash",         "file_hash"),
        Index("ix_meta_processor_is_duplicate_of",   "is_duplicate_of"),

        # Partial index — pending/failed queue
        Index(
            "ix_processing_queue",
            "created_at",
            postgresql_where=text("status IN ('pending', 'failed')")
        ),

        # Partial index — manual review queue
        Index(
            "ix_manual_review_pending",
            "id",
            postgresql_where=text("needs_manual_review = true")
        ),
    )


# ── 1. updated_at trigger ─────────────────────────────────────────────────────
# Fires on EVERY update regardless of whether it came from ORM or raw SQL

def _create_updated_at_trigger(target, connection, **kw):
    connection.execute(text("""
        CREATE OR REPLACE FUNCTION touch_updated_at()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$;
    """))
    connection.execute(text("""
        DROP TRIGGER IF EXISTS trg_meta_processor_updated_at
        ON meta_processor;
    """))
    connection.execute(text("""
        CREATE TRIGGER trg_meta_processor_updated_at
        BEFORE UPDATE ON meta_processor
        FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
    """))

#event.listen(Meta_Processor_Table.__table__, "after_create", _create_updated_at_trigger)


# ── 2. last_scanned_at trigger ────────────────────────────────────────────────
# Automatically sets last_scanned_at = now() on every update
# So you never forget to update it manually in your scan logic

# def _create_last_scanned_at_trigger(target, connection, **kw):
#     connection.execute(text("""
#         CREATE OR REPLACE FUNCTION touch_last_scanned_at()
#         RETURNS trigger LANGUAGE plpgsql AS $$
#         BEGIN
#             NEW.last_scanned_at = now();
#             RETURN NEW;
#         END;
#         $$;
#     """))
#     connection.execute(text("""
#         DROP TRIGGER IF EXISTS trg_meta_processor_last_scanned_at
#         ON meta_processor;
#     """))
#     connection.execute(text("""
#         CREATE TRIGGER trg_meta_processor_last_scanned_at
#         BEFORE UPDATE ON meta_processor
#         FOR EACH ROW EXECUTE FUNCTION touch_last_scanned_at();
#     """))

#event.listen(Meta_Processor_Table.__table__, "after_create", _create_last_scanned_at_trigger)


# ── 3. hash_changed_by auto-clear trigger ─────────────────────────────────────
# When file_hash changes AND hash_changed_by is NULL,
# it means something external changed the file — auto set hash_changed_by = 'external'
# When your software changes the hash, it sets hash_changed_by = 'software' explicitly
# After reprocessing completes, reset hash_changed_by back to NULL automatically

def _create_hash_changed_by_trigger(target, connection, **kw):
    connection.execute(text("""
        CREATE OR REPLACE FUNCTION manage_hash_changed_by()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            -- hash changed but nobody claimed it → must be external
            IF NEW.file_hash <> OLD.file_hash AND NEW.hash_changed_by IS NULL THEN
                NEW.hash_changed_by = 'external';
                NEW.last_known_hash = OLD.file_hash;
            END IF;

            -- processing completed → clear the flag, it's been handled
            IF NEW.status = 'completed' THEN
                NEW.hash_changed_by = NULL;
            END IF;

            RETURN NEW;
        END;
        $$;
    """))
    connection.execute(text("""
        DROP TRIGGER IF EXISTS trg_meta_processor_hash_changed_by
        ON meta_processor;
    """))
    connection.execute(text("""
        CREATE TRIGGER trg_meta_processor_hash_changed_by
        BEFORE UPDATE ON meta_processor
        FOR EACH ROW EXECUTE FUNCTION manage_hash_changed_by();
    """))

#event.listen(Meta_Processor_Table.__table__, "after_create", _create_hash_changed_by_trigger)


# ── 4. last_failed_at trigger ─────────────────────────────────────────────────
# Automatically stamps last_failed_at whenever status transitions to 'failed'
# No need to set it manually in your error handling code

def _create_last_failed_at_trigger(target, connection, **kw):
    connection.execute(text("""
        CREATE OR REPLACE FUNCTION touch_last_failed_at()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.status = 'failed' AND OLD.status <> 'failed' THEN
                NEW.last_failed_at = now();
            END IF;
            RETURN NEW;
        END;
        $$;
    """))
    connection.execute(text("""
        DROP TRIGGER IF EXISTS trg_meta_processor_last_failed_at
        ON meta_processor;
    """))
    connection.execute(text("""
        CREATE TRIGGER trg_meta_processor_last_failed_at
        BEFORE UPDATE ON meta_processor
        FOR EACH ROW EXECUTE FUNCTION touch_last_failed_at();
    """))

event.listen(Meta_Processor_Table.__table__, "after_create", _create_last_failed_at_trigger)


# ── 5. retry_count trigger ────────────────────────────────────────────────────
# Automatically increments retry_count every time status goes back to 'pending'
# from 'failed' — so you never manually track retries in your code

def _create_retry_count_trigger(target, connection, **kw):
    connection.execute(text("""
        CREATE OR REPLACE FUNCTION increment_retry_count()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.status = 'pending' AND OLD.status = 'failed' THEN
                NEW.retry_count = OLD.retry_count + 1;
            END IF;
            RETURN NEW;
        END;
        $$;
    """))
    connection.execute(text("""
        DROP TRIGGER IF EXISTS trg_meta_processor_retry_count
        ON meta_processor;
    """))
    connection.execute(text("""
        CREATE TRIGGER trg_meta_processor_retry_count
        BEFORE UPDATE ON meta_processor
        FOR EACH ROW EXECUTE FUNCTION increment_retry_count();
    """))

#event.listen(Meta_Processor_Table.__table__, "after_create", _create_retry_count_trigger)

Base.metadata.create_all(DB_ENGINE)


#------------Tools-----------------------------------------------------------------------------

def db_init():
    Base.metadata.create_all(DB_ENGINE)
def drop_all_table_cascade():
    Base.metadata.drop_all(DB_ENGINE)


class Song:
    def __init__(self, song_path:str, source_artist:str=None, source_title:str=None,
                source_track_mbid:str = None, track_mbid_valid:bool = None,
                source_album_mbid:str=None, album_mbid_valid:bool = None):

        self.set_column_data(func.now(),Meta_Processor_Table.last_scanned_at,MACHINE_ID,song_path)
        
        if not MACHINE_ID:
            print("Something is wrong with machine ID, aborting!!")
        else:  
            with open(song_path,"rb") as f:
                file_hash  = hashlib.sha256(f.read()).hexdigest()
                #Compare hash function
                table_file_hash = self.fetch_column_data(Meta_Processor_Table.file_hash,MACHINE_ID,song_path)
                if table_file_hash != file_hash and table_file_hash != False:
                    self.set_column_data(HashChangedBy.external,Meta_Processor_Table.hash_changed_by,MACHINE_ID,song_path)
                    self.set_column_data(table_file_hash,Meta_Processor_Table.last_known_hash,MACHINE_ID,song_path)
                    self.set_column_data(file_hash,Meta_Processor_Table.file_hash,MACHINE_ID,song_path)

            table_file_path = self.fetch_column_data(Meta_Processor_Table.file_path,MACHINE_ID,song_path)
            table_machine_id = self.fetch_column_data(Meta_Processor_Table.machine_id,MACHINE_ID,song_path)
            if table_file_hash and table_machine_id:
                print("Row already present")
            else:
                with SESSION_MANAGER() as session:
                    record = Meta_Processor_Table(

                        #Process info
                        machine_id = MACHINE_ID,
                        file_path  = song_path,
                        file_hash = file_hash,
                        status  = ProcessorStatus.pending,
                        current_stage = PipelineStage.read_file,

                        #Source file info
                        source_track_mbid   = source_track_mbid,
                        source_album_mbid = source_album_mbid,
                        source_artist = source_artist,
                        source_title  = source_title,

                        #Source Validation
                        has_track_mbid  = bool(source_track_mbid),
                        has_album_mbid   = bool(source_album_mbid),
                        has_artist_and_title_tags = bool(source_artist and source_title),
                        track_mbid_valid  = track_mbid_valid,
                        album_mbid_valid  = album_mbid_valid
                    )
                    session.add(record)
                    session.commit()

    def truncate_table():
        pass


    def fetch_column_data(self,column, machine_id, file_path):
        with SESSION_MANAGER() as session:
            command = select(column).where(
                Meta_Processor_Table.machine_id == machine_id,
                Meta_Processor_Table.file_path == file_path
            )
            return session.execute(command).scalar_one_or_none()

    def set_column_data(self,value,column, machine_id, file_path):
        with SESSION_MANAGER() as session:
            select_command = select(Meta_Processor_Table).where(
                Meta_Processor_Table.machine_id == machine_id,
                Meta_Processor_Table.file_path  == file_path
            )
            row = session.execute(select_command).scalar_one_or_none()
            if row:
                print(row)
                setattr(row, column.key, value)     # row.column = value
                if column.key != "last_scanned_at":
                    row.updated_at = func.now()            
            else:
                print("No row found", row)
            session.commit()


