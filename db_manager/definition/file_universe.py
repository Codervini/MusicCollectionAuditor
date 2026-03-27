import dotenv
from app_tools.machine_identifier import  machine_id
from app_tools.enums import *
from sqlalchemy import (
    Column, Text, Boolean, SmallInteger, Integer, Date,
    String, TIMESTAMP, Index, text, Enum,
    UniqueConstraint, ForeignKey, create_engine
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base ,sessionmaker
from sqlalchemy.sql import func
from db_manager.db_connector import Base , DB_ENGINE
"""
music_library/schema.py
=======================
Song Library Module — Database Schema
26 tables: 11 lookup + 15 core

Table Hierarchy (read bottom up for authority):
    physical_files  →  recordings  →  works  (the truth)
    tracks          →  recordings  +  releases
    *_credits       →  artists    (who did what)
    tags            →  anything   (flexible labelling)

Author: Auto-generated
"""


#----- Constants -----------------------------------------------------------------
# CONFIG_CONSTANTS = dotenv.dotenv_values(".env")
# DB_ENGINE = create_engine(f"postgresql+psycopg://{CONFIG_CONSTANTS['DB_USERNAME']}:{CONFIG_CONSTANTS['DB_PASSWORD']}@localhost:5432/mcamusicdb")
# SESSION_MANAGER = sessionmaker(bind=DB_ENGINE)
# MACHINE_ID = machine_id()
# Base = declarative_base()



# ══════════════════════════════════════════════════════════════════════════════
# GROUP 2 — ARTISTS
# Artists are their own universe.
# A person or group who was involved in any musical work.
# Referenced by works, recordings, and releases via credit tables.
# ══════════════════════════════════════════════════════════════════════════════

class Artists(Base):
    """
    Every person or group who ever touched a song in this library.
    One row per unique artist — never duplicated.
    Referenced by work_credits, recording_credits, release_credits.
    """
    __tablename__ = "artists"

    id               = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name             = Column(Text, nullable=False)                 # display name e.g. "Freddie Mercury"
    sort_name        = Column(Text, nullable=True)                  # sortable e.g. "Mercury, Freddie"
    type_id          = Column(UUID(as_uuid=True), ForeignKey("artist_type_lookup.id"), nullable=True)
    gender_id        = Column(UUID(as_uuid=True), ForeignKey("gender_lookup.id"), nullable=True)
    mbid             = Column(String(36), nullable=True)            # MusicBrainz artist ID
    isni             = Column(String(16), nullable=True)            # International Standard Name Identifier
    country          = Column(String(4), nullable=True)             # ISO country code
    born_or_formed   = Column(Date, nullable=True)                  # birth or formation date
    died_or_disbanded= Column(Date, nullable=True)                  # death or disbandment date
    disambiguation   = Column(Text, nullable=True)                  # e.g. "Queen guitarist" if name clash
    raw_mb_response  = Column(JSONB, nullable=True)                 # full MusicBrainz API response
    created_at       = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at       = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_artists_mbid",      "mbid"),
        Index("ix_artists_name",      "name"),
        Index("ix_artists_sort_name", "sort_name"),
        Index("ix_artists_type_id",   "type_id"),
    )


class ArtistAliases(Base):
    """
    Alternative names for an artist.
    One row per alias. An artist can have many aliases.
    e.g. "The Weeknd" has legal name "Abel Tesfaye"
    """
    __tablename__ = "artist_aliases"

    id              = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    artist_id       = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=False)
    alias_type_id   = Column(UUID(as_uuid=True), ForeignKey("alias_types_lookup.id"), nullable=False)
    name            = Column(Text, nullable=False)                  # the alias
    sort_name       = Column(Text, nullable=True)
    locale          = Column(String(8), nullable=True)              # language/region e.g. "en_US"
    is_primary      = Column(Boolean, nullable=False, server_default=text("false"))
    created_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_artist_aliases_artist_id", "artist_id"),
        Index("ix_artist_aliases_name",      "name"),
    )


class ArtistLinks(Base):
    """
    External URLs for an artist — Spotify, Wikipedia, Instagram etc.
    One row per link per artist.
    """
    __tablename__ = "artist_links"

    id              = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    artist_id       = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=False)
    link_type_id    = Column(UUID(as_uuid=True), ForeignKey("link_types_lookup.id"), nullable=False)
    url             = Column(Text, nullable=False)
    created_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("artist_id", "link_type_id", name="uq_artist_links_artist_type"),
        Index("ix_artist_links_artist_id",    "artist_id"),
        Index("ix_artist_links_link_type_id", "link_type_id"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 3 — WORKS
# A work is the song as a pure concept.
# It exists independently of any recording, format, or release.
# "Bohemian Rhapsody" as an idea — not tied to any audio.
# ══════════════════════════════════════════════════════════════════════════════

class Works(Base):
    """
    The song concept. Pure idea, no audio.
    One row per unique song concept.
    All recordings of this song point back here.
    """
    __tablename__ = "works"

    id              = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title           = Column(Text, nullable=False)                  # song name
    type_id         = Column(UUID(as_uuid=True), ForeignKey("work_type_lookup.id"), nullable=True)
    iswc            = Column(String(15), nullable=True)             # International Standard Musical Work Code
    language        = Column(String(8), nullable=True)              # primary language ISO code
    mbid            = Column(String(36), nullable=True)             # MusicBrainz work ID
    raw_mb_response = Column(JSONB, nullable=True)                  # full MusicBrainz API response
    created_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_works_mbid",    "mbid"),
        Index("ix_works_title",   "title"),
        Index("ix_works_iswc",    "iswc"),
        Index("ix_works_type_id", "type_id"),
    )


class WorkCredits(Base):
    """
    Who was involved in creating this work concept.
    Composer, lyricist, original performer.
    One row per artist per role per work.
    """
    __tablename__ = "work_credits"

    id           = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    work_id      = Column(UUID(as_uuid=True), ForeignKey("works.id"), nullable=False)
    artist_id    = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=False)
    role_id      = Column(UUID(as_uuid=True), ForeignKey("artist_roles_lookup.id"), nullable=False)
    credit_order = Column(SmallInteger, nullable=False, server_default=text("1"))  # 1 = primary
    note         = Column(Text, nullable=True)                      # extra credit note
    created_at   = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("work_id", "artist_id", "role_id", name="uq_work_credits"),
        Index("ix_work_credits_work_id",   "work_id"),
        Index("ix_work_credits_artist_id", "artist_id"),
        Index("ix_work_credits_role_id",   "role_id"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 4 — RECORDINGS
# A recording is a specific captured version of a work.
# Studio, live, remix, remaster, cover — each is a separate recording.
# THE TRUTH. Everything else orbits this.
# AcoustID fingerprint lives here — same audio = same recording.
# ══════════════════════════════════════════════════════════════════════════════

class Recordings(Base):
    """
    Every specific version of a work ever captured.
    Studio 1975, Live Aid 1985, 2011 Remaster — three separate rows.
    AcoustID fingerprint lives here.
    All physical files point here.
    All tracks reference here.
    """
    __tablename__ = "recordings"

    id                   = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    work_id              = Column(UUID(as_uuid=True), ForeignKey("works.id"), nullable=False)
    version_type_id      = Column(UUID(as_uuid=True), ForeignKey("version_type_lookup.id"), nullable=False)
    title                = Column(Text, nullable=False)             # full title e.g. "Bohemian Rhapsody (Live Aid 1985)"
    duration_ms          = Column(Integer, nullable=True)           # duration in milliseconds
    acoustid_fingerprint = Column(Text, nullable=True)              # AcoustID audio fingerprint
    acoustid_mbid        = Column(String(36), nullable=True)        # MBID returned by AcoustID lookup
    mbid                 = Column(String(36), nullable=True)        # MusicBrainz recording ID
    isrc                 = Column(String(12), nullable=True)        # International Standard Recording Code
    language             = Column(String(8), nullable=True)         # language of this recording
    raw_mb_response      = Column(JSONB, nullable=True)             # full MusicBrainz API response
    created_at           = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at           = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_recordings_work_id",              "work_id"),
        Index("ix_recordings_mbid",                 "mbid"),
        Index("ix_recordings_isrc",                 "isrc"),
        Index("ix_recordings_acoustid_fingerprint", "acoustid_fingerprint"),
        Index("ix_recordings_acoustid_mbid",        "acoustid_mbid"),
        Index("ix_recordings_version_type_id",      "version_type_id"),
    )


class RecordingCredits(Base):
    """
    Who was involved in this specific recording.
    Main artist, featured artist, producer, remixer, conductor.
    One row per artist per role per recording.
    """
    __tablename__ = "recording_credits"

    id           = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    recording_id = Column(UUID(as_uuid=True), ForeignKey("recordings.id"), nullable=False)
    artist_id    = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=False)
    role_id      = Column(UUID(as_uuid=True), ForeignKey("artist_roles_lookup.id"), nullable=False)
    credit_order = Column(SmallInteger, nullable=False, server_default=text("1"))
    note         = Column(Text, nullable=True)
    created_at   = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("recording_id", "artist_id", "role_id", name="uq_recording_credits"),
        Index("ix_recording_credits_recording_id", "recording_id"),
        Index("ix_recording_credits_artist_id",    "artist_id"),
        Index("ix_recording_credits_role_id",      "role_id"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 5 — RELEASES
# A release is a product that was made available to the world.
# Album, single, EP, compilation, soundtrack.
# One release has many tracks. Each track links a recording to a release.
# ══════════════════════════════════════════════════════════════════════════════

class Releases(Base):
    """
    Every album, single, or EP ever released that contains
    a recording in this library.
    One row per release product.
    """
    __tablename__ = "releases"

    id              = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    title           = Column(Text, nullable=False)                  # album or single name
    type_id         = Column(UUID(as_uuid=True), ForeignKey("release_type_lookup.id"), nullable=True)
    year            = Column(SmallInteger, nullable=True)           # release year
    date            = Column(Date, nullable=True)                   # full release date if known
    label           = Column(Text, nullable=True)                   # record label
    country         = Column(String(4), nullable=True)              # ISO country code
    barcode         = Column(String(32), nullable=True)             # product barcode
    mbid            = Column(String(36), nullable=True)             # MusicBrainz release ID
    artwork_url     = Column(Text, nullable=True)                   # remote artwork URL
    artwork_local   = Column(Text, nullable=True)                   # local path if downloaded
    total_tracks    = Column(SmallInteger, nullable=True)           # total track count
    total_discs     = Column(SmallInteger, nullable=True)           # total disc count
    raw_mb_response = Column(JSONB, nullable=True)                  # full MusicBrainz API response
    created_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_releases_mbid",    "mbid"),
        Index("ix_releases_title",   "title"),
        Index("ix_releases_year",    "year"),
        Index("ix_releases_type_id", "type_id"),
        Index("ix_releases_barcode", "barcode"),
    )


class ReleaseCredits(Base):
    """
    Who is credited on this release.
    Main artist, featured artist, various artists for compilations.
    One row per artist per role per release.
    """
    __tablename__ = "release_credits"

    id           = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    release_id   = Column(UUID(as_uuid=True), ForeignKey("releases.id"), nullable=False)
    artist_id    = Column(UUID(as_uuid=True), ForeignKey("artists.id"), nullable=False)
    role_id      = Column(UUID(as_uuid=True), ForeignKey("artist_roles_lookup.id"), nullable=False)
    credit_order = Column(SmallInteger, nullable=False, server_default=text("1"))
    note         = Column(Text, nullable=True)
    created_at   = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("release_id", "artist_id", "role_id", name="uq_release_credits"),
        Index("ix_release_credits_release_id", "release_id"),
        Index("ix_release_credits_artist_id",  "artist_id"),
        Index("ix_release_credits_role_id",    "role_id"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 6 — TRACKS
# The bridge between recordings and releases.
# "Bohemian Rhapsody studio recording" sits at position 11
# on "A Night at the Opera" and position 1 on "Greatest Hits".
# Two track rows. One recording. Two releases.
# ══════════════════════════════════════════════════════════════════════════════

class Tracks(Base):
    """
    Links a recording to a release with a position number.
    This is the normalised junction that replaces having
    album_name, track_number sitting on the recording itself.
    One recording can appear on many releases — one track row each time.
    """
    __tablename__ = "tracks"

    id           = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    recording_id = Column(UUID(as_uuid=True), ForeignKey("recordings.id"), nullable=False)
    release_id   = Column(UUID(as_uuid=True), ForeignKey("releases.id"), nullable=False)
    position     = Column(SmallInteger, nullable=False)             # track number on this release
    disc_number  = Column(SmallInteger, nullable=False, server_default=text("1"))
    title        = Column(Text, nullable=True)                      # if different from recording title
    duration_ms  = Column(Integer, nullable=True)                   # if different from recording duration
    created_at   = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("recording_id", "release_id", name="uq_tracks_recording_release"),
        UniqueConstraint("release_id", "disc_number", "position", name="uq_tracks_position"),
        Index("ix_tracks_recording_id", "recording_id"),
        Index("ix_tracks_release_id",   "release_id"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 7 — PHYSICAL FILES
# The files you actually have on your disk.
# mp3, flac, opus — all pointing to the same recording.
# This is YOUR data. Everything above comes from MusicBrainz.
# This is what you own.
# ══════════════════════════════════════════════════════════════════════════════

class PhysicalFiles(Base):
    """
    Your actual audio files on disk.
    Multiple formats of the same recording all point to the same recording_id.
    This is the only table in this module that represents YOUR data
    rather than MusicBrainz data.
    """
    __tablename__ = "physical_files"

    id              = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    recording_id    = Column(UUID(as_uuid=True), ForeignKey("recordings.id"), nullable=False)
    format_id       = Column(UUID(as_uuid=True), ForeignKey("file_format_lookup.id"), nullable=False)
    file_path       = Column(Text, nullable=False)                  # full path on disk
    file_hash       = Column(String(64), nullable=False)            # SHA-256 whole file
    audio_hash      = Column(String(64), nullable=True)             # SHA-256 audio stream only
    file_size_bytes = Column(Integer, nullable=True)
    bitrate         = Column(Integer, nullable=True)                # kbps
    sample_rate     = Column(Integer, nullable=True)                # Hz
    channels        = Column(SmallInteger, nullable=True)
    duration_ms     = Column(Integer, nullable=True)
    added_at        = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_physical_files_recording_id", "recording_id"),
        Index("ix_physical_files_file_hash",    "file_hash"),
        Index("ix_physical_files_audio_hash",   "audio_hash"),
        Index("ix_physical_files_format_id",    "format_id"),
        Index(
            "ix_physical_files_duplicates",
            "audio_hash",
            postgresql_where=text("audio_hash IS NOT NULL")
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 8 — TAGS
# Flexible labelling system for any entity.
# One table serves works, recordings, releases, artists.
# entity_type tells you which table entity_id points to.
# ══════════════════════════════════════════════════════════════════════════════

class Tags(Base):
    """
    A tag can attach to any entity — work, recording, release, artist.
    entity_type_id tells you which table entity_id refers to.
    source_id tells you where the tag came from — MusicBrainz, user, Last.fm etc.
    """
    __tablename__ = "tags"

    id             = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    entity_type_id = Column(UUID(as_uuid=True), ForeignKey("entity_type_lookup.id"), nullable=False)
    entity_id      = Column(UUID(as_uuid=True), nullable=False)     # points to whichever table
    tag            = Column(String(64), nullable=False)             # the tag value e.g. "rock"
    source_id      = Column(UUID(as_uuid=True), ForeignKey("tag_source_lookup.id"), nullable=False)
    created_at     = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("entity_type_id", "entity_id", "tag", "source_id", name="uq_tags"),
        Index("ix_tags_entity_id",      "entity_id"),
        Index("ix_tags_entity_type_id", "entity_type_id"),
        Index("ix_tags_tag",            "tag"),
        Index("ix_tags_source_id",      "source_id"),
    )





# Base.metadata.create_all(DB_ENGINE)