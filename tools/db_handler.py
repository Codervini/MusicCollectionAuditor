import dotenv
from sqlalchemy import (
    Column, Text, Boolean, SmallInteger, Numeric,
    String, TIMESTAMP, ARRAY, Index, text, create_engine, Enum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, base
from sqlalchemy.sql import func
import enum  # Python's built-in enum — used to define the values
import hashlib

#----- Constants -----------------------------------------------------------------
CONFIG_CONSTANTS = dotenv.dotenv_values(".env")
DB_ENGINE = create_engine(f"postgresql+psycopg://{CONFIG_CONSTANTS['DB_USERNAME']}:{CONFIG_CONSTANTS['DB_PASSWORD']}@localhost/mcamusicdb")
SESSION_MANAGER = sessionmaker(bind=DB_ENGINE)
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
    file_path  = Column(Text, nullable=False, unique=True)
    file_hash  = Column(String(64))                         # SHA-256
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # ── Pipeline state ───────────────────────────────────────────────
    status = Column(
        Enum(ProcessorStatus, name="processor_status"),
        nullable=False,
        server_default="pending"
    )
    current_stage = Column(String(64))                      # active node name
    save_type = Column(                                     # ENUM: DB will reject anything not in SaveType
        Enum(SaveType, name="save_type"),
        nullable=True
    )
    error_message = Column(Text)
    retry_count   = Column(SmallInteger, server_default=text("0"))

    # ── Source tags (READ_FILE) ──────────────────────────────────────
    source_track_mbid  = Column(String(36))
    source_album_mbid = Column(String(36))
    source_artist = Column(Text)
    source_title  = Column(Text)
    has_track_mbid  = Column(Boolean, server_default=text("false"))
    has_album_mbid  = Column(Boolean, server_default=text("false"))
    has_artist_and_title_tags  = Column(Boolean, server_default=text("false"))
    track_mbid_valid = Column(Boolean)          # NULL = unchecked
    album_mbid_valid = Column(Boolean)

    # ── Fingerprint (AcoustID) ───────────────────────────────────────
    acoustid_fingerprint = Column(Text)
    acoustid_score       = Column(Numeric(4, 3))            # 0.000–1.000
    acoustid_result = Column(                               # ENUM: only 'found' or 'not_found' allowed
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
    resolved_genre        = Column(ARRAY(Text))             # multiple genres
    resolved_isrc         = Column(String(12))
    resolution_source     = Column(String(32))              # which service won

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
    needs_manual_review = Column(Boolean, server_default=text("false"))
    manual_review_reason = Column(Text)
    manual_reviewed_at   = Column(TIMESTAMP(timezone=True))
    manual_reviewed_by   = Column(Text)
    manual_has_artwork   = Column(Boolean)

    # ── Indexes ───────────────────────────────────────────────────────
    __table_args__ = (

        # Normal indexes — search across ALL rows
        Index("ix_meta_processor_source_track_mbid",   "source_track_mbid"),
        Index("ix_meta_processor_resolved_mbid",  "resolved_mbid"),
        Index("ix_meta_processor_file_hash",      "file_hash"),

        # PARTIAL index — only indexes rows WHERE status IN ('pending','failed')
        # At 1M songs, maybe 10% are pending/failed at any time.
        # This index is 10x smaller than a full status index.
        # Your queue worker query hits this index directly.
        Index(
            "ix_processing_queue",
            "created_at",
            postgresql_where=text("status IN ('pending', 'failed')")
        ),

        # PARTIAL index — only indexes rows WHERE needs_manual_review = true
        # Maybe 5% of songs need review. No point indexing the other 95%.
        Index(
            "ix_manual_review_pending",
            "id",
            postgresql_where=text("needs_manual_review = true")
        ),
    )
Base.metadata.create_all(DB_ENGINE)


#------------Tools-----------------------------------------------------------------------------

def db_init():
    Base.metadata.create_all(DB_ENGINE)


class Song:
    def __init__(self, song_path:str, source_artist:str=None, source_title:str=None,
                source_track_mbid:str = None, track_mbid_valid:bool = None,
                source_album_mbid:str=None, album_mbid_valid:bool = None):
        
        with open(song_path,"rb") as f:
            file_hash  = hashlib.sha256(f.read()).hexdigest()
          
        with SESSION_MANAGER() as session:
            record = Meta_Processor_Table(
                file_path  = song_path,
                file_hash = file_hash,
                status  = ProcessorStatus.pending,
                current_stage = "READ_FILE",

                source_track_mbid   = source_track_mbid,
                source_album_mbid = source_album_mbid,
                source_artist = source_artist,
                source_title  = source_title,

                has_track_mbid  = bool(source_track_mbid),
                has_album_mbid   = bool(source_album_mbid),
                has_artist_and_title_tags = bool(source_artist and source_title),
                track_mbid_valid  = track_mbid_valid,
                album_mbid_valid  = album_mbid_valid
            )
            session.add(record)
            session.commit() 













































# ── updated_at trigger ────────────────────────────────────────────────────────
# onupdate=func.now() in SQLAlchemy does NOT create a DB trigger.
# It only works when you update via SQLAlchemy ORM — raw SQL updates ignore it.
# This trigger fires on EVERY update, no matter how the row is changed.

# from sqlalchemy import event

# def _create_updated_at_trigger(target, connection, **kw):
#     connection.execute(text("""
#         CREATE OR REPLACE FUNCTION touch_updated_at()
#         RETURNS trigger LANGUAGE plpgsql AS $$
#         BEGIN
#             NEW.updated_at = now();
#             RETURN NEW;
#         END;
#         $$;
#     """))
#     connection.execute(text("""
#         DROP TRIGGER IF EXISTS trg_meta_processor_updated_at
#         ON meta_processor;
#     """))
#     connection.execute(text("""
#         CREATE TRIGGER trg_meta_processor_updated_at
#         BEFORE UPDATE ON meta_processor
#         FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
#     """))

# # Runs once, right after create_all() creates the table
# event.listen(Meta_Processor_Table.__table__, "after_create", _create_updated_at_trigger)


