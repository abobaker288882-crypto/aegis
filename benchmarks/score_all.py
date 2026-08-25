#!/usr/bin/env python3
"""Aggregate benchmark scoring across mission directories.

Usage: score_all.py <run-root>            expects run-root/M1 and run-root/M2
Prints one JSON summary; exit 0 only when every mission is fully solved.
"""
import json
import subprocess
import sys
from pathlib import Path

MISSIONS = [("M1", "score.py"), ("M2", "score_m2.py")]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = Path(sys.argv[1])
    here = Path(__file__).parent
    summary = {}
    for name, scorer in MISSIONS:
        d = root / name
        if not d.is_dir():
            summary[name] = {"error": "missing directory"}
            continue
        r = subprocess.run([sys.executable, str(here / scorer), str(d)],
                           capture_output=True, text=True, timeout=600)
        try:
            summary[name] = json.loads(r.stdout)
        except json.JSONDecodeError:
            summary[name] = {"error": (r.stderr or "no output")[:200]}
    total = sum(m.get("fixed", 0) for m in summary.values() if isinstance(m, dict))
    possible = sum(m.get("total", 0) for m in summary.values() if isinstance(m, dict))
    summary["aggregate"] = {"fixed": total, "possible": possible,
                            "score": round(total / possible, 2) if possible else 0.0}
    print(json.dumps(summary, separators=(",", ":")))
    ok = possible > 0 and total == possible
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
