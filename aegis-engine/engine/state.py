"""Mission state: versioned schema, atomic storage, validation, migration.

The state file `<project>/aegis/mission.json` is the single authoritative
source of truth for an Aegis mission. Writes are atomic (tmp + rename) and
keep a `.bak` of the last good version for corruption recovery.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
STATE_DIR_NAME = "aegis"
STATE_FILE_NAME = "mission.json"
MAX_STATE_BYTES = 5 * 1024 * 1024

KINDS_BLOCKER = ("credentials", "decision", "failure", "inconvenience")
PHASES = ("discover", "design", "build", "verify", "ship", "done")


class StateError(Exception):
    """Raised when mission state cannot be safely loaded or saved."""


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_id(prefix: str, existing) -> str:
    numbers = [int(e["id"][len(prefix):]) for e in existing
               if e["id"].startswith(prefix) and e["id"][len(prefix):].isdigit()]
    return f"{prefix}{max(numbers, default=0) + 1}"


def empty_state(goal: str, why: str = "", mission_id: str | None = None) -> dict:
    return {
        "schema": SCHEMA_VERSION,
        "mission": {
            "id": mission_id or ("m-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")),
            "goal": goal,
            "why": why,
            "created_at": now_iso(),
            "constraints": [],
            "non_goals": [],
            "phase": "discover",
            "release": "",
        },
        "criteria": [],       # {id, text, required, evidence:[], blocked_reason}
        "workstreams": [],    # {id, title, impact, effort, status, depends_on, notes}
        "defects": [],        # {id, title, severity, status, fix}
        "blockers": [],       # {id, kind, title, attempts, blocks, resolved}
        "evidence": [],       # {id, criterion, kind, command, exit, summary, commit, files, captured_at, verified}
        "decisions": [],      # {id, context, options, choice, reason, consequences, revisit_when}
        "regressions": [],    # {id, defect, cause, fix, test, area}
        "checkpoints": [],    # {n, file, commit, created_at, note}
        "deploy": {"target": "", "state": "unknown", "url": "", "last_checked_at": ""},
        "next_hint": "",
    }


def validate(state: dict) -> list[str]:
    """Return a list of problems (empty list = structurally valid)."""
    problems: list[str] = []
    if not isinstance(state, dict):
        return ["state is not an object"]
    schema = state.get("schema")
    if schema is None:
        problems.append("missing schema version")
    elif not isinstance(schema, int) or schema < 1:
        problems.append(f"invalid schema version: {schema!r}")
    mission = state.get("mission")
    if not isinstance(mission, dict):
        problems.append("missing mission object")
    else:
        if not str(mission.get("goal", "")).strip():
            problems.append("mission.goal is empty")
        if mission.get("phase") not in PHASES:
            problems.append(f"mission.phase invalid: {mission.get('phase')!r}")
    ids: set[str] = set()

    def check_id(entity: dict, prefix: str) -> None:
        eid = entity.get("id")
        if not isinstance(eid, str) or not eid.startswith(prefix):
            problems.append(f"bad id {eid!r} (expected prefix {prefix})")
        elif eid in ids:
            problems.append(f"duplicate id {eid}")
        ids.add(eid)

    for c in state.get("criteria", []):
        check_id(c, "C")
        if not str(c.get("text", "")).strip():
            problems.append(f"{c.get('id')}: empty criterion text")
    for w in state.get("workstreams", []):
        check_id(w, "W")
        if w.get("impact") not in (1, 2, 3):
            problems.append(f"{w.get('id')}: impact must be 1-3")
        if w.get("effort") not in (1, 2, 3):
            problems.append(f"{w.get('id')}: effort must be 1-3")
    for d in state.get("defects", []):
        check_id(d, "D")
    for b in state.get("blockers", []):
        check_id(b, "B")
        if b.get("kind") not in KINDS_BLOCKER:
            problems.append(f"{b.get('id')}: blocker kind invalid: {b.get('kind')!r}")
    for e in state.get("evidence", []):
        check_id(e, "E")
        if e.get("exit") is not None and not isinstance(e.get("exit"), int):
            problems.append(f"{e.get('id')}: evidence exit must be integer or null")
    for dec in state.get("decisions", []):
        check_id(dec, "DEC")
    for r in state.get("regressions", []):
        check_id(r, "R")

    evidence_ids = {e.get("id") for e in state.get("evidence", [])}
    for c in state.get("criteria", []):
        for ev in c.get("evidence", []):
            if ev not in evidence_ids:
                problems.append(f"{c.get('id')}: references missing evidence {ev}")
    return problems


def migrate(state: dict) -> tuple[dict, list[str]]:
    """Migrate older schemas to the current one. Returns (state, notes)."""
    notes: list[str] = []
    schema = state.get("schema", 0)
    if not isinstance(schema, int):
        raise StateError(f"schema version is not an integer: {schema!r}")
    if schema > SCHEMA_VERSION:
        raise StateError(
            f"state schema {schema} is newer than this engine (supports <= {SCHEMA_VERSION}); "
            "upgrade Aegis instead of downgrading state"
        )
    if schema < 1:
        # v0 was never shipped; treat as v1 with defaults for missing keys.
        base = empty_state(str(state.get("mission", {}).get("goal", "imported mission")))
        merged = {**base, **state}
        merged["schema"] = SCHEMA_VERSION
        base_keys = set(base)
        for key in base_keys:
            merged.setdefault(key, base[key])
        notes.append("migrated schema 0 -> 1 (defaults filled)")
        state = merged
    return state, notes


def state_dir(project: Path) -> Path:
    return project / STATE_DIR_NAME


def state_path(project: Path) -> Path:
    return state_dir(project) / STATE_FILE_NAME


def load(project: Path, migrate_on_load: bool = True) -> tuple[dict, list[str]]:
    """Load and validate state. Returns (state, notes).

    Raises StateError with recovery guidance on corruption.
    """
    path = state_path(project)
    if path.is_symlink():
        raise StateError(f"{path} is a symlink; refusing to read it (possible attack)")
    if not path.exists():
        raise StateError(f"no mission state at {path}; run 'aegis init' first")
    size = path.stat().st_size
    if size > MAX_STATE_BYTES:
        raise StateError(
            f"state file is {size} bytes (limit {MAX_STATE_BYTES}); "
            "inspect it manually, then archive or trim aegis/"
        )
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise StateError(f"cannot read {path}: {exc}") from exc
    try:
        state = json.loads(raw)
    except json.JSONDecodeError as exc:
        bak = path.with_suffix(".json.bak")
        raise StateError(
            f"state file is corrupt ({exc.msg} at line {exc.lineno}). "
            f"Recover with: aegis doctor   (a backup may exist at {bak})"
        ) from exc
    if migrate_on_load:
        state, notes = migrate(state)
    else:
        notes = []
    problems = validate(state)
    if problems:
        raise StateError("state validation failed:\n  - " + "\n  - ".join(problems))
    return state, notes


def save(project: Path, state: dict) -> None:
    """Atomically persist state; keep a .bak of the previous good copy."""
    problems = validate(state)
    if problems:
        raise StateError("refusing to save invalid state:\n  - " + "\n  - ".join(problems))
    sdir = state_dir(project)
    if sdir.is_symlink():
        raise StateError(f"{sdir} is a symlink; refusing to write (possible attack)")
    sdir.mkdir(parents=True, exist_ok=True)
    path = state_path(project)
    if path.is_symlink():
        raise StateError(f"{path} is a symlink; refusing to overwrite (possible attack)")
    payload = json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if len(payload.encode("utf-8")) > MAX_STATE_BYTES:
        raise StateError("state exceeds size limit; archive old checkpoints/evidence first")
    tmp_name = None
    try:
        fd, tmp_name = tempfile.mkstemp(dir=sdir, prefix=".mission-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            shutil.copyfile(path, path.with_suffix(".json.bak"))
        os.replace(tmp_name, path)
    except OSError as exc:
        if tmp_name:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
        raise StateError(f"cannot write {path}: {exc}") from exc
    except BaseException:
        if tmp_name:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
        raise
