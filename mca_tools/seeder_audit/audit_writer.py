"""
audit_writer.py
---------------
Opened once at the start of a seeder run. Appends one JSONL line per
operation as the seeder loops. On finish, renames the file to either
.done.jsonl (success) or .failed.jsonl (error).

Usage:
    writer = AuditWriter(seeder_name="seed_lookups")

    writer.record(
        table_name="lkp_status",
        row_key=id,
        mca_pid="MP-ST-...",   # or None if skipped
        status="inserted",     # inserted | skipped | failed
        error_msg=None,
        duration_ms=4,
    )

    writer.finish(success=True)   # or False on error
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from .audit_flusher import flush_to_postgres
from .orphan_scanner import scan_for_orphans, orphan_handler
logger = logging.getLogger(__name__)

TMP_DIR = Path(__file__).resolve().parents[2] / "tmp"


class AuditWriter:
    def __init__(self, session, seeder_name: str):
        scan_for_orphans()
        orphan_handler(session)
        TMP_DIR.mkdir(parents=True, exist_ok=True)

        self.seeder_name = seeder_name
        self.timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.run_id = f"{self.timestamp}_{seeder_name}"
        self._row_counter = 0
        self._finished = False

        # Active file — plain .jsonl while run is in progress
        self._active_path = TMP_DIR / f"seed_run_{self.run_id}.jsonl"
        self._file = open(self._active_path, "a", encoding="utf-8")

        logger.info("AuditWriter started | run_id=%s | file=%s",self.run_id,self._active_path.name,)

    def record(
            self,
            table_name: str,
            row_key: str,
            status: str,
            mca_pid: str | None = None,
            error_msg: str | None = None,
            duration_ms: int | None = None,
        ) -> None:
        """
        Append one audit record as a JSONL line.

        Args:
            table_name:  DB table targeted — e.g. "lkp_status"
            row_key:     Row key — e.g. mbid or id
            status:      "inserted" | "skipped" | "failed"
            mca_pid:     MCA Provenance ID if inserted; None otherwise
            error_msg:   Exception message if failed; None otherwise
            duration_ms: Operation time in ms; None if not measured
        """
        if self._finished:
            raise RuntimeError("AuditWriter.record() called after finish() — writer is closed.")

        self._row_counter += 1

        record = {
            "run_id": self.run_id,
            "seeder_name": self.seeder_name,
            "row_number": self._row_counter,
            "table_name": table_name,
            "row_key": row_key,
            "mca_pid": mca_pid,
            "status": status,
            "error_msg": error_msg,
            "duration_ms": duration_ms,
            "operated_at": datetime.now(tz=timezone.utc).isoformat(),
        }

        self._file.write(json.dumps(record) + "\n")
        self._file.flush()  # ensure line hits disk immediately

    def finish(self, success: bool = True) -> Path:
        """
        Close the file and rename it to .done.jsonl or .failed.jsonl.

        Returns the final path so the caller can pass it to AuditFlusher.
        """
        if self._finished:
            raise RuntimeError("AuditWriter.finish() called more than once.")

        self._file.close()
        self._finished = True

        suffix = "done" if success else "failed"
        final_path = TMP_DIR / f"seed_run_{self.run_id}.{suffix}.jsonl"
        self._active_path.rename(final_path)

        logger.info("AuditWriter finished | run_id=%s | status=%s | rows=%d | file=%s",self.run_id,suffix,self._row_counter,final_path.name)

        flush_to_postgres(final_path)

    @property
    def row_count(self) -> int:
        return self._row_counter
