from sqlalchemy import (
    Column, String, Text, Integer, SmallInteger, Boolean, Numeric,
    TIMESTAMP, Index, UniqueConstraint, ForeignKey, ARRAY
)
from sqlalchemy.sql import text
from schema.base import Base
from sqlalchemy.dialects.postgresql import UUID

# ══════════════════════════════════════════════════════════════════════════════
# LOOKUP TABLES
# ══════════════════════════════════════════════════════════════════════════════

class ProcessorStatusLookup(Base):
    __tablename__ = "processor_status_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class RunTriggerLookup(Base):
    __tablename__ = "run_trigger_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class ReprocessReasonLookup(Base):
    __tablename__ = "reprocess_reason_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class PipelineStageLookup(Base):
    __tablename__ = "pipeline_stage_lookup"
    id           = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid      = Column(String(1024), nullable=False)
    label        = Column(String(128), nullable=False)
    display_order = Column(SmallInteger, nullable=False)
    description  = Column(Text, nullable=True)


class PipelinePhaseLookup(Base):
    __tablename__ = "pipeline_phase_lookup"
    id           = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid      = Column(String(1024), nullable=False)
    stage_id     = Column(String(64), ForeignKey("pipeline_stage_lookup.id"), nullable=False)
    label        = Column(String(128), nullable=False)
    display_order = Column(SmallInteger, nullable=False)
    description  = Column(Text, nullable=True)


class PipelineStepLookup(Base):
    __tablename__ = "pipeline_step_lookup"
    id           = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid      = Column(String(1024), nullable=False)
    phase_id     = Column(String(64), ForeignKey("pipeline_phase_lookup.id"), nullable=False)
    stage_id     = Column(String(64), ForeignKey("pipeline_stage_lookup.id"), nullable=False)
    label        = Column(String(128), nullable=False)
    display_order = Column(SmallInteger, nullable=False)
    description  = Column(Text, nullable=True)


class PipelineDecisionTypeLookup(Base):
    __tablename__ = "pipeline_decision_type_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    stage_id    = Column(String(64), ForeignKey("pipeline_stage_lookup.id"), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class DecisionBranchLookup(Base):
    __tablename__ = "decision_branch_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class ServiceLookup(Base):
    __tablename__ = "service_lookup"
    id              = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid         = Column(String(1024), nullable=False)
    label           = Column(String(128), nullable=False)
    is_local        = Column(Boolean, nullable=False, server_default=text("false"))  # true for Picard
    requires_consent = Column(Boolean, nullable=False, server_default=text("true"))
    description     = Column(Text, nullable=True)


class ServiceResultLookup(Base):
    __tablename__ = "service_result_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class MetadataFieldLookup(Base):
    __tablename__ = "metadata_field_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    is_core     = Column(Boolean, nullable=False, server_default=text("false"))  # true = flat column in resolved_metadata
    data_type   = Column(String(32), nullable=False)    # text, integer, numeric, array, boolean
    description = Column(Text, nullable=True)


class MBIDSourceLookup(Base):
    __tablename__ = "mbid_source_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class MBIDValidationResultLookup(Base):
    __tablename__ = "mbid_validation_result_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class AcoustIDResultLookup(Base):
    __tablename__ = "acoustid_result_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class FileFormatLookup(Base):
    __tablename__ = "file_format_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    mime_type   = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)


class FileQualityFlagLookup(Base):
    __tablename__ = "file_quality_flag_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    is_blocking = Column(Boolean, nullable=False, server_default=text("false"))  # blocks pipeline if true
    description = Column(Text, nullable=True)


class HashChangedByLookup(Base):
    __tablename__ = "hash_changed_by_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class ArtworkSourceLookup(Base):
    __tablename__ = "artwork_source_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    is_local    = Column(Boolean, nullable=False, server_default=text("false"))
    description = Column(Text, nullable=True)


class ArtworkFormatLookup(Base):
    __tablename__ = "artwork_format_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    mime_type   = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)


class SaveTypeLookup(Base):
    __tablename__ = "save_type_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class SaveFieldStatusLookup(Base):
    __tablename__ = "save_field_status_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class PicardActionLookup(Base):
    __tablename__ = "picard_action_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class ConsentTypeLookup(Base):
    __tablename__ = "consent_type_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class ConsentDecisionLookup(Base):
    __tablename__ = "consent_decision_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class ManualReviewReasonLookup(Base):
    __tablename__ = "manual_review_reason_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    category    = Column(String(64), nullable=True)     # dead_end, data_quality, artwork, file_issue etc
    description = Column(Text, nullable=True)


class ManualReviewResolutionLookup(Base):
    __tablename__ = "manual_review_resolution_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class ErrorCategoryLookup(Base):
    __tablename__ = "error_category_lookup"
    id          = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid     = Column(String(1024), nullable=False)
    label       = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)


class ErrorTypeLookup(Base):
    __tablename__ = "error_type_lookup"
    id              = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuidv7()"))
    mca_pid         = Column(String(1024), nullable=False)
    category_id     = Column(String(64), ForeignKey("error_category_lookup.id"), nullable=False)
    label           = Column(String(128), nullable=False)
    http_status_code = Column(SmallInteger, nullable=True)  # for HTTP errors
    description     = Column(Text, nullable=True)


class ReprocessReasonLookup2(Base):
    # already defined above — placeholder comment only
    pass
