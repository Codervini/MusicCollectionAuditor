import dotenv
from sqlalchemy import (
    Column, Text, Boolean, SmallInteger, Numeric,
    String, TIMESTAMP, ARRAY, Index, text, create_engine, Enum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum  # Python's built-in enum — used to define the values

CONFIG_CONSTANTS = dotenv.dotenv_values(".env")

db_engine = create_engine(
    f"postgresql+psycopg://{CONFIG_CONSTANTS['DB_USERNAME']}:"
    f"{CONFIG_CONSTANTS['DB_PASSWORD']}@localhost/mcamusicdb"
)

BASE = declarative_base()


# ── ENUMs ────────────────────────────────────────────────────────────────────
# These are Python enums that SQLAlchemy mirrors as Postgres ENUMs in the DB.
# The DB will REJECT any value not in this list — no more typo bugs.

class ProcessorStatus(enum.Enum):
    pending    = "pending"
    processing = "processing"
    completed  = "completed"
    failed     = "failed"
    skipped    = "skipped"

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

class Meta_Processor_Table(BASE):
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
    # NOTE: updated_at does NOT auto-update via onupdate= in Postgres.
    # The trigger below (after_create) handles this reliably instead.

    # ── Pipeline state ───────────────────────────────────────────────
    # ENUM: DB will reject anything not in ProcessorStatus
    status = Column(
        Enum(ProcessorStatus, name="processor_status"),
        nullable=False,
        server_default="pending"
    )
    current_stage = Column(String(64))                      # active node name
    # ENUM: DB will reject anything not in SaveType
    save_type = Column(
        Enum(SaveType, name="save_type"),
        nullable=True
    )
    error_message = Column(Text)
    retry_count   = Column(SmallInteger, server_default=text("0"))

    # ── Source tags (READ_FILE) ──────────────────────────────────────
    source_mbid  = Column(String(36))
    source_artist = Column(Text)
    source_title  = Column(Text)
    has_mbid  = Column(Boolean, server_default=text("false"))
    has_tags  = Column(Boolean, server_default=text("false"))
    mbid_valid = Column(Boolean)                            # NULL = unchecked

    # ── Fingerprint (AcoustID) ───────────────────────────────────────
    acoustid_fingerprint = Column(Text)
    acoustid_score       = Column(Numeric(4, 3))            # 0.000–1.000
    # ENUM: only 'found' or 'not_found' allowed
    acoustid_result = Column(
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
    # ENUM: fully_found | partially_found | not_found
    # Each service gets the same ENUM type — they share one Postgres ENUM
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
        Index("ix_meta_processor_source_mbid",   "source_mbid"),
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

# ── Create everything ─────────────────────────────────────────────────────────
BASE.metadata.create_all(db_engine)


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


