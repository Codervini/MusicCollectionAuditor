import enum

# ══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ══════════════════════════════════════════════════════════════════════════════

# # ── High level pipeline stage (category) ─────────────────────────────────────
# class PipelineStage(enum.Enum):
#     read_file            = "read_file"
#     mbid_validation      = "mbid_validation"
#     acoustid             = "acoustid"
#     service_search       = "service_search"
#     merge_enrich         = "merge_enrich"
#     picard               = "picard"
#     artwork_search       = "artwork_search"
#     manual_review        = "manual_review"
#     finalize             = "finalize"

# # ── Fine grained pipeline step (every node in the flowchart) ─────────────────
# class PipelineStep(enum.Enum):
#     # read_file stage
#     read_file_tags              = "read_file_tags"
#     check_has_mbid              = "check_has_mbid"
#     check_has_artist_title      = "check_has_artist_title"

#     # mbid_validation stage
#     validate_source_mbid        = "validate_source_mbid"
#     validate_acoustid_mbid      = "validate_acoustid_mbid"
#     validate_service_mbid       = "validate_service_mbid"
#     validate_merge_mbid         = "validate_merge_mbid"

#     # acoustid stage
#     acoustid_fingerprint        = "acoustid_fingerprint"
#     acoustid_lookup             = "acoustid_lookup"

#     # service_search stage
#     musicbrainz_text_search     = "musicbrainz_text_search"
#     itunes_search               = "itunes_search"
#     lastfm_search               = "lastfm_search"
#     spotify_search              = "spotify_search"
#     discogs_search              = "discogs_search"
#     audiodb_search              = "audiodb_search"
#     deezer_search               = "deezer_search"
#     youtube_search              = "youtube_search"

#     # merge_enrich stage
#     merge_service_results       = "merge_service_results"
#     enrich_metadata             = "enrich_metadata"
#     check_merge_has_mbid        = "check_merge_has_mbid"

#     # picard stage
#     send_to_picard              = "send_to_picard"
#     awaiting_picard_user_action = "awaiting_picard_user_action"
#     picard_finalised            = "picard_finalised"

#     # artwork_search stage
#     check_has_artwork           = "check_has_artwork"
#     art_caa_search              = "art_caa_search"
#     art_itunes_search           = "art_itunes_search"
#     art_spotify_search          = "art_spotify_search"
#     art_audiodb_search          = "art_audiodb_search"
#     art_discogs_search          = "art_discogs_search"
#     art_deezer_search           = "art_deezer_search"
#     art_lastfm_search           = "art_lastfm_search"

#     # manual_review stage
#     manual_review_triggered     = "manual_review_triggered"
#     awaiting_user_decision      = "awaiting_user_decision"
#     user_decision_made          = "user_decision_made"
#     check_artwork_sufficient    = "check_artwork_sufficient"

#     # finalize stage
#     full_save                   = "full_save"
#     incomplete_save             = "incomplete_save"

# # ── Where did the MBID input come from ───────────────────────────────────────
# class MBIDSource(enum.Enum):
#     file_tags    = "file_tags"
#     acoustid     = "acoustid"
#     musicbrainz  = "musicbrainz"
#     itunes       = "itunes"
#     lastfm       = "lastfm"
#     spotify      = "spotify"
#     discogs      = "discogs"
#     audiodb      = "audiodb"
#     deezer       = "deezer"
#     youtube      = "youtube"
#     merge        = "merge"
#     manual       = "manual"

# # ── Result of an MBID validation attempt ─────────────────────────────────────
# class MBIDValidationResult(enum.Enum):
#     valid         = "valid"
#     invalid       = "invalid"
#     not_found     = "not_found"
#     ambiguous     = "ambiguous"
#     api_error     = "api_error"

# # ── Services available in this module ────────────────────────────────────────
# class Service(enum.Enum):
#     musicbrainz  = "musicbrainz"
#     acoustid     = "acoustid"
#     itunes       = "itunes"
#     lastfm       = "lastfm"
#     spotify      = "spotify"
#     discogs      = "discogs"
#     audiodb      = "audiodb"
#     deezer       = "deezer"
#     youtube      = "youtube"
#     caa          = "caa"          # Cover Art Archive
#     picard       = "picard"       # local, not an API

# # ── Result of a service metadata search ──────────────────────────────────────
# class ServiceResult(enum.Enum):
#     fully_found     = "fully_found"
#     partially_found = "partially_found"
#     not_found       = "not_found"
#     error           = "error"
#     skipped         = "skipped"   # user did not consent

# ── Result of an AcoustID lookup ─────────────────────────────────────────────
class AcoustidResult(enum.Enum):
    found       = "found"
    not_found   = "not_found"
    ambiguous   = "ambiguous"
    error       = "error"

# # ── Who changed the file hash ─────────────────────────────────────────────────
# class HashChangedBy(enum.Enum):
#     software = "software"
#     external = "external"

# ── How the file was saved at the end ────────────────────────────────────────
class SaveType(enum.Enum):
    full       = "full"
    incomplete = "incomplete"

# ── User roles ────────────────────────────────────────────────────────────────
class UserRole(enum.Enum):
    owner    = "owner"
    trusted  = "trusted"
    readonly = "readonly"

# # ── Service consent decision per file ────────────────────────────────────────
# class ConsentDecision(enum.Enum):
#     approved = "approved"
#     rejected = "rejected"
#     revoked  = "revoked"

# # ── Manual review trigger reasons ────────────────────────────────────────────
# class ManualReviewReason(enum.Enum):
#     # Pipeline dead ends
#     acoustid_not_found              = "acoustid_not_found"
#     all_services_not_found          = "all_services_not_found"
#     merge_enrich_no_mbid_found      = "merge_enrich_no_mbid_found"
#     insufficient_data_for_artwork   = "insufficient_data_for_artwork"

#     # AcoustID issues
#     acoustid_low_score              = "acoustid_low_score"
#     acoustid_ambiguous              = "acoustid_ambiguous"

#     # MBID issues
#     mbid_invalid                    = "mbid_invalid"
#     mbid_mismatch_across_services   = "mbid_mismatch_across_services"
#     mbid_ambiguous                  = "mbid_ambiguous"

#     # Data quality
#     conflicting_service_data        = "conflicting_service_data"
#     missing_required_fields         = "missing_required_fields"
#     suspicious_metadata             = "suspicious_metadata"
#     artist_name_inconsistent        = "artist_name_inconsistent"
#     title_inconsistent              = "title_inconsistent"
#     album_inconsistent              = "album_inconsistent"
#     year_inconsistent               = "year_inconsistent"
#     genre_missing                   = "genre_missing"
#     isrc_invalid                    = "isrc_invalid"
#     isrc_mismatch                   = "isrc_mismatch"

#     # Duplicate
#     duplicate_candidate             = "duplicate_candidate"
#     duplicate_confirmed             = "duplicate_confirmed"

#     # Artwork
#     no_artwork_found                = "no_artwork_found"
#     artwork_low_resolution          = "artwork_low_resolution"
#     artwork_format_unsupported      = "artwork_format_unsupported"
#     multiple_artwork_candidates     = "multiple_artwork_candidates"

#     # File issues
#     file_moved                      = "file_moved"
#     file_corrupted                  = "file_corrupted"
#     file_format_unsupported         = "file_format_unsupported"
#     file_too_short                  = "file_too_short"
#     hash_changed_externally         = "hash_changed_externally"

#     # Service issues
#     service_rate_limited            = "service_rate_limited"
#     service_returned_empty          = "service_returned_empty"
#     service_timeout                 = "service_timeout"
#     service_conflicting_data        = "service_conflicting_data"
#     service_not_consented           = "service_not_consented"

#     # Confidence issues
#     confidence_below_threshold      = "confidence_below_threshold"
#     confidence_tie_between_services = "confidence_tie_between_services"
#     all_services_disagree           = "all_services_disagree"

#     # History
#     previously_failed_multiple_times         = "previously_failed_multiple_times"
#     manually_reviewed_before_and_changed     = "manually_reviewed_before_and_changed"

#     # User triggered
#     user_flagged                    = "user_flagged"
#     user_wants_custom_value         = "user_wants_custom_value"
#     user_disputes_resolved_data     = "user_disputes_resolved_data"
#     user_wants_different_artwork    = "user_wants_different_artwork"
#     user_wants_reprocess            = "user_wants_reprocess"

# ── Manual review resolution ──────────────────────────────────────────────────
class ManualReviewResolution(enum.Enum):
    resolved_by_user     = "resolved_by_user"
    skipped_by_user      = "skipped_by_user"
    escalated            = "escalated"
    marked_as_duplicate  = "marked_as_duplicate"
    marked_as_incomplete = "marked_as_incomplete"
    reprocessed          = "reprocessed"

# # ── Error categories ──────────────────────────────────────────────────────────
# class ErrorCategory(enum.Enum):
#     network  = "network"
#     data     = "data"
#     file     = "file"
#     system   = "system"
#     acoustid = "acoustid"
#     auth     = "auth"

# # ── Exact error types ─────────────────────────────────────────────────────────
# class ErrorType(enum.Enum):
#     # Network
#     connection_timeout      = "connection_timeout"
#     connection_refused      = "connection_refused"
#     dns_failure             = "dns_failure"
#     ssl_error               = "ssl_error"
#     proxy_error             = "proxy_error"
#     http_400_bad_request    = "http_400_bad_request"
#     http_401_unauthorized   = "http_401_unauthorized"
#     http_403_forbidden      = "http_403_forbidden"
#     http_404_not_found      = "http_404_not_found"
#     http_408_request_timeout = "http_408_request_timeout"
#     http_429_rate_limited   = "http_429_rate_limited"
#     http_500_server_error   = "http_500_server_error"
#     http_502_bad_gateway    = "http_502_bad_gateway"
#     http_503_unavailable    = "http_503_unavailable"
#     http_504_gateway_timeout = "http_504_gateway_timeout"

#     # Data
#     response_parse_error    = "response_parse_error"
#     unexpected_schema       = "unexpected_schema"
#     empty_response          = "empty_response"
#     invalid_mbid            = "invalid_mbid"
#     invalid_isrc            = "invalid_isrc"
#     encoding_error          = "encoding_error"
#     schema_version_mismatch = "schema_version_mismatch"
#     missing_required_field  = "missing_required_field"

#     # File
#     file_not_found          = "file_not_found"
#     file_unreadable         = "file_unreadable"
#     file_corrupt            = "file_corrupt"
#     unsupported_format      = "unsupported_format"
#     permission_denied       = "permission_denied"
#     file_too_large          = "file_too_large"
#     file_too_short          = "file_too_short"

#     # System
#     db_connection_error     = "db_connection_error"
#     db_write_error          = "db_write_error"
#     db_read_error           = "db_read_error"
#     out_of_memory           = "out_of_memory"
#     disk_full               = "disk_full"
#     process_killed          = "process_killed"
#     unknown                 = "unknown"

#     # AcoustID specific
#     acoustid_no_match       = "acoustid_no_match"
#     acoustid_low_score      = "acoustid_low_score"
#     acoustid_ambiguous      = "acoustid_ambiguous"
#     acoustid_api_error      = "acoustid_api_error"
#     acoustid_fingerprint_failed = "acoustid_fingerprint_failed"

#     # Auth
#     api_key_invalid         = "api_key_invalid"
#     api_key_expired         = "api_key_expired"
#     api_quota_exceeded      = "api_quota_exceeded"
#     token_refresh_failed    = "token_refresh_failed"

# # ── Audit actions ─────────────────────────────────────────────────────────────
# class AuditAction(enum.Enum):
#     insert = "insert"
#     update = "update"
#     delete = "delete"

# # ── Artwork image format ───────────────────────────────────────────────────────
# class ArtworkFormat(enum.Enum):
#     jpeg = "jpeg"
#     png  = "png"
#     webp = "webp"
#     gif  = "gif"
#     bmp  = "bmp"
#     tiff = "tiff"
#     unknown = "unknown"

# ── Artwork source service (enum for artwork_source column) ───────────────────
class ArtworkSource(enum.Enum):
    caa     = "caa"
    itunes  = "itunes"
    spotify = "spotify"
    audiodb = "audiodb"
    discogs = "discogs"
    deezer  = "deezer"
    lastfm  = "lastfm"
    manual  = "manual"






"""
MCA Meta Processor Module — Enums
==================================
These enums mirror the lookup tables in the database.
They exist to make Python code readable and type-safe.
The lookup tables are the source of truth — these are the Pythonic interface.

Every enum here corresponds to a _lookup table in the schema.
"""


# ══════════════════════════════════════════════════════════════════════════════
# RUN LEVEL
# ══════════════════════════════════════════════════════════════════════════════

class ProcessorStatus(enum.Enum):
    """Overall status of a processing run. → processor_status_lookup"""
    pending              = "pending"
    processing           = "processing"
    awaiting_user        = "awaiting_user"        # waiting for user decision at any point
    completed            = "completed"
    failed               = "failed"
    skipped              = "skipped"
    duplicate            = "duplicate"
    promoted_to_library  = "promoted_to_library"  # approved and sent to song_library


class RunTrigger(enum.Enum):
    """What caused this run to start. → run_trigger_lookup"""
    manual               = "manual"               # user explicitly added file
    folder_watcher       = "folder_watcher"        # automatic folder scan picked it up
    scheduled_rescan     = "scheduled_rescan"      # periodic rescan job
    reprocess_request    = "reprocess_request"     # user requested reprocess
    hash_change_detected = "hash_change_detected"  # file hash changed externally
    api_triggered        = "api_triggered"         # triggered via MCA API


class ReprocessReason(enum.Enum):
    """Why a file was reprocessed. → reprocess_reason_lookup"""
    user_requested              = "user_requested"
    hash_changed_externally     = "hash_changed_externally"
    previous_run_failed         = "previous_run_failed"
    new_services_available      = "new_services_available"
    metadata_disputed_by_user   = "metadata_disputed_by_user"
    artwork_unsatisfactory      = "artwork_unsatisfactory"
    scheduled_refresh           = "scheduled_refresh"


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE TRACKING
# ══════════════════════════════════════════════════════════════════════════════

class PipelineStage(enum.Enum):
    """High level pipeline stages. → pipeline_stage_lookup"""
    ingest          = "ingest"
    identify        = "identify"
    metadata_fetch  = "metadata_fetch"
    resolve         = "resolve"
    artwork         = "artwork"
    save            = "save"
    picard          = "picard"
    manual_review   = "manual_review"


class PipelinePhase(enum.Enum):
    """Logical phases within stages. → pipeline_phase_lookup"""
    # ingest
    file_read           = "file_read"
    quality_check       = "quality_check"

    # identify
    mbid_check          = "mbid_check"
    tag_check           = "tag_check"
    fingerprint         = "fingerprint"
    mbid_validation     = "mbid_validation"

    # metadata_fetch
    text_search         = "text_search"
    service_chain       = "service_chain"

    # resolve
    field_merge         = "field_merge"
    field_enrich        = "field_enrich"
    user_resolve        = "user_resolve"

    # artwork
    artwork_check       = "artwork_check"
    artwork_service_chain = "artwork_service_chain"
    artwork_user_select = "artwork_user_select"

    # save
    user_approval       = "user_approval"
    file_write          = "file_write"

    # picard
    picard_send         = "picard_send"
    picard_user_action  = "picard_user_action"
    picard_receive      = "picard_receive"

    # manual_review
    review_assignment   = "review_assignment"
    review_resolution   = "review_resolution"


class PipelineStep(enum.Enum):
    """Every atomic step / flowchart node. → pipeline_step_lookup"""
    # ingest stage
    read_file_tags              = "read_file_tags"
    compute_file_hash           = "compute_file_hash"
    compute_audio_hash          = "compute_audio_hash"
    snapshot_technical_props    = "snapshot_technical_props"
    check_file_quality          = "check_file_quality"

    # identify stage
    check_has_mbid              = "check_has_mbid"
    check_has_artist_title      = "check_has_artist_title"
    check_has_isrc              = "check_has_isrc"
    acoustid_fingerprint        = "acoustid_fingerprint"
    acoustid_lookup             = "acoustid_lookup"
    validate_source_mbid        = "validate_source_mbid"
    validate_acoustid_mbid      = "validate_acoustid_mbid"
    validate_service_mbid       = "validate_service_mbid"
    validate_merge_mbid         = "validate_merge_mbid"

    # metadata_fetch stage
    musicbrainz_text_search     = "musicbrainz_text_search"
    itunes_search               = "itunes_search"
    lastfm_search               = "lastfm_search"
    spotify_search              = "spotify_search"
    discogs_search              = "discogs_search"
    audiodb_search              = "audiodb_search"
    deezer_search               = "deezer_search"
    youtube_search              = "youtube_search"

    # resolve stage
    merge_service_results       = "merge_service_results"
    enrich_metadata             = "enrich_metadata"
    present_to_user             = "present_to_user"
    user_field_decision         = "user_field_decision"
    resolve_confirmed           = "resolve_confirmed"

    # artwork stage
    check_has_artwork           = "check_has_artwork"
    check_info_for_artwork      = "check_info_for_artwork"
    art_caa_search              = "art_caa_search"
    art_itunes_search           = "art_itunes_search"
    art_spotify_search          = "art_spotify_search"
    art_audiodb_search          = "art_audiodb_search"
    art_discogs_search          = "art_discogs_search"
    art_deezer_search           = "art_deezer_search"
    art_lastfm_search           = "art_lastfm_search"
    art_local_upload            = "art_local_upload"
    art_user_selection          = "art_user_selection"

    # picard stage
    send_to_picard              = "send_to_picard"
    awaiting_picard_user_action = "awaiting_picard_user_action"
    picard_finalised            = "picard_finalised"

    # manual_review stage
    manual_review_triggered     = "manual_review_triggered"
    awaiting_user_decision      = "awaiting_user_decision"
    user_decision_made          = "user_decision_made"

    # save stage
    user_approves_save          = "user_approves_save"
    write_metadata_to_file      = "write_metadata_to_file"
    write_artwork_to_file       = "write_artwork_to_file"
    full_save                   = "full_save"
    incomplete_save             = "incomplete_save"


class PipelineDecisionType(enum.Enum):
    """Every decision diamond in the flowchart. → pipeline_decision_type_lookup"""
    has_mbid                    = "has_mbid"
    has_artist_and_title        = "has_artist_and_title"
    has_isrc                    = "has_isrc"
    mbid_valid                  = "mbid_valid"
    acoustid_found              = "acoustid_found"
    service_found               = "service_found"
    merge_has_mbid              = "merge_has_mbid"
    has_artwork                 = "has_artwork"
    has_info_for_artwork        = "has_info_for_artwork"
    artwork_service_found       = "artwork_service_found"
    user_approved_save          = "user_approved_save"
    manual_review_has_artwork_info = "manual_review_has_artwork_info"


class DecisionBranch(enum.Enum):
    """The branch taken at a decision diamond. → decision_branch_lookup"""
    yes         = "yes"
    no          = "no"
    valid       = "valid"
    invalid     = "invalid"
    found       = "found"
    not_found   = "not_found"
    ambiguous   = "ambiguous"
    approved    = "approved"
    rejected    = "rejected"
    partial     = "partial"


# ══════════════════════════════════════════════════════════════════════════════
# INGEST STAGE
# ══════════════════════════════════════════════════════════════════════════════

class FileFormat(enum.Enum):
    """Supported audio file formats. → file_format_lookup"""
    mp3     = "mp3"
    flac    = "flac"
    ogg     = "ogg"
    wav     = "wav"
    aac     = "aac"
    m4a     = "m4a"
    wma     = "wma"
    opus    = "opus"
    aiff    = "aiff"
    ape     = "ape"
    unknown = "unknown"


class FileQualityFlag(enum.Enum):
    """Quality issues detected at ingest. → file_quality_flag_lookup"""
    too_short           = "too_short"           # duration below threshold
    too_large           = "too_large"           # file size above threshold
    corrupt             = "corrupt"             # file unreadable or damaged
    unsupported_format  = "unsupported_format"  # format not in supported list
    low_bitrate         = "low_bitrate"         # bitrate below acceptable threshold
    no_audio_stream     = "no_audio_stream"     # file has no audio data
    permission_denied   = "permission_denied"   # cannot read file
    zero_duration       = "zero_duration"       # duration is zero


class HashChangedBy(enum.Enum):
    """Who or what changed the file hash. → hash_changed_by_lookup"""
    software = "software"   # MCA or another known application
    external = "external"   # unknown external change


# ══════════════════════════════════════════════════════════════════════════════
# IDENTIFY / MBID
# ══════════════════════════════════════════════════════════════════════════════

class MBIDSource(enum.Enum):
    """Where an MBID came from. → mbid_source_lookup"""
    file_tags    = "file_tags"
    acoustid     = "acoustid"
    musicbrainz  = "musicbrainz"
    itunes       = "itunes"
    lastfm       = "lastfm"
    spotify      = "spotify"
    discogs      = "discogs"
    audiodb      = "audiodb"
    deezer       = "deezer"
    youtube      = "youtube"
    merge        = "merge"
    manual       = "manual"


class MBIDValidationResult(enum.Enum):
    """Result of an MBID validation attempt. → mbid_validation_result_lookup"""
    valid       = "valid"
    invalid     = "invalid"
    not_found   = "not_found"
    ambiguous   = "ambiguous"
    api_error   = "api_error"


class AcoustIDResult(enum.Enum):
    """Result of an AcoustID fingerprint lookup. → acoustid_result_lookup"""
    found       = "found"
    not_found   = "not_found"
    ambiguous   = "ambiguous"
    error       = "error"


# ══════════════════════════════════════════════════════════════════════════════
# METADATA FETCH STAGE
# ══════════════════════════════════════════════════════════════════════════════

class Service(enum.Enum):
    """All external services available in this module. → service_lookup"""
    musicbrainz  = "musicbrainz"
    acoustid     = "acoustid"
    itunes       = "itunes"
    lastfm       = "lastfm"
    spotify      = "spotify"
    discogs      = "discogs"
    audiodb      = "audiodb"
    deezer       = "deezer"
    youtube      = "youtube"
    caa          = "caa"      # Cover Art Archive
    picard       = "picard"   # local desktop app, not an API


class ServiceResult(enum.Enum):
    """Result of a service metadata search. → service_result_lookup"""
    fully_found     = "fully_found"
    partially_found = "partially_found"
    not_found       = "not_found"
    error           = "error"
    skipped         = "skipped"     # user did not consent or service bypassed


# ══════════════════════════════════════════════════════════════════════════════
# ARTWORK STAGE
# ══════════════════════════════════════════════════════════════════════════════

class ArtworkSource(enum.Enum):
    """Where artwork was sourced from. → artwork_source_lookup"""
    caa      = "caa"
    itunes   = "itunes"
    spotify  = "spotify"
    audiodb  = "audiodb"
    discogs  = "discogs"
    deezer   = "deezer"
    lastfm   = "lastfm"
    manual   = "manual"     # user uploaded from local disk


class ArtworkFormat(enum.Enum):
    """Image format of artwork. → artwork_format_lookup"""
    jpeg    = "jpeg"
    png     = "png"
    webp    = "webp"
    gif     = "gif"
    bmp     = "bmp"
    tiff    = "tiff"
    unknown = "unknown"


# ══════════════════════════════════════════════════════════════════════════════
# SAVE STAGE
# ══════════════════════════════════════════════════════════════════════════════

class SaveType(enum.Enum):
    """Overall save outcome. → save_type_lookup"""
    full        = "full"        # all fields and artwork written
    partial     = "partial"     # user selected subset of fields
    skipped     = "skipped"     # user decided not to save


class SaveFieldStatus(enum.Enum):
    """Per-field save outcome in file_save_log. → save_field_status_lookup"""
    written         = "written"         # field successfully written to file
    skipped         = "skipped"         # user chose to skip this field
    failed          = "failed"          # write attempted but failed
    user_excluded   = "user_excluded"   # user explicitly excluded this field


# ══════════════════════════════════════════════════════════════════════════════
# PICARD
# ══════════════════════════════════════════════════════════════════════════════

class PicardAction(enum.Enum):
    """What the user did inside Picard. → picard_action_lookup"""
    accepted    = "accepted"    # user accepted Picard's suggestion as-is
    modified    = "modified"    # user accepted but made manual changes
    rejected    = "rejected"    # user rejected Picard's match
    abandoned   = "abandoned"   # user closed Picard without finishing


# ══════════════════════════════════════════════════════════════════════════════
# CONSENT
# ══════════════════════════════════════════════════════════════════════════════

class ConsentType(enum.Enum):
    """What is being consented to. → consent_type_lookup"""
    service_call    = "service_call"    # calling an external metadata service
    acoustid_run    = "acoustid_run"    # running AcoustID fingerprinting
    picard_send     = "picard_send"     # sending file data to Picard
    file_write      = "file_write"      # writing metadata/artwork to file


class ConsentDecision(enum.Enum):
    """Consent outcome. → consent_decision_lookup"""
    approved = "approved"
    rejected = "rejected"
    revoked  = "revoked"


# ══════════════════════════════════════════════════════════════════════════════
# MANUAL REVIEW
# ══════════════════════════════════════════════════════════════════════════════

class ManualReviewReason(enum.Enum):
    """Why manual review was triggered. → manual_review_reason_lookup"""
    # Pipeline dead ends
    acoustid_not_found              = "acoustid_not_found"
    all_services_not_found          = "all_services_not_found"
    merge_enrich_no_mbid_found      = "merge_enrich_no_mbid_found"
    insufficient_data_for_artwork   = "insufficient_data_for_artwork"
    no_identifiers_at_all           = "no_identifiers_at_all"

    # AcoustID issues
    acoustid_low_score              = "acoustid_low_score"
    acoustid_ambiguous              = "acoustid_ambiguous"

    # MBID issues
    mbid_invalid                    = "mbid_invalid"
    mbid_mismatch_across_services   = "mbid_mismatch_across_services"
    mbid_ambiguous                  = "mbid_ambiguous"

    # Data quality
    conflicting_service_data        = "conflicting_service_data"
    missing_required_fields         = "missing_required_fields"
    suspicious_metadata             = "suspicious_metadata"
    artist_name_inconsistent        = "artist_name_inconsistent"
    title_inconsistent              = "title_inconsistent"
    album_inconsistent              = "album_inconsistent"
    year_inconsistent               = "year_inconsistent"
    genre_missing                   = "genre_missing"
    isrc_invalid                    = "isrc_invalid"
    isrc_mismatch                   = "isrc_mismatch"
    confidence_below_threshold      = "confidence_below_threshold"
    confidence_tie_between_services = "confidence_tie_between_services"
    all_services_disagree           = "all_services_disagree"

    # Duplicate
    duplicate_candidate             = "duplicate_candidate"
    duplicate_confirmed             = "duplicate_confirmed"

    # Artwork
    no_artwork_found                = "no_artwork_found"
    artwork_low_resolution          = "artwork_low_resolution"
    artwork_format_unsupported      = "artwork_format_unsupported"
    multiple_artwork_candidates     = "multiple_artwork_candidates"

    # File issues
    file_moved                      = "file_moved"
    file_corrupted                  = "file_corrupted"
    file_format_unsupported         = "file_format_unsupported"
    file_too_short                  = "file_too_short"
    hash_changed_externally         = "hash_changed_externally"

    # Service issues
    service_rate_limited            = "service_rate_limited"
    service_returned_empty          = "service_returned_empty"
    service_timeout                 = "service_timeout"
    service_conflicting_data        = "service_conflicting_data"
    service_not_consented           = "service_not_consented"

    # History
    previously_failed_multiple_times        = "previously_failed_multiple_times"
    manually_reviewed_before_and_changed    = "manually_reviewed_before_and_changed"

    # User triggered
    user_flagged                    = "user_flagged"
    user_wants_custom_value         = "user_wants_custom_value"
    user_disputes_resolved_data     = "user_disputes_resolved_data"
    user_wants_different_artwork    = "user_wants_different_artwork"
    user_wants_reprocess            = "user_wants_reprocess"


class ManualReviewResolution(enum.Enum):
    """How manual review was resolved. → manual_review_resolution_lookup"""
    resolved_by_user     = "resolved_by_user"
    skipped_by_user      = "skipped_by_user"
    escalated            = "escalated"
    marked_as_duplicate  = "marked_as_duplicate"
    marked_as_incomplete = "marked_as_incomplete"
    reprocessed          = "reprocessed"


# ══════════════════════════════════════════════════════════════════════════════
# ERRORS
# ══════════════════════════════════════════════════════════════════════════════

class ErrorCategory(enum.Enum):
    """High level error category. → error_category_lookup"""
    network  = "network"
    data     = "data"
    file     = "file"
    system   = "system"
    acoustid = "acoustid"
    auth     = "auth"


class ErrorType(enum.Enum):
    """Specific error type. → error_type_lookup"""
    # Network
    connection_timeout          = "connection_timeout"
    connection_refused          = "connection_refused"
    dns_failure                 = "dns_failure"
    ssl_error                   = "ssl_error"
    proxy_error                 = "proxy_error"
    http_400_bad_request        = "http_400_bad_request"
    http_401_unauthorized       = "http_401_unauthorized"
    http_403_forbidden          = "http_403_forbidden"
    http_404_not_found          = "http_404_not_found"
    http_408_request_timeout    = "http_408_request_timeout"
    http_429_rate_limited       = "http_429_rate_limited"
    http_500_server_error       = "http_500_server_error"
    http_502_bad_gateway        = "http_502_bad_gateway"
    http_503_unavailable        = "http_503_unavailable"
    http_504_gateway_timeout    = "http_504_gateway_timeout"

    # Data
    response_parse_error        = "response_parse_error"
    unexpected_schema           = "unexpected_schema"
    empty_response              = "empty_response"
    invalid_mbid                = "invalid_mbid"
    invalid_isrc                = "invalid_isrc"
    encoding_error              = "encoding_error"
    schema_version_mismatch     = "schema_version_mismatch"
    missing_required_field      = "missing_required_field"

    # File
    file_not_found              = "file_not_found"
    file_unreadable             = "file_unreadable"
    file_corrupt                = "file_corrupt"
    unsupported_format          = "unsupported_format"
    permission_denied           = "permission_denied"
    file_too_large              = "file_too_large"
    file_too_short              = "file_too_short"

    # System
    db_connection_error         = "db_connection_error"
    db_write_error              = "db_write_error"
    db_read_error               = "db_read_error"
    out_of_memory               = "out_of_memory"
    disk_full                   = "disk_full"
    process_killed              = "process_killed"
    unknown                     = "unknown"

    # AcoustID
    acoustid_no_match               = "acoustid_no_match"
    acoustid_low_score              = "acoustid_low_score"
    acoustid_ambiguous              = "acoustid_ambiguous"
    acoustid_api_error              = "acoustid_api_error"
    acoustid_fingerprint_failed     = "acoustid_fingerprint_failed"

    # Auth
    api_key_invalid         = "api_key_invalid"
    api_key_expired         = "api_key_expired"
    api_quota_exceeded      = "api_quota_exceeded"
    token_refresh_failed    = "token_refresh_failed"


# ══════════════════════════════════════════════════════════════════════════════
# AUDIT
# ══════════════════════════════════════════════════════════════════════════════

class AuditAction(enum.Enum):
    """Audit log action types."""
    insert = "insert"
    update = "update"
    delete = "delete"