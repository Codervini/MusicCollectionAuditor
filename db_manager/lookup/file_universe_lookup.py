import dotenv
from tools.machine_identifier import  machine_id
from tools.enums import *
from sqlalchemy import (
    Column, Text, Boolean, SmallInteger, Integer, Date,
    String, TIMESTAMP, Index, text, Enum,
    UniqueConstraint, ForeignKey, create_engine
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base ,sessionmaker
from sqlalchemy.sql import func

#----- Constants -----------------------------------------------------------------
CONFIG_CONSTANTS = dotenv.dotenv_values(".env")
DB_ENGINE = create_engine(f"postgresql+psycopg://{CONFIG_CONSTANTS['DB_USERNAME']}:{CONFIG_CONSTANTS['DB_PASSWORD']}@localhost:5432/mcamusicdb")
SESSION_MANAGER = sessionmaker(bind=DB_ENGINE)
MACHINE_ID = machine_id()
Base = declarative_base()



# ══════════════════════════════════════════════════════════════════════════════
# GROUP 1 — LOOKUP TABLES
# These are the "dictionaries" of the system.
# Every table that would have had an ENUM column
# now references one of these instead.
# Adding a new value = INSERT one row, no schema migration needed.
# ══════════════════════════════════════════════════════════════════════════════

class ArtistTypeLookup(Base):
    """
    What kind of entity an artist is.
    person, group, orchestra, choir, character
    """
    __tablename__ = "artist_type_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class GenderLookup(Base):
    """
    Gender of a person artist.
    male, female, non_binary, not_applicable
    """
    __tablename__ = "gender_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class WorkTypeLookup(Base):
    """
    What kind of musical work this is.
    song, aria, symphony, soundtrack, jingle, poem, spoken_word
    """
    __tablename__ = "work_type_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class VersionTypeLookup(Base):
    """
    What kind of recording version this is.
    original, live, remix, remaster, cover, acoustic,
    instrumental, medley, demo, radio_edit, extended
    """
    __tablename__ = "version_type_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class ReleaseTypeLookup(Base):
    """
    What kind of release product this is.
    album, single, ep, compilation, soundtrack,
    live_album, remix_album, mixtape, bootleg, other
    """
    __tablename__ = "release_type_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class FileFormatLookup(Base):
    """
    Audio file format.
    mp3, flac, opus, ogg, wav, aac, m4a, wma, ape, dsf
    """
    __tablename__ = "file_format_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(16), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_lossless = Column(Boolean, nullable=False, server_default=text("false"))
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class TagSourceLookup(Base):
    """
    Where a tag came from.
    musicbrainz, user, acoustid, lastfm, discogs
    """
    __tablename__ = "tag_source_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class EntityTypeLookup(Base):
    """
    Which table a tag or link points to.
    work, recording, release, artist
    """
    __tablename__ = "entity_type_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    table_name  = Column(String(64), nullable=False)                # actual db table name
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class AliasTypeLookup(Base):
    """
    What kind of alias an artist name is.
    artist_name, legal_name, search_hint, performance_name, abbreviation
    """
    __tablename__ = "alias_types_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class LinkTypeLookup(Base):
    """
    External platform or URL type for an artist.
    spotify, wikipedia, discogs, wikidata, youtube,
    instagram, official_site, soundcloud, bandcamp,
    lastfm, allmusic, twitter, facebook, tiktok
    """
    __tablename__ = "link_types_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    base_url    = Column(Text, nullable=True)                       # e.g. https://open.spotify.com/artist/
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


class ArtistRolesLookup(Base):
    """
    Every possible role an artist can have on a work, recording, or release.
    composer, lyricist, main_artist, featured, producer,
    remixer, arranger, conductor, orchestra, cover_artist,
    original_performer, mix_engineer, mastering_engineer
    """
    __tablename__ = "artist_roles_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name        = Column(String(64), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at  = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())



Base.metadata.create_all(DB_ENGINE)