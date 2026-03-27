import enum

# ══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ══════════════════════════════════════════════════════════════════════════════

# ── Overall processing status of a file in this module ───────────────────────
class ProcessorStatus(enum.Enum):
    pending             = "pending"
    processing          = "processing"
    awaiting_user       = "awaiting_user"       # waiting for user decision
    completed           = "completed"
    failed              = "failed"
    skipped             = "skipped"
    duplicate           = "duplicate"
    promoted_to_library = "promoted_to_library" # user approved, sent to song_library

# ── High level pipeline stage (category) ─────────────────────────────────────
class PipelineStage(enum.Enum):
    read_file            = "read_file"
    mbid_validation      = "mbid_validation"
    acoustid             = "acoustid"
    service_search       = "service_search"
    merge_enrich         = "merge_enrich"
    picard               = "picard"
    artwork_search       = "artwork_search"
    manual_review        = "manual_review"
    finalize             = "finalize"

# ── Fine grained pipeline step (every node in the flowchart) ─────────────────
class PipelineStep(enum.Enum):
    # read_file stage
    read_file_tags              = "read_file_tags"
    check_has_mbid              = "check_has_mbid"
    check_has_artist_title      = "check_has_artist_title"

    # mbid_validation stage
    validate_source_mbid        = "validate_source_mbid"
    validate_acoustid_mbid      = "validate_acoustid_mbid"
    validate_service_mbid       = "validate_service_mbid"
    validate_merge_mbid         = "validate_merge_mbid"

    # acoustid stage
    acoustid_fingerprint        = "acoustid_fingerprint"
    acoustid_lookup             = "acoustid_lookup"

    # service_search stage
    musicbrainz_text_search     = "musicbrainz_text_search"
    itunes_search               = "itunes_search"
    lastfm_search               = "lastfm_search"
    spotify_search              = "spotify_search"
    discogs_search              = "discogs_search"
    audiodb_search              = "audiodb_search"
    deezer_search               = "deezer_search"
    youtube_search              = "youtube_search"

    # merge_enrich stage
    merge_service_results       = "merge_service_results"
    enrich_metadata             = "enrich_metadata"
    check_merge_has_mbid        = "check_merge_has_mbid"

    # picard stage
    send_to_picard              = "send_to_picard"
    awaiting_picard_user_action = "awaiting_picard_user_action"
    picard_finalised            = "picard_finalised"

    # artwork_search stage
    check_has_artwork           = "check_has_artwork"
    art_caa_search              = "art_caa_search"
    art_itunes_search           = "art_itunes_search"
    art_spotify_search          = "art_spotify_search"
    art_audiodb_search          = "art_audiodb_search"
    art_discogs_search          = "art_discogs_search"
    art_deezer_search           = "art_deezer_search"
    art_lastfm_search           = "art_lastfm_search"

    # manual_review stage
    manual_review_triggered     = "manual_review_triggered"
    awaiting_user_decision      = "awaiting_user_decision"
    user_decision_made          = "user_decision_made"
    check_artwork_sufficient    = "check_artwork_sufficient"

    # finalize stage
    full_save                   = "full_save"
    incomplete_save             = "incomplete_save"

# ── Where did the MBID input come from ───────────────────────────────────────
class MBIDSource(enum.Enum):
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

# ── Result of an MBID validation attempt ─────────────────────────────────────
class MBIDValidationResult(enum.Enum):
    valid         = "valid"
    invalid       = "invalid"
    not_found     = "not_found"
    ambiguous     = "ambiguous"
    api_error     = "api_error"

# ── Services available in this module ────────────────────────────────────────
class Service(enum.Enum):
    musicbrainz  = "musicbrainz"
    acoustid     = "acoustid"
    itunes       = "itunes"
    lastfm       = "lastfm"
    spotify      = "spotify"
    discogs      = "discogs"
    audiodb      = "audiodb"
    deezer       = "deezer"
    youtube      = "youtube"
    caa          = "caa"          # Cover Art Archive
    picard       = "picard"       # local, not an API

# ── Result of a service metadata search ──────────────────────────────────────
class ServiceResult(enum.Enum):
    fully_found     = "fully_found"
    partially_found = "partially_found"
    not_found       = "not_found"
    error           = "error"
    skipped         = "skipped"   # user did not consent

# ── Result of an AcoustID lookup ─────────────────────────────────────────────
class AcoustidResult(enum.Enum):
    found       = "found"
    not_found   = "not_found"
    ambiguous   = "ambiguous"
    error       = "error"

# ── Who changed the file hash ─────────────────────────────────────────────────
class HashChangedBy(enum.Enum):
    software = "software"
    external = "external"

# ── How the file was saved at the end ────────────────────────────────────────
class SaveType(enum.Enum):
    full       = "full"
    incomplete = "incomplete"

# ── User roles ────────────────────────────────────────────────────────────────
class UserRole(enum.Enum):
    owner    = "owner"
    trusted  = "trusted"
    readonly = "readonly"

# ── Service consent decision per file ────────────────────────────────────────
class ConsentDecision(enum.Enum):
    approved = "approved"
    rejected = "rejected"
    revoked  = "revoked"

# ── Manual review trigger reasons ────────────────────────────────────────────
class ManualReviewReason(enum.Enum):
    # Pipeline dead ends
    acoustid_not_found              = "acoustid_not_found"
    all_services_not_found          = "all_services_not_found"
    merge_enrich_no_mbid_found      = "merge_enrich_no_mbid_found"
    insufficient_data_for_artwork   = "insufficient_data_for_artwork"

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

    # Confidence issues
    confidence_below_threshold      = "confidence_below_threshold"
    confidence_tie_between_services = "confidence_tie_between_services"
    all_services_disagree           = "all_services_disagree"

    # History
    previously_failed_multiple_times         = "previously_failed_multiple_times"
    manually_reviewed_before_and_changed     = "manually_reviewed_before_and_changed"

    # User triggered
    user_flagged                    = "user_flagged"
    user_wants_custom_value         = "user_wants_custom_value"
    user_disputes_resolved_data     = "user_disputes_resolved_data"
    user_wants_different_artwork    = "user_wants_different_artwork"
    user_wants_reprocess            = "user_wants_reprocess"

# ── Manual review resolution ──────────────────────────────────────────────────
class ManualReviewResolution(enum.Enum):
    resolved_by_user     = "resolved_by_user"
    skipped_by_user      = "skipped_by_user"
    escalated            = "escalated"
    marked_as_duplicate  = "marked_as_duplicate"
    marked_as_incomplete = "marked_as_incomplete"
    reprocessed          = "reprocessed"

# ── Error categories ──────────────────────────────────────────────────────────
class ErrorCategory(enum.Enum):
    network  = "network"
    data     = "data"
    file     = "file"
    system   = "system"
    acoustid = "acoustid"
    auth     = "auth"

# ── Exact error types ─────────────────────────────────────────────────────────
class ErrorType(enum.Enum):
    # Network
    connection_timeout      = "connection_timeout"
    connection_refused      = "connection_refused"
    dns_failure             = "dns_failure"
    ssl_error               = "ssl_error"
    proxy_error             = "proxy_error"
    http_400_bad_request    = "http_400_bad_request"
    http_401_unauthorized   = "http_401_unauthorized"
    http_403_forbidden      = "http_403_forbidden"
    http_404_not_found      = "http_404_not_found"
    http_408_request_timeout = "http_408_request_timeout"
    http_429_rate_limited   = "http_429_rate_limited"
    http_500_server_error   = "http_500_server_error"
    http_502_bad_gateway    = "http_502_bad_gateway"
    http_503_unavailable    = "http_503_unavailable"
    http_504_gateway_timeout = "http_504_gateway_timeout"

    # Data
    response_parse_error    = "response_parse_error"
    unexpected_schema       = "unexpected_schema"
    empty_response          = "empty_response"
    invalid_mbid            = "invalid_mbid"
    invalid_isrc            = "invalid_isrc"
    encoding_error          = "encoding_error"
    schema_version_mismatch = "schema_version_mismatch"
    missing_required_field  = "missing_required_field"

    # File
    file_not_found          = "file_not_found"
    file_unreadable         = "file_unreadable"
    file_corrupt            = "file_corrupt"
    unsupported_format      = "unsupported_format"
    permission_denied       = "permission_denied"
    file_too_large          = "file_too_large"
    file_too_short          = "file_too_short"

    # System
    db_connection_error     = "db_connection_error"
    db_write_error          = "db_write_error"
    db_read_error           = "db_read_error"
    out_of_memory           = "out_of_memory"
    disk_full               = "disk_full"
    process_killed          = "process_killed"
    unknown                 = "unknown"

    # AcoustID specific
    acoustid_no_match       = "acoustid_no_match"
    acoustid_low_score      = "acoustid_low_score"
    acoustid_ambiguous      = "acoustid_ambiguous"
    acoustid_api_error      = "acoustid_api_error"
    acoustid_fingerprint_failed = "acoustid_fingerprint_failed"

    # Auth
    api_key_invalid         = "api_key_invalid"
    api_key_expired         = "api_key_expired"
    api_quota_exceeded      = "api_quota_exceeded"
    token_refresh_failed    = "token_refresh_failed"

# ── Audit actions ─────────────────────────────────────────────────────────────
class AuditAction(enum.Enum):
    insert = "insert"
    update = "update"
    delete = "delete"

# ── Artwork image format ───────────────────────────────────────────────────────
class ArtworkFormat(enum.Enum):
    jpeg = "jpeg"
    png  = "png"
    webp = "webp"
    gif  = "gif"
    bmp  = "bmp"
    tiff = "tiff"
    unknown = "unknown"

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
