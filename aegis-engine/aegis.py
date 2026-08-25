#!/usr/bin/env python3
"""aegis — persistent execution layer for AI coding missions.

Run inside a project directory; state lives in ./aegis/mission.json.
Stdlib-only, Python 3.9+. Exit codes: 0 ok · 1 checks failed · 2 bad input/state.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engine import core, gitinfo
from engine import state as state_mod


def _fail(message: str, code: int = 2) -> int:
    print(f"error: {message}", file=sys.stderr)
    return code


def _load_or_fail(project: Path) -> dict:
    try:
        st, notes = state_mod.load(project)
        for note in notes:
            print(f"note: {note}")
        return st
    except state_mod.StateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)


def cmd_init(args, project: Path) -> int:
    if state_mod.state_path(project).exists():
        return _fail(f"mission already exists at {state_mod.state_path(project)}; "
                     "use 'aegis status' or remove aegis/ to start over")
    if not args.goal.strip():
        return _fail("--goal must not be empty")
    st = state_mod.empty_state(args.goal, args.why or "")
    st["mission"]["constraints"] = args.constraint or []
    st["mission"]["non_goals"] = args.non_goal or []
    for spec in args.criterion or []:
        required = not spec.startswith("?")
        text = spec.lstrip("?")
        if not text.strip():
            return _fail("criterion text must not be empty")
        st["criteria"].append({"id": state_mod.new_id("C", st["criteria"]),
                               "text": text, "required": required,
                               "evidence": [], "blocked_reason": None})
    try:
        state_mod.save(project, st)
    except state_mod.StateError as exc:
        return _fail(str(exc))
    print(f"mission {st['mission']['id']} created at {state_mod.state_path(project)}")
    print(f"criteria: {len(st['criteria'])}  (prefix '?' marks optional)")
    print("next: 'aegis next' or add evidence with 'aegis evidence add --run \"<cmd>\" -c C1'")
    return 0


def cmd_status(args, project: Path) -> int:
    st = _load_or_fail(project)
    report = core.verify_mission(project, st)
    m = st["mission"]
    print(f"mission   {m['id']}  phase={m['phase']}"
          + (f"  release={m['release']}" if m["release"] else ""))
    print(f"goal      {m['goal']}")
    print(f"gates     {report['required_pass']}/{report['required_total']} required pass"
          + ("  ✓ all required gates pass" if report["can_complete"] else ""))
    for row in report["criteria"]:
        mark = {"pass": "+", "stale": "~", "failed": "!", "blocked": "×", "open": " "}[row["status"]]
        req = "" if row["required"] else " (optional)"
        reasons = (" — " + "; ".join(row["reasons"])) if row["reasons"] and row["status"] != "pass" else ""
        print(f"  [{mark}] {row['status']:7} {row['id']}{req}: {row['text'][:96]}{reasons}")
    defects = [d for d in st["defects"] if d.get("status") == "open"]
    blocks = [b for b in st["blockers"] if not b.get("resolved")]
    print(f"defects   {len(defects)} open   blockers {len(blocks)} unresolved"
          + f"   checkpoints {len(st.get('checkpoints', []))}")
    deploy = st.get("deploy", {})
    if deploy.get("state") != "unknown":
        print(f"deploy    {deploy['state']}" + (f"  {deploy['url']}" if deploy.get("url") else ""))
    dirty = gitinfo.dirty_files(project)
    if dirty:
        print(f"git       {len(dirty)} uncommitted change(s); HEAD {gitinfo.head_commit(project)[:10]}")
    return 0


def cmd_next(args, project: Path) -> int:
    st = _load_or_fail(project)
    na = core.next_action(project, st)
    rec = na["recommendation"]
    g = na["gates"]
    print(f"gates: {g['required_pass']}/{g['required_total']} required pass")
    if rec is None:
        print(g["can_complete"] and "next: run 'aegis complete'" or
              "nothing recorded as actionable — add workstreams, defects, or criteria")
        return 0
    print(f"NEXT [{rec['type']} {rec['id']}] {rec['title']}")
    print(f"why:  {rec['why']}  (score {rec['score']})")
    for alt in na["alternatives"]:
        print(f"  alt [{alt['type']} {alt['id']}] {alt['title'][:80]} — {alt['why']}")
    return 0


def cmd_checkpoint(args, project: Path) -> int:
    st = _load_or_fail(project)
    cp = core.create_checkpoint(project, st, note=args.note or "",
                                tests_command=args.tests)
    st["mission"]["phase"] = args.phase or st["mission"]["phase"]
    state_mod.save(project, st)
    t = cp.get("tests")
    print(f"checkpoint #{cp['n']} written ({cp['file']})")
    print(f"  commit {cp['git']['commit'][:10] or '(no git)'}"
          f"  dirty={len(cp['git']['dirty_files'])}")
    if t:
        print(f"  tests: exit={t['exit']}  {t['summary'][:120]}")
    return 0 if (t is None or t["exit"] == 0) else 1


def cmd_resume(args, project: Path) -> int:
    st = _load_or_fail(project)
    print(core.resume_brief(project, st))
    return 0


def cmd_verify(args, project: Path) -> int:
    st = _load_or_fail(project)
    report = core.verify_mission(project, st)
    for row in report["criteria"]:
        reasons = ("; ".join(row["reasons"])) if row["reasons"] else ""
        line = f"[{row['status']:7}] {row['id']} {'REQ' if row['required'] else 'opt'} {row['text'][:90]}"
        print(line + ((" — " + reasons) if reasons else ""))
    print(f"{report['required_pass']}/{report['required_total']} required criteria pass")
    return 0 if report["can_complete"] else 1


def cmd_evidence(args, project: Path) -> int:
    st = _load_or_fail(project)
    try:
        entry, note = core.add_evidence(
            project, st, args.criterion, args.kind,
            command=args.run, manual_note=args.manual,
        )
    except ValueError as exc:
        return _fail(str(exc))
    state_mod.save(project, st)
    label = "EVIDENCE(unverified)" if not entry["verified"] else "EVIDENCE"
    print(f"{label} {entry['id']} → {entry['criterion']}  {note}")
    if entry["verified"] and entry["exit"] != 0:
        print(f"summary: {entry['summary']}")
        return 1
    return 0


def cmd_criteria(args, project: Path) -> int:
    st = _load_or_fail(project)
    if args.block:
        crit = next((c for c in st["criteria"] if c["id"] == args.block), None)
        if crit is None:
            return _fail(f"unknown criterion {args.block}")
        crit["blocked_reason"] = args.reason
        state_mod.save(project, st)
        print(f"{args.block} marked blocked: {args.reason}")
        return 0
    if args.add:
        required = not args.add.startswith("?")
        st["criteria"].append({"id": state_mod.new_id("C", st["criteria"]),
                               "text": args.add.lstrip("?"), "required": required,
                               "evidence": [], "blocked_reason": None})
        state_mod.save(project, st)
        print(f"criterion added: {st['criteria'][-1]['id']}")
    return 0


def cmd_workstream(args, project: Path) -> int:
    st = _load_or_fail(project)
    if args.done:
        w = next((x for x in st["workstreams"] if x["id"] == args.done), None)
        if w is None:
            return _fail(f"unknown workstream {args.done}")
        w["status"] = "done"
        state_mod.save(project, st)
        print(f"{args.done} marked done — will appear in DO-NOT-REPEAT on resume")
        return 0
    if args.add:
        w = {"id": state_mod.new_id("W", st["workstreams"]), "title": args.add,
             "impact": max(1, min(3, args.impact)), "effort": max(1, min(3, args.effort)),
             "status": "open", "depends_on": args.depends_on.split(",") if args.depends_on else [],
             "notes": args.notes or ""}
        st["workstreams"].append(w)
        state_mod.save(project, st)
        print(f"workstream added: {w['id']} impact={w['impact']} effort={w['effort']}")
    return 0


def cmd_defect(args, project: Path) -> int:
    st = _load_or_fail(project)
    if args.fix:
        d = next((x for x in st["defects"] if x["id"] == args.fix), None)
        if d is None:
            return _fail(f"unknown defect {args.fix}")
        d["status"] = "fixed"
        d["fix"] = args.fix_note or ""
        state_mod.save(project, st)
        print(f"{args.fix} marked fixed")
        return 0
    if args.add:
        d = {"id": state_mod.new_id("D", st["defects"]), "title": args.add,
             "severity": max(1, min(3, args.severity)), "status": "open", "fix": ""}
        st["defects"].append(d)
        state_mod.save(project, st)
        print(f"defect added: {d['id']} severity={d['severity']}")
    return 0


def cmd_blocker(args, project: Path) -> int:
    st = _load_or_fail(project)
    if args.resolve:
        b = next((x for x in st["blockers"] if x["id"] == args.resolve), None)
        if b is None:
            return _fail(f"unknown blocker {args.resolve}")
        b["resolved"] = True
        state_mod.save(project, st)
        print(f"{args.resolve} resolved")
        return 0
    if args.add:
        if args.kind not in state_mod.KINDS_BLOCKER:
            return _fail("--kind must be one of: " + ", ".join(state_mod.KINDS_BLOCKER))
        b = {"id": state_mod.new_id("B", st["blockers"]), "kind": args.kind,
             "title": args.add, "attempts": [], "blocks": args.blocks or "", "resolved": False}
        st["blockers"].append(b)
        state_mod.save(project, st)
        print(f"blocker added: {b['id']} kind={b['kind']}"
              + (" — continue independent work; revisit before completion" if b["kind"] != "failure" else ""))
    return 0


def cmd_regression(args, project: Path) -> int:
    st = _load_or_fail(project)
    if args.add:
        r = {"id": state_mod.new_id("R", st["regressions"]), "defect": args.add,
             "cause": args.cause or "", "fix": args.fix or "",
             "test": args.test or "", "area": args.area or ""}
        st["regressions"].append(r)
        state_mod.save(project, st)
        print(f"regression memory added: {r['id']} — future resumes will surface it")
    elif args.list:
        for r in st["regressions"]:
            print(f"{r['id']} [{r.get('area', '')}] {r['defect'][:90]}")
            if r.get("test"):
                print(f"    guard: {r['test']}")
    return 0


def cmd_decision(args, project: Path) -> int:
    st = _load_or_fail(project)
    if args.add:
        d = {"id": state_mod.new_id("DEC", st["decisions"]),
             "context": args.context or "", "options": (args.options or "").split("|"),
             "choice": args.choice or args.add, "reason": args.reason or "",
             "consequences": args.consequences or "", "revisit_when": args.revisit_when or ""}
        st["decisions"].append(d)
        state_mod.save(project, st)
        print(f"decision recorded: {d['id']} — resume briefs will surface it")
    elif args.list:
        for d in st["decisions"]:
            print(f"{d['id']}: chose “{d['choice']}” because {d['reason']}")
            if d.get("revisit_when"):
                print(f"    revisit when: {d['revisit_when']}")
    return 0


def cmd_deploy(args, project: Path) -> int:
    st = _load_or_fail(project)
    dep = st.setdefault("deploy", {})
    if args.state:
        dep["state"] = args.state
        dep["url"] = args.url or dep.get("url", "")
        dep["target"] = args.target or dep.get("target", "")
        dep["last_checked_at"] = state_mod.now_iso()
        state_mod.save(project, st)
        print(f"deploy state set to '{dep['state']}'")
    else:
        print(json.dumps(dep, indent=2))
    return 0


def cmd_checkpoint_restore(args, project: Path) -> int:
    cp_dir = state_mod.state_dir(project) / "checkpoints"
    available = sorted(p.name for p in cp_dir.glob("checkpoint-*.json")) if cp_dir.is_dir() else []
    if not available:
        return _fail("no checkpoints exist to restore from")
    target = args.checkpoint
    if target is None:
        target = f"checkpoints/{available[-1]}"
    elif not target.startswith("checkpoints/"):
        target = f"checkpoints/{Path(target).name}"
    if Path(target).name not in available:
        return _fail(f"checkpoint not found: {target} (have: {', '.join(available[-3:])})")
    try:
        payload = core.restore_checkpoint(project, target)
    except Exception as exc:  # noqa: BLE001
        return _fail(str(exc))
    print(f"restored mission state from {target} (checkpoint #{payload['n']}, "
          f"captured {payload['created_at']})")
    return 0


def cmd_doctor(args, project: Path) -> int:
    report = core.doctor(project)
    for f in report["findings"]:
        print(f"[{f['severity']:5}] {f['code']}: {f['message']}")
        if f.get("hint"):
            print(f"        hint: {f['hint']}")
    if report["findings"]:
        print(f"doctor: {len(report['findings'])} finding(s)")
    else:
        print("doctor: no problems found")
    gates = report.get("gates")
    if gates:
        print(f"gates: {gates['required_pass']}/{gates['required_total']} required pass")
    healthy = report["healthy"]
    if not healthy and getattr(args, "repair", False):
        bak = state_mod.state_path(project).with_suffix(".json.bak")
        if bak.exists():
            shutil_copy(bak, state_mod.state_path(project))
            print(f"repair: restored {state_mod.state_path(project)} from backup")
            report2 = core.doctor(project)
            print(f"doctor after repair: {'healthy' if report2['healthy'] else 'still unhealthy'}")
            return 0 if report2["healthy"] else 1
        print("repair: no backup available")
    return 0 if healthy else 1


def shutil_copy(src: Path, dst: Path) -> None:
    import shutil
    shutil.copyfile(src, dst)


def cmd_complete(args, project: Path) -> int:
    st = _load_or_fail(project)
    report = core.verify_mission(project, st)
    unmet = [r for r in report["criteria"] if r["required"] and r["status"] != "pass"]
    open_blocks = [b for b in st["blockers"] if not b.get("resolved") and b["kind"] in ("decision", "credentials")]
    if unmet:
        print("cannot complete: required gates without fresh passing evidence:", file=sys.stderr)
        for row in unmet:
            print(f"  {row['id']} [{row['status']}] {row['text'][:100]}", file=sys.stderr)
        return 1
    if open_blocks and not args.force:
        print("cannot complete: unresolved decision/credential blockers:", file=sys.stderr)
        for b in open_blocks:
            print(f"  {b['id']} {b['title'][:100]}", file=sys.stderr)
        print("(resolve them, or use --force to accept documented risk)", file=sys.stderr)
        return 1
    st["mission"]["phase"] = "done"
    core.create_checkpoint(project, st, note="mission complete")
    state_mod.save(project, st)
    print(f"mission {st['mission']['id']} COMPLETE. All {report['required_total']} required "
          "gates hold fresh passing evidence.")
    return 0


def cmd_report(args, project: Path) -> int:
    st = _load_or_fail(project)
    report = core.verify_mission(project, st)
    lines = ["# Aegis mission report", "",
             f"- **Mission:** {st['mission']['id']} — {st['mission']['goal']}",
             f"- **Phase:** {st['mission']['phase']}",
             f"- **Gates:** {report['required_pass']}/{report['required_total']} required pass",
             "", "| Criterion | Required | Status | Evidence |", "|---|---|---|---|"]
    ev_by_id = {e["id"]: e for e in st["evidence"]}
    for row in report["criteria"]:
        crit = next(c for c in st["criteria"] if c["id"] == row["id"])
        ev_cells = []
        for eid in crit.get("evidence", []):
            e = ev_by_id[eid]
            state = "fresh" if core._freshness(Path.cwd(), e) in ("fresh", "aged-ok") \
                else core._freshness(Path.cwd(), e)
            ev_cells.append(f"{eid} ({state}{'' if e.get('verified') else ', UNVERIFIED'})")
        lines.append(f"| {row['id']} {row['text'][:70]} | {'req' if row['required'] else 'opt'} "
                     f"| {row['status']} | {', '.join(ev_cells) or '—'} |")
    if st.get("regressions"):
        lines += ["", "## Regression memory", ""]
        lines += [f"- **{r['id']}** {r['defect']} — cause: {r.get('cause', '?')}; "
                  f"guard: {r.get('test') or 'none'}" for r in st["regressions"]]
    print("\n".join(lines))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aegis", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--project", default=None,
                        help="project directory (default: current directory)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init", parents=[parent], help="create mission state in ./aegis/")
    sp.add_argument("--goal", required=True)
    sp.add_argument("--why", default="")
    sp.add_argument("--constraint", action="append")
    sp.add_argument("--non-goal", dest="non_goal", action="append")
    sp.add_argument("--criterion", action="append", metavar="TEXT|'?TEXT' (optional)",
                    help="release gate; prefix '?' for optional")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("status", parents=[parent], help="mission summary with derived gate statuses")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("next", parents=[parent], help="highest-value next action with rationale")
    sp.set_defaults(func=cmd_next)

    sp = sub.add_parser("verify", parents=[parent], help="recompute all gate statuses and staleness")
    sp.set_defaults(func=cmd_verify)

    sp = sub.add_parser("resume", parents=[parent], help="minimum context brief to continue any session")
    sp.set_defaults(func=cmd_resume)

    sp = sub.add_parser("checkpoint", parents=[parent], help="capture resumable snapshot (with optional test run)")
    sp.add_argument("--note", default="")
    sp.add_argument("--tests", help="command whose exit becomes the checkpoint's test result")
    sp.add_argument("--phase", choices=list(state_mod.PHASES))
    sp.set_defaults(func=cmd_checkpoint)

    sp = sub.add_parser("restore", parents=[parent], help="restore mission state from a checkpoint")
    sp.add_argument("--checkpoint", help="checkpoint path (default: latest)")
    sp.set_defaults(func=cmd_checkpoint_restore)

    sp = sub.add_parser("complete", parents=[parent], help="finish mission; refuses while required gates are unmet")
    sp.add_argument("--force", action="store_true",
                    help="accept documented decision/credential blockers")
    sp.set_defaults(func=cmd_complete)

    sp = sub.add_parser("evidence", parents=[parent], help="record verification evidence")
    sp.add_argument("add", nargs="?", const=True, help="(subaction: add)")
    g = sp.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", help="command to execute now; its exit code IS the evidence")
    g.add_argument("--manual", help="free-text claim; stored as UNVERIFIED")
    sp.add_argument("-c", "--criterion", required=True)
    sp.add_argument("-k", "--kind", default="test",
                    choices=["test", "build", "manual", "deploy", "http", "security", "migration"])
    sp.set_defaults(func=cmd_evidence)

    sp = sub.add_parser("criteria", parents=[parent], help="add or block release criteria")
    sp.add_argument("--add", help="text; prefix '?' for optional")
    sp.add_argument("--block", metavar="ID")
    sp.add_argument("--reason", help="why blocked (used with --block)")
    sp.set_defaults(func=cmd_criteria)

    sp = sub.add_parser("workstream", parents=[parent], help="add or close a unit of work")
    sp.add_argument("--add", help="title")
    sp.add_argument("--impact", type=int, default=2, help="1-3 user impact")
    sp.add_argument("--effort", type=int, default=2, help="1-3 relative effort")
    sp.add_argument("--depends-on", dest="depends_on", help="comma-separated workstream ids")
    sp.add_argument("--notes", help='mention gate ids like C2 when this unblocks them')
    sp.add_argument("--done", metavar="ID", help="mark workstream done")
    sp.set_defaults(func=cmd_workstream)

    sp = sub.add_parser("defect", parents=[parent], help="track a defect until fixed")
    sp.add_argument("--add", help="title")
    sp.add_argument("--severity", type=int, default=2, help="1-3")
    sp.add_argument("--fix", metavar="ID", help="mark defect fixed")
    sp.add_argument("--fix-note", dest="fix_note", default="")
    sp.set_defaults(func=cmd_defect)

    sp = sub.add_parser("blocker", parents=[parent], help="record/resolve blockers with class and attempts")
    sp.add_argument("--add", help="title")
    sp.add_argument("--kind", default="inconvenience",
                    choices=list(state_mod.KINDS_BLOCKER))
    sp.add_argument("--blocks", help="what it blocks (W/C id or description)")
    sp.add_argument("--resolve", metavar="ID")
    sp.set_defaults(func=cmd_blocker)

    sp = sub.add_parser("regression", parents=[parent], help="remember past failures and their guards")
    sp.add_argument("--add", help="what broke")
    sp.add_argument("--cause")
    sp.add_argument("--fix")
    sp.add_argument("--test", help="test/command that now guards against it")
    sp.add_argument("--area")
    sp.add_argument("--list", action="store_true")
    sp.set_defaults(func=cmd_regression)

    sp = sub.add_parser("decision", parents=[parent], help="record architectural/product decisions")
    sp.add_argument("--add", help="short name of the decision")
    sp.add_argument("--context")
    sp.add_argument("--options", help="options considered, '|'-separated")
    sp.add_argument("--choice")
    sp.add_argument("--reason")
    sp.add_argument("--consequences")
    sp.add_argument("--revisit-when", dest="revisit_when")
    sp.add_argument("--list", action="store_true")
    sp.set_defaults(func=cmd_decision)

    sp = sub.add_parser("deploy", parents=[parent], help="record deployment state")
    sp.add_argument("--state", choices=["pending", "deployed", "failed", "rolled-back"])
    sp.add_argument("--url")
    sp.add_argument("--target")
    sp.set_defaults(func=cmd_deploy)

    sp = sub.add_parser("doctor", parents=[parent], help="diagnose and repair mission health")
    sp.add_argument("--repair", action="store_true", help="restore corrupt state from .bak")
    sp.set_defaults(func=cmd_doctor)

    sp = sub.add_parser("report", parents=[parent], help="markdown mission report (for PRs/handoffs)")
    sp.set_defaults(func=cmd_report)
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    project = Path(args.project or ".").expanduser()
    try:
        return args.func(args, project)
    except state_mod.StateError as exc:
        return _fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
