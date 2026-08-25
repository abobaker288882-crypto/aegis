# PHASE3_SCORECARD — Aegis Mission Engine

Graded by Ox Alpha with cited evidence. 2026-08-25, Phase 3 close.

| # | Category | Grade | Evidence |
|---|----------|-------|----------|
| 1 | Mission persistence | 9 | `aegis/mission.json` schema v1, atomic writes, `.bak`, 5MB cap, symlink refusal; survives every CLI operation (state.py + tests) |
| 2 | Resume quality | 9 | `resume` brief covers goal/why/decisions/gates/stale/defects/blockers/do-not-repeat/regressions/deploy/next; exercised on dogfood + fixture interruption mid-mission |
| 3 | Evidence integrity | 9 | Evidence captured by execution (exit from process); manual claims stored UNVERIFIED and can never satisfy gates; output clipped (4KB), ANSI-stripped, secret-redacted (tested) |
| 4 | Release-gate enforcement | 9 | `complete` refused with unmet gates in tests AND against me live (rejected my buggy C4/C5 evidence in the benchmark run); decision/credential blockers block completion |
| 5 | Next-action quality | 9 | Deterministic scoring (impact/severity/deps/gate-unblocking); tests pin ordering; rationale printed; no fake precision |
| 6 | Regression memory | 8 | Mechanism works (add/list/resume-surfacing/report); 2 real regressions recorded during this phase; similarity-triggered surfacing by area is manual — noted as future work |
| 7 | Decision memory | 9 | DEC records with context/options/choice/reason/consequences/revisit-when; surfaced in every resume brief |
| 8 | Blocker handling | 9 | Classified kinds; decision/credential blockers gate completion; failure blockers enter next-action ranking; resolve flow tested |
| 9 | Change awareness | 9 | Git-based staleness: guarded-file scoping (`--files`) verified — unrelated commits keep evidence fresh, guarded changes stale it; repo-wide evidence stales on any commit (conservative by design) |
| 10 | Context-loss recovery | 9 | Checkpoints embed full state + checksum; `restore` rebuilds mission.json from checkpoint alone (test: state file deleted → restored → resume shows goal+work); orphan checkpoints detectable and restorable |
| 11 | CLI usability | 9 | 18 commands, --help everywhere, --project with spaces tested, exit codes 0/1/2 documented and consistent, clean errors (no tracebacks — tested for empty goal, readonly dir, bad flags) |
| 12 | Reliability | 9 | 24 engine tests + 30 existing = 54 green; concurrent writers keep state valid (tested); atomic rename; timeouts on git and commands |
| 13 | Security | 9 | Phase 3 threat model in SECURITY.md terms: no shell, redaction (tested incl. ghp_ tokens + ANSI), symlink refusal (tested), size caps, checksummed checkpoints (tamper test), no network; hostile-input fixture defect (eval) used in benchmark |
| 14 | Performance | 9 | Full suite 24 tests ≈ 7s; state ops are small-file JSON; checkpoint pruning caps growth at 20; 5MB state guard |
| 15 | Maintainability | 9 | 4 focused modules (~900 LOC total), stdlib-only, docstrings, mission-state dogfooded on this repo (state committed as record) |
| 16 | Installation | 9 | Installer ships engine with install/upgrade/uninstall + backups (tested incl. custom --target and engine upgrade path) |
| 17 | Documentation | 9 | aegis-engine/README.md (model, commands, security), benchmarks/PROTOCOL.md, main README + QUICKSTART updated, CHANGELOG 2.0.0 |
| 18 | Benchmarkability | 9 | Deterministic fixture (5 planted defects), objective scorer (exit-code CI-usable), A/B protocol with contamination rules; self-run: engine 5/5 == scorer 5/5 agreement; interruption mid-run exercised |
| 19 | Real-world usefulness | 8 | Engine demonstrably prevented false completion and loss of mid-mission state during this very phase (observed, documented). True A/B vs agent-without-Aegis requires an external agent run per PROTOCOL — infrastructure ready, comparative number pending |
| 20 | Product differentiation | 9 | Evidence-derived gates + git-aware staleness + resumable checksummed checkpoints are, to my knowledge, unmatched among stdlib-only agent tools; the benchmark harness makes the claim testable |

## Honest gaps (documented, not hidden)

1. Comparative A/B benchmark against an agent without Aegis (PROTOCOL.md is
   ready; requires running an external agent — outside this repository).
2. Regression memory surfaces by explicit area tags; content-similarity
   matching is future work.
3. Single-mission per project (one `aegis/` dir); multi-mission support is
   deliberately deferred until a real user needs it.
