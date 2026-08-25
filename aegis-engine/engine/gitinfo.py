"""Safe, read-only git queries. Repository content is treated as hostile.

All subprocess calls use list argv (no shell), capped output, and timeouts.
Every function degrades gracefully when git is missing or the tree is not a
repository, returning empty/None instead of raising.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

TIMEOUT = 10
MAX_BYTES = 200_000


def _git(project: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(project), *args],
            capture_output=True,
            timeout=TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout[:MAX_BYTES].decode("utf-8", errors="replace")


def available() -> bool:
    try:
        subprocess.run(["git", "--version"], capture_output=True, timeout=TIMEOUT, check=False)
        return True
    except (OSError, subprocess.TimeoutExpired):
        return False


def is_repo(project: Path) -> bool:
    return _git(project, "rev-parse", "--is-inside-work-tree") == "true\n"


def head_commit(project: Path) -> str:
    return (_git(project, "rev-parse", "HEAD") or "").strip()


def branch(project: Path) -> str:
    return (_git(project, "branch", "--show-current") or "").strip()


def dirty_files(project: Path) -> list[str]:
    out = _git(project, "status", "--porcelain")
    if not out:
        return []
    lines = [line[3:] for line in out.splitlines() if len(line) > 3]
    # A rename line "R  old -> new" yields the whole expression; keep both sides.
    files: list[str] = []
    for name in lines:
        if " -> " in name:
            files.extend(part.strip() for part in name.split(" -> "))
        else:
            files.append(name.strip().strip('"'))
    return [f for f in files if f]


def changed_since(project: Path, commit: str) -> list[str] | None:
    """Files changed between commit and HEAD; None when unknowable."""
    if not commit or not is_repo(project):
        return None
    out = _git(project, "diff", "--name-only", "--no-color", commit, "HEAD", "--")
    if out is None:
        return None
    return [line for line in (l.strip() for l in out.splitlines()) if line]


def commit_subject(project: Path, commit: str) -> str:
    out = _git(project, "log", "-1", "--format=%s", commit)
    return (out or "").strip()


def has_commits(project: Path) -> bool:
    return bool(head_commit(project))
