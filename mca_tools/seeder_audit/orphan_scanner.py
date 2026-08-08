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

logger = logging.getLogger(__name__)

# Resolved relative to project root — adjust if your tmp/ lives elsewhere
TMP_DIR = Path(__file__).resolve().parents[2] / "tmp"


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
           name.endswith(".orphaned.jsonl"):
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
