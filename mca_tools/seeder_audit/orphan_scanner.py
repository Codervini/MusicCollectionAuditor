"""
orphan_scanner.py
-----------------
Called at the top of every seeder run before anything else.

Scans tmp/ for plain .jsonl files (no .done / .failed / .orphaned suffix)
and renames them to .orphaned.jsonl.

A plain .jsonl file means the seeder process was hard-killed before it could
rename itself — these are unresolved runs with unknown completion state.
"""

import logging
from pathlib import Path
from .audit_flusher import flush_to_postgres
from sqlalchemy.orm import Session
from schema.base import SESSION_MANAGER
from mca.core.logger import set_logger
# import traceback
logger = set_logger(__name__)

# Resolved relative to project root — adjust if your tmp/ lives elsewhere
TMP_DIR = Path(__file__).resolve().parents[2] / "tmp"

def orphan_handler(session : Session ,recent_orphan_scan_limit : int = 1):
    # traceback.print_stack()
    files = sorted(TMP_DIR.glob("*.orphaned.jsonl"),reverse=True,key=lambda f:f.stat().st_mtime)[:recent_orphan_scan_limit]
    # print(type(files))
    if not files:
        logger.warning("No orphaned JSONL detected!")
        return
    
    for i in files:
    #    print(i)
       logger.info("Orphaned JSONL detected, attempting to insert to log: %s", i)
       a = flush_to_postgres(session,i,orphan=True)
       if a > 0:
           logger.info("Orphaned JSONL inserted to log: %s with %d records", i,a)
           new_name = i.with_suffix("").with_suffix(".orphaned.saved.jsonl")
           i.rename(new_name)
           logger.info(f"Orphaned JSONL renamed to: {new_name}")
       elif a == 0:
           logger.warning("Orphaned JSONL failed to insert to log because it has no records in it: %s", i)
           new_name = i.with_suffix("").with_suffix(".orphaned.empty.jsonl")
           i.rename(new_name)
           logger.info(f"Orphaned JSONL renamed to: {new_name}")
       elif a == -1:
           logger.error("Orphaned JSONL failed to insert to log due to some problem: %s", i,stack_info=True)
           new_name = i.with_suffix("").with_suffix("sus.orphaned.jsonl")
           i.rename(new_name)
           logger.info(f"Orphaned JSONL renamed to: {new_name}")
           
           
with SESSION_MANAGER() as session:
    orphan_handler(session,1)

def scan_for_orphans() -> list[Path]:
    """
    Scan tmp/ for orphaned .jsonl files and rename them to .orphaned.jsonl.

    Returns a list of paths that were renamed, so the caller can log or
    alert on them if needed.

    Safe to call even if tmp/ doesn't exist yet — it will be created.
    """
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    orphaned = []

    for path in TMP_DIR.glob("*.jsonl"):
        # Skip already-resolved files
        name = path.name
        if name.endswith(".done.jsonl") or \
           name.endswith(".failed.jsonl") or \
           name.endswith(".orphaned.jsonl") or \
           name.endswith(".orphaned.saved.jsonl") or \
           name.endswith(".orphaned.empty.jsonl") or \
           name.endswith(".sus.orphaned.jsonl"):
            continue

        # Plain .jsonl — orphaned run
        new_path = path.with_suffix("").with_suffix(".orphaned.jsonl")
        path.rename(new_path)
        orphaned.append(new_path)
        logger.warning("Orphaned seeder run detected and marked: %s", new_path.name)

    if orphaned:
        logger.warning(
            "%d orphaned seeder run(s) found in tmp/. "
            "These runs were hard-killed and their audit records may be incomplete. "
            "Inspect the .orphaned.jsonl files manually.",
            len(orphaned),
        )

    return orphaned
