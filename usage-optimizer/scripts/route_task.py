#!/usr/bin/env python3
"""Deterministically select a worker for a task.

The helper is deliberately policy-only: it does not inspect accounts, estimate
tokens, or report weekly usage.  Input is either a JSON object (stdin or
``--json``) or the equivalent small set of CLI flags.  Output is one compact
JSON object with a route and the rule that selected it.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


ROUTES = ("chatgpt", "luna", "terra", "sol")
KINDS = (
    "implementation",
    "debugging",
    "review",
    "research",
    "docs",
    "formatting",
    "testing",
    "planning",
    "security",
    "other",
)
LEVELS = ("low", "medium", "high")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Choose an Aegis worker by policy.")
    parser.add_argument("--json", dest="json_input", help="JSON task object")
    parser.add_argument("--task", help="Short task description")
    parser.add_argument("--kind", choices=KINDS)
    parser.add_argument("--complexity", choices=LEVELS)
    parser.add_argument("--risk", choices=LEVELS)
    parser.add_argument("--sensitive", action="store_true")
    parser.add_argument("--requires-network", action="store_true")
    parser.add_argument("--consequential", action="store_true")
    return parser


def _fail(message: str) -> None:
    print(json.dumps({"error": message}, separators=(",", ":")), file=sys.stderr)
    raise SystemExit(2)


def _level(value: Any, field: str, default: str) -> str:
    if value is None:
        return default
    if not isinstance(value, str) or value not in LEVELS:
        _fail(f"{field} must be one of: {', '.join(LEVELS)}")
    return value


def _bool(value: Any, field: str, default: bool = False) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        _fail(f"{field} must be a boolean")
    return value


def _infer_kind(task: str) -> str:
    text = task.lower()
    terms = (
        ("security", ("security", "vulnerability", "exploit", "auth", "secret")),
        ("research", ("research", "summarize", "summary", "compare", "brainstorm", "ideate")),
        ("debugging", ("debug", "bug", "failing", "failure", "fix")),
        ("testing", ("test", "tests", "coverage")),
        ("docs", ("docs", "documentation", "readme", "document")),
        ("formatting", ("format", "formatting", "rename")),
        ("implementation", ("implement", "build", "create", "add")),
        ("planning", ("plan", "architecture", "design")),
    )
    for kind, keywords in terms:
        if any(keyword in text for keyword in keywords):
            return kind
    return "other"


def _infer_complexity(task: str, kind: str) -> str:
    text = task.lower()
    high_markers = ("end-to-end", "repository-wide", "migrate", "migration", "production", "architecture")
    if kind in {"security", "implementation", "debugging"} and any(marker in text for marker in high_markers):
        return "high"
    if kind in {"formatting", "docs", "testing"} and len(text) < 100:
        return "low"
    return "medium"


def _infer_risk(kind: str, task: str) -> str:
    text = task.lower()
    if kind == "security" or any(marker in text for marker in ("production", "deploy", "payment", "delete")):
        return "high"
    if kind in {"implementation", "debugging", "review", "testing"}:
        return "medium"
    return "low"


def _normalise(raw: dict[str, Any]) -> dict[str, Any]:
    task = raw.get("task", "")
    if not isinstance(task, str) or not task.strip():
        _fail("task must be a non-empty string")
    task = task.strip()

    kind = raw.get("kind")
    if kind is None:
        kind = _infer_kind(task)
    if not isinstance(kind, str) or kind not in KINDS:
        _fail(f"kind must be one of: {', '.join(KINDS)}")

    complexity = _level(raw.get("complexity"), "complexity", _infer_complexity(task, kind))
    risk = _level(raw.get("risk"), "risk", _infer_risk(kind, task))
    return {
        "task": task,
        "kind": kind,
        "complexity": complexity,
        "risk": risk,
        "sensitive": _bool(raw.get("sensitive"), "sensitive"),
        "requires_network": _bool(raw.get("requires_network"), "requires_network"),
        "consequential": _bool(raw.get("consequential"), "consequential"),
    }


def route(raw: dict[str, Any]) -> dict[str, str]:
    """Return the policy route for a validated task object."""
    task = _normalise(raw)
    if task["risk"] == "high" or task["kind"] == "security" or task["consequential"]:
        return {"route": "sol", "reason": "high-risk or consequential work needs strongest judgment"}
    if task["kind"] == "research" and not task["sensitive"] and not task["requires_network"]:
        return {"route": "chatgpt", "reason": "non-sensitive research or synthesis is suitable for chat"}
    if task["sensitive"]:
        return {"route": "terra", "reason": "sensitive material stays on the controlled worker path"}
    if task["complexity"] == "low" and task["risk"] == "low" and task["kind"] in {"docs", "formatting", "testing", "other"}:
        return {"route": "luna", "reason": "low-risk, low-complexity task is well specified for a lightweight worker"}
    return {"route": "terra", "reason": "normal implementation, debugging, review, or integration work"}


def _input_from_args(args: argparse.Namespace) -> dict[str, Any]:
    flag_values = {
        "task": args.task,
        "kind": args.kind,
        "complexity": args.complexity,
        "risk": args.risk,
        "sensitive": args.sensitive,
        "requires_network": args.requires_network,
        "consequential": args.consequential,
    }
    if args.json_input is not None:
        if any(value not in (None, False) for value in flag_values.values()):
            _fail("use --json or task flags, not both")
        try:
            decoded = json.loads(args.json_input)
        except json.JSONDecodeError as exc:
            _fail(f"invalid JSON: {exc.msg}")
        if not isinstance(decoded, dict):
            _fail("JSON input must be an object")
        return decoded

    if any(value not in (None, False) for value in flag_values.values()):
        return flag_values

    stdin = sys.stdin.read().strip()
    if not stdin:
        _fail("provide --json, task flags, or a JSON object on stdin")
    try:
        decoded = json.loads(stdin)
    except json.JSONDecodeError as exc:
        _fail(f"invalid JSON: {exc.msg}")
    if not isinstance(decoded, dict):
        _fail("JSON input must be an object")
    return decoded


def main() -> int:
    args = _parser().parse_args()
    result = route(_input_from_args(args))
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
