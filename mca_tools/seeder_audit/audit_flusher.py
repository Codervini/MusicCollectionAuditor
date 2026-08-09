"""
audit_flusher.py
----------------
Reads a .done.jsonl file produced by AuditWriter and bulk inserts all
records into the seed_audit_log Postgres table in a single statement.

Called once per seeder run, after AuditWriter.finish(success=True).

Usage:
    from mca_tools.seeder_audit.audit_flusher import flush_to_postgres

    final_path = writer.finish(success=True)
    flush_to_postgres(session, final_path)
"""

import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from schema.models.seeder_audit_log import SeedAuditLog

logger = logging.getLogger(__name__)

def flush_to_postgres(session: Session, jsonl_path: Path, orphan: bool = False) -> int:
    """
    Bulk insert all records from a .done.jsonl file into seed_audit_log.

    Args:
        session:     SQLAlchemy session (from db_butler)
        jsonl_path:  Path to the .done.jsonl file produced by AuditWriter

    Returns:
        Number of rows inserted.

    Raises:
        ValueError: If the file is not a .done.jsonl file.
        FileNotFoundError: If the file doesn't exist.
    """
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Audit JSONL file not found: {jsonl_path}")

    if not orphan and not jsonl_path.name.endswith(".done.jsonl"):
        raise ValueError(f"flush_to_postgres expects a .done.jsonl file, got: {jsonl_path.name}")

    if orphan and not jsonl_path.name.endswith(".orphaned.jsonl"):
        raise ValueError(f"flush_to_postgres expects a .oprhaned.jsonl for orphan = True file, got: {jsonl_path.name}")

    records = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                logger.warning("Skipping malformed JSONL line %d in %s: %s",line_num,jsonl_path.name,e)

    if not records:
        logger.warning("No records found in %s — nothing to flush.", jsonl_path.name)
        return 0

    try:
        session.bulk_insert_mappings(SeedAuditLog, records)
        session.commit()
        logger.info("Flushed %d audit records to seed_audit_log | file=%s",len(records),jsonl_path.name,)
    except Exception as e:
        session.rollback()
        logger.error("Failed to flush audit records to Postgres | file=%s | error=%s",jsonl_path.name,e,)
        raise
        return -1

    return len(records)
