from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from schema.base import Base


class SeedAuditLog(Base):
    """
    Audit trail for all seeder operations across the MCA project.
    Records every insert / skip / failed decision made by any seeder run.
    Populated via bulk insert from a JSONL temp file after each seeder run completes.
    """

    __tablename__ = "seed_audit_log"
    # __table_args__ = {"schema": "meta"}

    id          = Column(Integer, primary_key=True, autoincrement=True)

    # --- Run-level fields (same across all rows in one seeder execution) ---
    run_id      = Column(String(128),nullable=False, index=True, comment="Unique run identifier — e.g. 20260808_143022_seed_lookups")
    seeder_name = Column(String(128),nullable=False,index=True,comment="Name of the seeder script that ran — e.g. seed_lookups",)

    # --- Row-level fields ---
    row_number  = Column(Integer,nullable=False,comment="Sequential position of this record within the run (1-based)",)
    table_name  = Column(String(128),nullable=False,comment="DB table the operation targeted — e.g. lkp_status",)
    row_key     = Column(String(256),nullable=False,comment="Human-readable seed key — e.g. status.active",)
    status      = Column(String(32),nullable=False,index=True,comment="Operation outcome: inserted | skipped | failed",)
    error_msg   = Column(Text,nullable=True,comment="Exception message if status=failed; null otherwise",)
    duration_ms = Column(Integer,nullable=True,comment="Time taken for the operation in milliseconds",)
    operated_at = Column(TIMESTAMP(timezone=True),nullable=False,default=func.now(),comment="Timestamp when the operation was executed",)