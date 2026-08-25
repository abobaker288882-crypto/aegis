"""Regression Memory V2: explainable retrieval of historical failures.

A regression record may carry:
  paths    — file/directory prefixes it guards ("auth/", "engine/core.py")
  keywords — lowercase tokens meaningful to the failure ("token", "session")

`relevant_regressions(changed_files)` scores every record and returns the
top matches with a human-readable WHY for each. Matching is intentionally
simple and explainable: longest path-prefix wins, keyword hits add less.

Scoring:
  path match   : +6 (directory prefix) / +8 (exact file prefix)
  keyword hit  : +2 per distinct keyword found in title/cause/fix (max +6)
  area tag hit : +3 when a changed file's basename or a path segment equals
                 the area tag
Only scores > 0 are returned; results are capped (default 5) so surfacing
never becomes noise.
"""

from __future__ import annotations

from pathlib import PurePosixPath

PATH_EXACT_SCORE = 8
PATH_DIR_SCORE = 6
AREA_SCORE = 3
KEYWORD_SCORE = 2
KEYWORD_CAP = 6
DEFAULT_LIMIT = 5
MIN_SCORE = 1


def _norm(p: str) -> str:
    return PurePosixPath(p.strip().replace("\\", "/")).as_posix().lstrip("./")


def score_regression(record: dict, changed_files: list[str]) -> tuple[int, list[str]]:
    """Return (score, reasons). Deterministic and explainable."""
    score = 0
    reasons: list[str] = []
    paths = record.get("paths") or ([record["area"]] if record.get("area") else [])
    area = (record.get("area") or "").strip()

    for changed in changed_files:
        c = _norm(changed)
        base = PurePosixPath(c).name
        if area and area not in record.get("paths", []) and (
            base == area or f"{area}/" in c + "/"
        ):
            score += AREA_SCORE
            reasons.append(f"area '{area}' matches {c}")
        for guard in paths:
            g = _norm(guard)
            if not g:
                continue
            if c == g or c.startswith(g + "/"):
                score += PATH_EXACT_SCORE
                reasons.append(f"changed file {c} is guarded by path '{g}'")
            elif g.endswith("/") and c.startswith(g):
                score += PATH_DIR_SCORE
                reasons.append(f"changed file {c} is under guard '{g}'")
            elif c.startswith(g + "/"):
                score += PATH_DIR_SCORE
                reasons.append(f"changed file {c} is under guard '{g}'")

    changed_text = " ".join(_norm(c) for c in changed_files).lower()
    hits = 0
    for kw in record.get("keywords", []):
        k = str(kw).lower().strip()
        if k and k in changed_text:
            hits += 1
            if hits <= 3:
                reasons.append(f"keyword '{k}' matches the changed paths")
    score += min(hits * KEYWORD_SCORE, KEYWORD_CAP)

    # de-duplicate reasons, preserve order
    seen: set[str] = set()
    unique = [r for r in reasons if not (r in seen or seen.add(r))]
    return score, unique


def relevant_regressions(regressions: list[dict], changed_files: list[str],
                         limit: int = DEFAULT_LIMIT) -> list[dict]:
    """Top relevant regressions with WHY, highest score first (ties: id)."""
    scored = []
    for record in regressions:
        score, reasons = score_regression(record, changed_files)
        if score >= MIN_SCORE:
            scored.append({"record": record, "score": score, "why": reasons})
    scored.sort(key=lambda item: (-item["score"], item["record"].get("id", "")))
    return scored[:limit]


def surface_block(project_dir: str, regressions: list[dict],
                  changed_files: list[str]) -> str:
    """Render the auto-surfacing block used by status/next/resume."""
    matches = relevant_regressions(regressions, changed_files)
    if not matches:
        return ""
    lines = ["", "REGRESSION WATCH (you are touching code with a failure history):"]
    for m in matches:
        r = m["record"]
        guard = f" — rerun guard: {r['test']}" if r.get("test") else ""
        lines.append(f"  {r['id']} (relevance {m['score']}): {r['defect'][:80]}")
        lines.append(f"      why: {'; '.join(m['why'][:2])}{guard}")
    return "\n".join(lines)
