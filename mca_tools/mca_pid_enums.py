import enum
class mca_pid_version(enum.Enum):
    v1 = "1"
    v2 = "2"
class pkg(enum.Enum):
    mca = "MCA"
    schema = "SCH"
    mca_tools = "MCT"

class module(enum.Enum):
    meta_processor = "MPS"
    quality_checker = "QCK"

class table_family(enum.Enum):
    file_universe = "FLU"
    meta_processor_universe = "MPU"


class TableName(enum.Enum):
    # =========================================================================
    # DATA TABLES
    # =========================================================================

    MPR = "meta_processor_runs"
    MPG = "meta_processor_reprocess_log"

    RSG = "run_stage_log"
    RPG = "run_phase_log"
    RST = "run_step_log"
    RDG = "run_decision_log"

    FIG = "file_ingest_log"
    FQG = "file_quality_check_log"

    MVG = "mbid_validation_log"

    MFG = "metadata_fetch_log"
    MFF = "metadata_fetch_fields"

    RMD = "resolved_metadata"
    RME = "resolved_metadata_extended"
    RMS = "resolved_metadata_sources"

    AFG = "artwork_fetch_log"
    ASG = "artwork_selection_log"

    FSG = "file_save_log"
    FSF = "file_save_field_log"

    PSG = "picard_session_log"

    UCG = "user_consent_log"

    MRG = "manual_review_log"
    MRF = "manual_review_field_log"

    REG = "run_error_log"

    # =========================================================================
    # LOOKUP TABLES
    # =========================================================================

    RTL = "run_trigger_lookup"

    PSL = "pipeline_stage_lookup"
    PHL = "pipeline_phase_lookup"
    PTL = "pipeline_step_lookup"

    STL = "save_type_lookup"

    SVL = "service_lookup"
    SRL = "service_result_lookup"

    MFL = "metadata_field_lookup"

    MSL = "mbid_source_lookup"
    MVL = "mbid_validation_result_lookup"

    ASL = "artwork_source_lookup"
    AFL = "artwork_format_lookup"

    CTL = "consent_type_lookup"
    CDL = "consent_decision_lookup"

    PDL = "pipeline_decision_type_lookup"
    DBL = "decision_branch_lookup"

    ECL = "error_category_lookup"
    ETL = "error_type_lookup"

    PAL = "picard_action_lookup"

    MRL = "manual_review_reason_lookup"
    MXL = "manual_review_resolution_lookup"  

    SFL = "save_field_status_lookup"

    FFL = "file_quality_flag_lookup"

    HCL = "hash_changed_by_lookup"

    RRL = "reprocess_reason_lookup"