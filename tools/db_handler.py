from sqlalchemy.orm import declarative_base
import dotenv
import uuid
from sqlalchemy import (
    Column, Text, Boolean, SmallInteger, Numeric,
    String, TIMESTAMP, ARRAY, Index, text, create_engine
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy import text


CONFIG_CONSTANTS = dotenv.dotenv_values(".env")


db_engine = create_engine(f"postgresql+psycopg://{CONFIG_CONSTANTS['DB_USERNAME']}:{CONFIG_CONSTANTS['DB_PASSWORD']}@localhost/mcamusicdb")

BASE = declarative_base()


class Base(DeclarativeBase):
    pass


#Table definitions

class Meta_Processor_Table(BASE):
    __tablename__ = "meta_processor"

    # file = Column(String, primary_key=True)
    # has_musicbrainz_id = Column(Boolean, default=False)
    # has_artist_and_title = Column(Boolean, default=False)
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
        # server_default=text("uuid_generate_v4()"),
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    file_path = Column(Text, nullable=False, unique=True)
    file_hash = Column(String(64))                        # SHA-256
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ── Pipeline state ───────────────────────────────────────────────
    status = Column(String(32), nullable=False, server_default="pending")
    # pending | processing | full_save | incomplete_save | error
    current_stage = Column(String(64))                    # active node name
    save_type = Column(String(16))                        # 'full' | 'incomplete'
    error_message = Column(Text)
    retry_count = Column(SmallInteger, server_default=text("0"))

    # ── Source tags (READ_FILE) ──────────────────────────────────────
    source_mbid = Column(String(36))
    source_artist = Column(Text)
    source_title = Column(Text)
    has_mbid = Column(Boolean, server_default=text("false"))      # HAS_MBID decision
    has_tags = Column(Boolean, server_default=text("false"))      # HAS_TAGS decision
    mbid_valid = Column(Boolean)                                  # NULL = unchecked

    # ── Fingerprint (AcoustID) ───────────────────────────────────────
    acoustid_fingerprint = Column(Text)
    acoustid_score = Column(Numeric(4, 3))                # 0.000–1.000
    acoustid_result = Column(String(16))                  # 'found' | 'not_found'

    # ── Resolved metadata ────────────────────────────────────────────
    resolved_mbid = Column(String(36))
    resolved_artist = Column(Text)
    resolved_title = Column(Text)
    resolved_album = Column(Text)
    resolved_year = Column(SmallInteger)
    resolved_track_number = Column(SmallInteger)
    resolved_genre = Column(ARRAY(Text))                  # multiple genres
    resolved_isrc = Column(String(12))
    resolution_source = Column(String(32))                # which service won

    # ── Search results per service (MERGE_ENRICH) ────────────────────
    mb_search_result = Column(String(16))                 # fully_found | partially_found | not_found
    itunes_result = Column(String(16))
    lastfm_result = Column(String(16))
    spotify_result = Column(String(16))
    discogs_result = Column(String(16))
    audiodb_result = Column(String(16))
    deezer_result = Column(String(16))
    youtube_result = Column(String(16))
    # service_payloads = Column(JSONB)                      # raw API responses keyed by service
    service_payloads = Column(JSONB, nullable=False, server_default=_EMPTY_PAYLOADS)


    # ── Artwork ───────────────────────────────────────────────────────
    has_artwork = Column(Boolean, server_default=text("false"))   # HAS_ARTWORK decision
    artwork_source = Column(String(32))                   # which service provided art
    artwork_url = Column(Text)
    artwork_local_path = Column(Text)
    art_caa_result = Column(Boolean)                      # Cover Art Archive
    art_itunes_result = Column(Boolean)
    art_spotify_result = Column(Boolean)
    art_audiodb_result = Column(Boolean)
    art_discogs_result = Column(Boolean)
    art_deezer_result = Column(Boolean)
    art_lastfm_result = Column(Boolean)

    # ── Manual review ─────────────────────────────────────────────────
    needs_manual_review = Column(Boolean, server_default=text("false"))
    manual_review_reason = Column(Text)
    manual_reviewed_at = Column(TIMESTAMP(timezone=True))
    manual_reviewed_by = Column(Text)
    manual_has_artwork = Column(Boolean)                  # MANUAL_HAS_ARTWORK decision

    # ── Indexes ───────────────────────────────────────────────────────
    __table_args__ = (
        Index("ix_meta_processor_status", "status"),
        Index("ix_meta_processor_source_mbid", "source_mbid"),
        Index("ix_meta_processor_resolved_mbid", "resolved_mbid"),
        Index("ix_meta_processor_file_hash", "file_hash"),
        Index("ix_meta_processor_needs_manual_review", "needs_manual_review"),
    )



BASE.metadata.create_all(db_engine)