# Aegis Mission Engine

A persistent execution layer for AI coding missions. Zero dependencies
(Python 3.9+ stdlib). State lives in `<project>/aegis/mission.json`.

## The problem it solves

Long agent missions fail through amnesia (lost state), drift (goal decay),
and dishonesty (claiming completion without proof). The engine makes state,
evidence, and completion mechanical:

- **Evidence is captured, not claimed.** `aegis evidence add --run "<cmd>"`
  executes the command and records its real exit code. Free-text claims are
  stored as `UNVERIFIED` and can never satisfy a required gate.
- **Gates are derived.** A criterion passes only while fresh passing
  evidence exists. If a later commit touches the files the evidence guarded,
  the gate flips to `stale` automatically (git-based change awareness).
- **Completion refuses.** `aegis complete` exits non-zero while any required
  gate lacks fresh passing evidence, or while decision/credential blockers
  are open.
- **Resume is one command.** `aegis resume` prints the minimum brief a fresh
  session needs: goal, why, decisions, gate statuses, stale evidence, open
  defects/blockers, completed work (do-not-repeat), regression memory,
  deploy state, and the recommended next action.
- **Checkpoints survive state loss.** Each checkpoint embeds a full state
  snapshot with a checksum. If `mission.json` is deleted or corrupt,
  `aegis restore` rebuilds from the checkpoint alone.

## Commands

```
init status next verify resume checkpoint restore complete
evidence criteria workstream defect blocker regression decision
deploy doctor report
```

Every command: `--help` for flags, `--project <dir>` to operate on another
directory, exit 0 on success / 1 on failed checks / 2 on bad input or state.

## State model

`aegis/mission.json` (schema-versioned, atomic writes, `.bak` recovery):

| Section | Purpose |
|---|---|
| mission | id, goal, why, phase, constraints, non-goals, release |
| criteria | release gates; status always derived from evidence |
| workstreams / defects | prioritized via impact/severity/effort/dependencies |
| blockers | classified: credentials, decision, failure, inconvenience |
| evidence | command, exit, clipped+redacted output, commit, timestamp |
| decisions | context, options, choice, reason, revisit-when |
| regressions | defect, cause, fix, guard test, area |
| checkpoints | rolling window (20) of self-contained snapshots |
| deploy | target, state, url, last checked |

## Security model

Repository content is hostile. The engine: never uses a shell (argv lists
after `shlex.split`), strips ANSI escapes, redacts secret-like strings
(keys, tokens, private keys) before persisting anything, caps captured
output (4 KB) and state size (5 MB), refuses symlinked state paths, times
out commands and git calls, and never touches the network.

## Testing

`python3 -m unittest discover aegis-engine -p "test_*.py"` — 23 tests
covering the full lifecycle, staleness math, corruption/repair, checkpoint
tamper, state-loss recovery, secret redaction, clipping, symlink attacks,
concurrent writers, unicode/space paths, detached HEAD, migrations, and
refusals.
