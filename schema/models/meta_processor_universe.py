"""
MCA Meta Processor Module — SQLAlchemy Schema
===============================================
23 core tables + 28 lookup tables.
"""

from sqlalchemy import (
    Column, String, Text, Integer, SmallInteger, Boolean, Numeric,
    TIMESTAMP, Index, UniqueConstraint, ForeignKey, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import text, func
from schema.base import Base


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 1 — RUN LEVEL
# ══════════════════════════════════════════════════════════════════════════════

class MetaProcessorRuns(Base):
    """
    Central truth table for this module. One row per processing attempt per file.
    This is the accountant — it holds live state and FKs out to every detail table.
    If a file is reprocessed it gets a new row; meta_processor_reprocess_log links them.
    """
    __tablename__ = "meta_processor_runs"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False)
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    file_universe_id        = Column(UUID(as_uuid=True), ForeignKey("file_universe.id"), nullable=False)
    song_library_id         = Column(UUID(as_uuid=True), nullable=True)           # filled when promoted

    # ── Run context ───────────────────────────────────────────────────
    trigger                 = Column(String(64), ForeignKey("run_trigger_lookup.id"), nullable=False)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    triggered_by_user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id              = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=True)

    # ── Live pipeline state ───────────────────────────────────────────
    status                  = Column(String(64), ForeignKey("processor_status_lookup.id"), nullable=False, server_default="pending")
    current_stage           = Column(String(64), ForeignKey("pipeline_stage_lookup.id"), nullable=True)
    current_phase           = Column(String(64), ForeignKey("pipeline_phase_lookup.id"), nullable=True)
    current_step            = Column(String(64), ForeignKey("pipeline_step_lookup.id"), nullable=True)

    # ── Timestamps ───────────────────────────────────────────────────
    created_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    completed_at            = Column(TIMESTAMP(timezone=True), nullable=True)

    # ── Outcome FKs ──────────────────────────────────────────────────
    file_ingest_id          = Column(UUID(as_uuid=True), ForeignKey("file_ingest_log.id"), nullable=True)
    resolved_metadata_id    = Column(UUID(as_uuid=True), ForeignKey("resolved_metadata.id"), nullable=True)
    artwork_selection_id    = Column(UUID(as_uuid=True), ForeignKey("artwork_selection_log.id"), nullable=True)
    file_save_id            = Column(UUID(as_uuid=True), ForeignKey("file_save_log.id"), nullable=True)
    manual_review_id        = Column(UUID(as_uuid=True), ForeignKey("manual_review_log.id"), nullable=True)
    save_type               = Column(String(64), ForeignKey("save_type_lookup.id"), nullable=True)

    # ── Duplicate tracking ────────────────────────────────────────────
    is_duplicate_of         = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=True)

    __table_args__ = (
        Index("ix_mpr_file_universe_id",    "file_universe_id"),
        Index("ix_mpr_machine_id",          "machine_id"),
        Index("ix_mpr_status",              "status"),
        Index("ix_mpr_is_duplicate_of",     "is_duplicate_of"),
        Index("ix_mpr_created_at",          "created_at"),
        Index(
            "ix_mpr_processing_queue",
            "created_at",
            postgresql_where=text("status IN ('pending', 'failed')")
        ),
    )


class MetaProcessorReprocessLog(Base):
    """
    Records why a file was reprocessed and links the new run to the old one.
    One row per reprocess event.
    """
    __tablename__ = "meta_processor_reprocess_log"

    id                  = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid             = Column(String(1024), nullable=False, unique=True)
    new_run_id          = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    previous_run_id     = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    reason              = Column(String(64), ForeignKey("reprocess_reason_lookup.id"), nullable=False)
    note                = Column(Text, nullable=True)
    triggered_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    machine_id          = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    created_at          = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_mprpl_new_run_id",      "new_run_id"),
        Index("ix_mprpl_previous_run_id", "previous_run_id"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 2 — PIPELINE TRACKING (cross-cutting)
# ══════════════════════════════════════════════════════════════════════════════

class RunStageLog(Base):
    """One row per stage per run. Records start and end of every pipeline stage."""
    __tablename__ = "run_stage_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    stage                   = Column(String(64), ForeignKey("pipeline_stage_lookup.id"), nullable=False)
    started_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    completed_at            = Column(TIMESTAMP(timezone=True), nullable=True)
    outcome                 = Column(String(64), ForeignKey("service_result_lookup.id"), nullable=True)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    triggered_by_user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id              = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=True)
    note                    = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_rsl_run_id", "run_id"),
        Index("ix_rsl_stage",  "stage"),
    )


class RunPhaseLog(Base):
    """One row per phase per run. Drill-down below stage level."""
    __tablename__ = "run_phase_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    stage_log_id            = Column(UUID(as_uuid=True), ForeignKey("run_stage_log.id"), nullable=False)
    phase                   = Column(String(64), ForeignKey("pipeline_phase_lookup.id"), nullable=False)
    started_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    completed_at            = Column(TIMESTAMP(timezone=True), nullable=True)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    note                    = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_rpl_run_id",       "run_id"),
        Index("ix_rpl_stage_log_id", "stage_log_id"),
        Index("ix_rpl_phase",        "phase"),
    )


class RunStepLog(Base):
    """One row per step per run. Every atomic action recorded explicitly."""
    __tablename__ = "run_step_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    phase_log_id            = Column(UUID(as_uuid=True), ForeignKey("run_phase_log.id"), nullable=False)
    step                    = Column(String(64), ForeignKey("pipeline_step_lookup.id"), nullable=False)
    started_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    completed_at            = Column(TIMESTAMP(timezone=True), nullable=True)
    result                  = Column(String(64), ForeignKey("service_result_lookup.id"), nullable=True)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    note                    = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_rstl_run_id",      "run_id"),
        Index("ix_rstl_phase_log_id","phase_log_id"),
        Index("ix_rstl_step",        "step"),
    )


class RunDecisionLog(Base):
    """
    One row per decision diamond evaluation per run.
    Records what the decision saw and which branch it took.
    This is the explicit record of every if/else in the flowchart.
    """
    __tablename__ = "run_decision_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    step_log_id             = Column(UUID(as_uuid=True), ForeignKey("run_step_log.id"), nullable=True)
    decision_type           = Column(String(64), ForeignKey("pipeline_decision_type_lookup.id"), nullable=False)
    branch_taken            = Column(String(64), ForeignKey("decision_branch_lookup.id"), nullable=False)
    evaluated_value         = Column(Text, nullable=True)       # what value was tested e.g. the actual MBID string
    reason                  = Column(Text, nullable=True)       # why this branch was taken
    evaluated_at            = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)

    __table_args__ = (
        Index("ix_rdl_run_id",       "run_id"),
        Index("ix_rdl_decision_type","decision_type"),
        Index("ix_rdl_branch_taken", "branch_taken"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 3 — INGEST STAGE
# ══════════════════════════════════════════════════════════════════════════════

class FileIngestLog(Base):
    """
    Full snapshot of everything readable from the file at ingest time.
    This is the hedge table — the complete picture of the file as we first saw it.
    Tags, technical properties, hashes, and what identifiers were present.
    """
    __tablename__ = "file_ingest_log"

    id                              = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                         = Column(String(1024), nullable=False, unique=True)
    run_id                          = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False, unique=True)
    ingested_at                     = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    machine_id                      = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)

    # ── File identity ─────────────────────────────────────────────────
    file_path                       = Column(Text, nullable=False)
    file_name                       = Column(Text, nullable=False)
    file_extension                  = Column(String(16), nullable=True)
    file_format                     = Column(String(64), ForeignKey("file_format_lookup.id"), nullable=True)
    file_size_bytes                 = Column(Integer, nullable=True)
    file_hash                       = Column(String(64), nullable=False)        # SHA-256 whole file
    audio_hash                      = Column(String(64), nullable=True)         # SHA-256 audio stream only
    last_known_hash                 = Column(String(64), nullable=True)
    hash_changed_by                 = Column(String(64), ForeignKey("hash_changed_by_lookup.id"), nullable=True)

    # ── Technical properties ──────────────────────────────────────────
    duration_ms                     = Column(Integer, nullable=True)
    sample_rate_hz                  = Column(Integer, nullable=True)
    bitrate_kbps                    = Column(Integer, nullable=True)
    channels                        = Column(SmallInteger, nullable=True)
    bits_per_sample                 = Column(SmallInteger, nullable=True)
    codec                           = Column(String(32), nullable=True)
    encoder                         = Column(Text, nullable=True)
    is_vbr                          = Column(Boolean, nullable=True)

    # ── Tags found in the file ────────────────────────────────────────
    source_track_mbid               = Column(String(36), nullable=True)
    source_album_mbid               = Column(String(36), nullable=True)
    source_artist                   = Column(Text, nullable=True)
    source_title                    = Column(Text, nullable=True)
    source_album                    = Column(Text, nullable=True)
    source_year                     = Column(SmallInteger, nullable=True)
    source_track_number             = Column(SmallInteger, nullable=True)
    source_genre                    = Column(ARRAY(Text), nullable=True)
    source_isrc                     = Column(String(12), nullable=True)
    source_label                    = Column(Text, nullable=True)
    source_composer                 = Column(Text, nullable=True)
    source_comment                  = Column(Text, nullable=True)
    source_lyrics                   = Column(Text, nullable=True)
    source_bpm                      = Column(Numeric(6, 2), nullable=True)
    source_key                      = Column(String(8), nullable=True)
    source_language                 = Column(String(8), nullable=True)
    all_raw_tags                    = Column(JSONB, nullable=True)               # full tag dump, nothing lost

    # ── Identifier presence flags ─────────────────────────────────────
    has_track_mbid                  = Column(Boolean, nullable=False, server_default=text("false"))
    has_album_mbid                  = Column(Boolean, nullable=False, server_default=text("false"))
    has_artist_and_title            = Column(Boolean, nullable=False, server_default=text("false"))
    has_isrc                        = Column(Boolean, nullable=False, server_default=text("false"))
    has_any_identifier              = Column(Boolean, nullable=False, server_default=text("false"))
    has_embedded_artwork            = Column(Boolean, nullable=False, server_default=text("false"))
    track_mbid_format_valid         = Column(Boolean, nullable=True)             # format check only, not API
    album_mbid_format_valid         = Column(Boolean, nullable=True)
    isrc_format_valid               = Column(Boolean, nullable=True)

    __table_args__ = (
        Index("ix_fil_run_id",      "run_id"),
        Index("ix_fil_file_hash",   "file_hash"),
        Index("ix_fil_audio_hash",  "audio_hash"),
        Index("ix_fil_source_track_mbid", "source_track_mbid"),
    )


class FileQualityCheckLog(Base):
    """
    Quality flags detected at ingest. One row per flag per run.
    Blocking flags will halt the pipeline before any processing.
    """
    __tablename__ = "file_quality_check_log"

    id              = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid         = Column(String(1024), nullable=False, unique=True)
    run_id          = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    ingest_id       = Column(UUID(as_uuid=True), ForeignKey("file_ingest_log.id"), nullable=False)
    flag            = Column(String(64), ForeignKey("file_quality_flag_lookup.id"), nullable=False)
    is_blocking     = Column(Boolean, nullable=False, server_default=text("false"))
    detail          = Column(Text, nullable=True)           # e.g. "duration: 3200ms, threshold: 10000ms"
    checked_at      = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    machine_id      = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)

    __table_args__ = (
        Index("ix_fqcl_run_id",   "run_id"),
        Index("ix_fqcl_flag",     "flag"),
        Index("ix_fqcl_is_blocking", "is_blocking"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 4 — MBID VALIDATION LOG (cross-cutting)
# ══════════════════════════════════════════════════════════════════════════════

class MBIDValidationLog(Base):
    """
    Every MBID validation attempt ever, across the entire module lifecycle.
    MBIDs can be validated at multiple points — after reading tags, after AcoustID,
    after merge, after manual entry. Every attempt gets a row here.
    """
    __tablename__ = "mbid_validation_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    mbid                    = Column(String(36), nullable=False)
    mbid_type               = Column(String(16), nullable=False)                # track or album
    mbid_source             = Column(String(64), ForeignKey("mbid_source_lookup.id"), nullable=False)
    result                  = Column(String(64), ForeignKey("mbid_validation_result_lookup.id"), nullable=False)
    triggered_at_stage      = Column(String(64), ForeignKey("pipeline_stage_lookup.id"), nullable=False)
    triggered_at_step       = Column(String(64), ForeignKey("pipeline_step_lookup.id"), nullable=False)
    validated_at            = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    raw_response            = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("ix_mvl_run_id", "run_id"),
        Index("ix_mvl_mbid",   "mbid"),
        Index("ix_mvl_result", "result"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 5 — METADATA FETCH STAGE
# ══════════════════════════════════════════════════════════════════════════════

class MetadataFetchLog(Base):
    """
    One row per service per run. The envelope for every external service call.
    Records call order (for the linear chain), timing, result and raw JSON.
    call_order supports both linear and future parallel approaches.
    """
    __tablename__ = "metadata_fetch_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    service                 = Column(String(64), ForeignKey("service_lookup.id"), nullable=False)
    call_order              = Column(SmallInteger, nullable=False)               # position in the chain
    result                  = Column(String(64), ForeignKey("service_result_lookup.id"), nullable=False)
    skipped_reason          = Column(Text, nullable=True)                        # why skipped if result=skipped
    called_at               = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    completed_at            = Column(TIMESTAMP(timezone=True), nullable=True)
    duration_ms             = Column(Integer, nullable=True)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    raw_response            = Column(JSONB, nullable=True)
    http_status_code        = Column(SmallInteger, nullable=True)
    consent_id              = Column(UUID(as_uuid=True), ForeignKey("user_consent_log.id"), nullable=True)

    __table_args__ = (
        UniqueConstraint("run_id", "service", name="uq_mfl_run_service"),
        Index("ix_mfl_run_id",  "run_id"),
        Index("ix_mfl_service", "service"),
        Index("ix_mfl_result",  "result"),
    )


class MetadataFetchFields(Base):
    """
    Relational translation of the raw JSON from each service call.
    One row per field per service per run.
    FK to metadata_field_lookup keeps the vocabulary controlled.
    This is what makes the JSON queryable.
    """
    __tablename__ = "metadata_fetch_fields"

    id                  = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid             = Column(String(1024), nullable=False, unique=True)
    run_id              = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    fetch_log_id        = Column(UUID(as_uuid=True), ForeignKey("metadata_fetch_log.id"), nullable=False)
    service             = Column(String(64), ForeignKey("service_lookup.id"), nullable=False)
    field               = Column(String(64), ForeignKey("metadata_field_lookup.id"), nullable=False)
    value_text          = Column(Text, nullable=True)                   # for text fields
    value_integer       = Column(Integer, nullable=True)                # for integer fields
    value_numeric       = Column(Numeric(10, 4), nullable=True)         # for decimal fields
    value_array         = Column(ARRAY(Text), nullable=True)            # for array fields (genre etc)
    confidence          = Column(Numeric(5, 4), nullable=True)          # service's own confidence if provided
    fetched_at          = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("fetch_log_id", "field", name="uq_mff_fetch_field"),
        Index("ix_mff_run_id",       "run_id"),
        Index("ix_mff_fetch_log_id", "fetch_log_id"),
        Index("ix_mff_field",        "field"),
        Index("ix_mff_service",      "service"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 6 — RESOLVE STAGE
# ══════════════════════════════════════════════════════════════════════════════

class ResolvedMetadata(Base):
    """
    Flat winner row for core metadata fields. Fast queries live here.
    One row per run. Core fields only — artist, title, album, year, mbid, isrc.
    Extended fields are in resolved_metadata_extended.
    Nothing here is final until the user has approved it.
    """
    __tablename__ = "resolved_metadata"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False, unique=True)
    created_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    user_approved           = Column(Boolean, nullable=False, server_default=text("false"))
    approved_by_user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at             = Column(TIMESTAMP(timezone=True), nullable=True)

    # ── Core winner fields ────────────────────────────────────────────
    resolved_mbid           = Column(String(36), nullable=True)
    resolved_artist         = Column(Text, nullable=True)
    resolved_title          = Column(Text, nullable=True)
    resolved_album          = Column(Text, nullable=True)
    resolved_year           = Column(SmallInteger, nullable=True)
    resolved_track_number   = Column(SmallInteger, nullable=True)
    resolved_isrc           = Column(String(12), nullable=True)

    # ── Confidence ────────────────────────────────────────────────────
    confidence_score        = Column(Numeric(5, 4), nullable=True)
    services_agreed_count   = Column(SmallInteger, nullable=True)
    confidence_override     = Column(Numeric(5, 4), nullable=True)
    confidence_note         = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_rm_run_id",           "run_id"),
        Index("ix_rm_resolved_mbid",    "resolved_mbid"),
        Index("ix_rm_resolved_isrc",    "resolved_isrc"),
        Index("ix_rm_confidence_score", "confidence_score"),
    )


class ResolvedMetadataExtended(Base):
    """
    Normalised winner rows for extended metadata fields.
    One row per field per run. FK to metadata_field_lookup.
    Covers everything beyond the core fields — bpm, key, mood, language,
    label, country, genre, composer, lyricist, publisher, etc.
    Infinitely extensible without schema changes.
    """
    __tablename__ = "resolved_metadata_extended"

    id                  = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid             = Column(String(1024), nullable=False, unique=True)
    run_id              = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    resolved_id         = Column(UUID(as_uuid=True), ForeignKey("resolved_metadata.id"), nullable=False)
    field               = Column(String(64), ForeignKey("metadata_field_lookup.id"), nullable=False)
    value_text          = Column(Text, nullable=True)
    value_integer       = Column(Integer, nullable=True)
    value_numeric       = Column(Numeric(10, 4), nullable=True)
    value_array         = Column(ARRAY(Text), nullable=True)
    user_approved       = Column(Boolean, nullable=False, server_default=text("false"))
    approved_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at         = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("run_id", "field", name="uq_rme_run_field"),
        Index("ix_rme_run_id",     "run_id"),
        Index("ix_rme_resolved_id","resolved_id"),
        Index("ix_rme_field",      "field"),
    )


class ResolvedMetadataSources(Base):
    """
    One row per field per run. Records which service won each field,
    what value it provided, confidence, and any user override.
    Covers both core and extended fields — every field winner is recorded here.
    """
    __tablename__ = "resolved_metadata_sources"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    field                   = Column(String(64), ForeignKey("metadata_field_lookup.id"), nullable=False)
    winning_service         = Column(String(64), ForeignKey("service_lookup.id"), nullable=True)
    winning_value_text      = Column(Text, nullable=True)
    winning_value_integer   = Column(Integer, nullable=True)
    winning_value_numeric   = Column(Numeric(10, 4), nullable=True)
    winning_value_array     = Column(ARRAY(Text), nullable=True)
    confidence              = Column(Numeric(5, 4), nullable=True)
    user_overridden         = Column(Boolean, nullable=False, server_default=text("false"))
    override_value_text     = Column(Text, nullable=True)
    override_reason         = Column(Text, nullable=True)
    overridden_by_user_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    overridden_at           = Column(TIMESTAMP(timezone=True), nullable=True)
    decided_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("run_id", "field", name="uq_rms_run_field"),
        Index("ix_rms_run_id",         "run_id"),
        Index("ix_rms_field",          "field"),
        Index("ix_rms_winning_service","winning_service"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 7 — ARTWORK STAGE
# ══════════════════════════════════════════════════════════════════════════════

class ArtworkFetchLog(Base):
    """
    One row per service per run for artwork. Records every artwork candidate found.
    User can also upload artwork from local disk (source=manual).
    """
    __tablename__ = "artwork_fetch_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    service                 = Column(String(64), ForeignKey("artwork_source_lookup.id"), nullable=False)
    call_order              = Column(SmallInteger, nullable=False)
    result                  = Column(String(64), ForeignKey("service_result_lookup.id"), nullable=False)
    skipped_reason          = Column(Text, nullable=True)
    artwork_url             = Column(Text, nullable=True)
    artwork_local_path      = Column(Text, nullable=True)
    width_px                = Column(Integer, nullable=True)
    height_px               = Column(Integer, nullable=True)
    file_size_bytes         = Column(Integer, nullable=True)
    format                  = Column(String(64), ForeignKey("artwork_format_lookup.id"), nullable=True)
    raw_response            = Column(JSONB, nullable=True)
    fetched_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    consent_id              = Column(UUID(as_uuid=True), ForeignKey("user_consent_log.id"), nullable=True)

    __table_args__ = (
        UniqueConstraint("run_id", "service", name="uq_afl_run_service"),
        Index("ix_afl_run_id",  "run_id"),
        Index("ix_afl_service", "service"),
        Index("ix_afl_result",  "result"),
    )


class ArtworkSelectionLog(Base):
    """
    User picks the winning artwork from all candidates.
    One row per run — only one winner, but the selection history is recorded.
    """
    __tablename__ = "artwork_selection_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False, unique=True)
    selected_fetch_id       = Column(UUID(as_uuid=True), ForeignKey("artwork_fetch_log.id"), nullable=True)
    selected_by_user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    selected_at             = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    note                    = Column(Text, nullable=True)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    session_id              = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=True)

    __table_args__ = (
        Index("ix_asl_run_id", "run_id"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 8 — SAVE STAGE
# ══════════════════════════════════════════════════════════════════════════════

class FileSaveLog(Base):
    """
    The definitive record of what was actually written to the file.
    Every field that was written, every field that was skipped.
    Nothing hits disk without a row here. User explicitly initiates every save.
    """
    __tablename__ = "file_save_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    save_type               = Column(String(64), ForeignKey("save_type_lookup.id"), nullable=False)
    initiated_by_user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    session_id              = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=True)
    consent_id              = Column(UUID(as_uuid=True), ForeignKey("user_consent_log.id"), nullable=True)
    initiated_at            = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    completed_at            = Column(TIMESTAMP(timezone=True), nullable=True)
    success                 = Column(Boolean, nullable=True)
    file_hash_after_save    = Column(String(64), nullable=True)     # SHA-256 after write, to confirm
    note                    = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_fsl_run_id",              "run_id"),
        Index("ix_fsl_initiated_by_user_id","initiated_by_user_id"),
        Index("ix_fsl_save_type",           "save_type"),
    )


class FileSaveFieldLog(Base):
    """
    One row per field per save. Every field decision recorded explicitly.
    Was it written? Skipped? Did the user exclude it? Did it fail?
    """
    __tablename__ = "file_save_field_log"

    id                  = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid             = Column(String(1024), nullable=False, unique=True)
    save_log_id         = Column(UUID(as_uuid=True), ForeignKey("file_save_log.id"), nullable=False)
    run_id              = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    field               = Column(String(64), ForeignKey("metadata_field_lookup.id"), nullable=False)
    status              = Column(String(64), ForeignKey("save_field_status_lookup.id"), nullable=False)
    value_written       = Column(Text, nullable=True)       # the actual value written
    previous_value      = Column(Text, nullable=True)       # what was in the tag before
    note                = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("save_log_id", "field", name="uq_fsfl_save_field"),
        Index("ix_fsfl_save_log_id", "save_log_id"),
        Index("ix_fsfl_run_id",      "run_id"),
        Index("ix_fsfl_field",       "field"),
        Index("ix_fsfl_status",      "status"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 9 — PICARD
# ══════════════════════════════════════════════════════════════════════════════

class PicardSessionLog(Base):
    """
    Picard is a local desktop application — the user is physically in the loop.
    Records what we sent, what Picard matched, what the user changed, what came back.
    """
    __tablename__ = "picard_session_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    user_id                 = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    session_id              = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=True)
    consent_id              = Column(UUID(as_uuid=True), ForeignKey("user_consent_log.id"), nullable=True)

    # ── What went in ──────────────────────────────────────────────────
    data_sent_to_picard     = Column(JSONB, nullable=True)
    sent_at                 = Column(TIMESTAMP(timezone=True), nullable=True)

    # ── What Picard did ───────────────────────────────────────────────
    picard_matched_mbid     = Column(String(36), nullable=True)
    picard_match_score      = Column(Numeric(5, 4), nullable=True)
    picard_raw_result       = Column(JSONB, nullable=True)

    # ── What the user did inside Picard ───────────────────────────────
    user_action             = Column(String(64), ForeignKey("picard_action_lookup.id"), nullable=True)
    user_changes            = Column(JSONB, nullable=True)      # field-level changes user made in Picard
    user_action_at          = Column(TIMESTAMP(timezone=True), nullable=True)

    # ── What came back ────────────────────────────────────────────────
    final_data_returned     = Column(JSONB, nullable=True)
    was_finalised           = Column(Boolean, nullable=False, server_default=text("false"))
    finalised_at            = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_psl_run_id",  "run_id"),
        Index("ix_psl_user_id", "user_id"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 10 — CONSENT
# ══════════════════════════════════════════════════════════════════════════════

class UserConsentLog(Base):
    """
    Every consent event in the module. Consent is broader than just service calls —
    it covers AcoustID runs, Picard sends, service calls, and file writes.
    No action is taken without a consent record.
    """
    __tablename__ = "user_consent_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    consent_type            = Column(String(64), ForeignKey("consent_type_lookup.id"), nullable=False)
    service                 = Column(String(64), ForeignKey("service_lookup.id"), nullable=True)    # if service_call type
    decision                = Column(String(64), ForeignKey("consent_decision_lookup.id"), nullable=False)
    decided_by_user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    decided_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    revoked_at              = Column(TIMESTAMP(timezone=True), nullable=True)
    revoked_by_user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    note                    = Column(Text, nullable=True)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)

    __table_args__ = (
        Index("ix_ucl_run_id",       "run_id"),
        Index("ix_ucl_consent_type", "consent_type"),
        Index("ix_ucl_service",      "service"),
        Index("ix_ucl_decision",     "decision"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 11 — MANUAL REVIEW
# ══════════════════════════════════════════════════════════════════════════════

class ManualReviewLog(Base):
    """
    One row per review event per file. A file can be reviewed multiple times.
    Stores all reasons that triggered the review as an array of lookup FKs.
    """
    __tablename__ = "manual_review_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    reasons                 = Column(ARRAY(Text), nullable=False)               # array of manual_review_reason_lookup ids
    triggered_at_stage      = Column(String(64), ForeignKey("pipeline_stage_lookup.id"), nullable=False)
    triggered_at_step       = Column(String(64), ForeignKey("pipeline_step_lookup.id"), nullable=False)
    triggered_at            = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    triggered_by_user_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_to_user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_at             = Column(TIMESTAMP(timezone=True), nullable=True)
    resolution              = Column(String(64), ForeignKey("manual_review_resolution_lookup.id"), nullable=True)
    resolved_by_user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at             = Column(TIMESTAMP(timezone=True), nullable=True)
    resolution_note         = Column(Text, nullable=True)
    has_sufficient_artwork  = Column(Boolean, nullable=True)

    __table_args__ = (
        Index("ix_mrl_run_id",               "run_id"),
        Index("ix_mrl_assigned_to_user_id",  "assigned_to_user_id"),
        Index("ix_mrl_resolution",           "resolution"),
        Index(
            "ix_mrl_unresolved",
            "triggered_at",
            postgresql_where=text("resolution IS NULL")
        ),
    )


class ManualReviewFieldLog(Base):
    """
    Field-level decisions made during a manual review.
    Full history of what the user changed, field by field.
    """
    __tablename__ = "manual_review_field_log"

    id                      = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid                 = Column(String(1024), nullable=False, unique=True)
    review_id               = Column(UUID(as_uuid=True), ForeignKey("manual_review_log.id"), nullable=False)
    run_id                  = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    field                   = Column(String(64), ForeignKey("metadata_field_lookup.id"), nullable=False)
    old_value               = Column(Text, nullable=True)
    new_value               = Column(Text, nullable=True)
    value_source            = Column(String(64), ForeignKey("service_lookup.id"), nullable=True)
    confidence_override     = Column(Numeric(5, 4), nullable=True)
    confidence_note         = Column(Text, nullable=True)
    decided_by_user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    machine_id              = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    session_id              = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=True)
    decided_at              = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    note                    = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_mrfl_review_id", "review_id"),
        Index("ix_mrfl_run_id",    "run_id"),
        Index("ix_mrfl_field",     "field"),
    )


# ══════════════════════════════════════════════════════════════════════════════
# GROUP 12 — ERROR LOG (cross-cutting)
# ══════════════════════════════════════════════════════════════════════════════

class RunErrorLog(Base):
    """
    Every error that ever happened, ever. Nothing is overwritten.
    Full HTTP context for network errors. Full system context for system errors.
    """
    __tablename__ = "run_error_log"

    id                  = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid             = Column(String(1024), nullable=False, unique=True)
    run_id              = Column(UUID(as_uuid=True), ForeignKey("meta_processor_runs.id"), nullable=False)
    machine_id          = Column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=False)
    session_id          = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=True)
    occurred_at         = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    stage               = Column(String(64), ForeignKey("pipeline_stage_lookup.id"), nullable=False)
    step                = Column(String(64), ForeignKey("pipeline_step_lookup.id"), nullable=False)
    retry_number        = Column(SmallInteger, nullable=False, server_default=text("0"))
    error_category      = Column(String(64), ForeignKey("error_category_lookup.id"), nullable=False)
    error_type          = Column(String(64), ForeignKey("error_type_lookup.id"), nullable=False)
    error_message       = Column(Text, nullable=False)
    error_traceback     = Column(Text, nullable=True)
    service             = Column(String(64), ForeignKey("service_lookup.id"), nullable=True)

    # ── HTTP details ──────────────────────────────────────────────────
    http_status_code    = Column(SmallInteger, nullable=True)
    retry_after_seconds = Column(Integer, nullable=True)
    request_url         = Column(Text, nullable=True)
    request_method      = Column(String(8), nullable=True)
    request_headers     = Column(JSONB, nullable=True)
    request_body        = Column(JSONB, nullable=True)
    response_headers    = Column(JSONB, nullable=True)
    response_body       = Column(Text, nullable=True)

    # ── System context ────────────────────────────────────────────────
    python_version      = Column(String(16), nullable=True)
    os_info             = Column(Text, nullable=True)
    available_memory_mb = Column(Integer, nullable=True)
    available_disk_mb   = Column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_rel_run_id",         "run_id"),
        Index("ix_rel_machine_id",     "machine_id"),
        Index("ix_rel_error_type",     "error_type"),
        Index("ix_rel_error_category", "error_category"),
        Index("ix_rel_service",        "service"),
        Index("ix_rel_occurred_at",    "occurred_at"),
    )