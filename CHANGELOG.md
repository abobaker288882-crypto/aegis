# Changelog

All notable changes to Aegis. Format follows Keep a Changelog; versioning is
semantic (MAJOR.MINOR.PATCH).

## [2.1.0] — 2026-08-25

### Added
- **Regression Memory V2**: records carry guarded paths and keywords;
  `aegis regressions-for --files …` returns ranked, explainable matches
  (path-prefix > area > keyword), and `status` / `next` / `resume`
  auto-surface relevant past failures with rerun-guard hints. Capped at 5
  to prevent noise. Secret-redacted at write time.
- **`aegis verify --rerun`**: re-executes stored evidence commands and
  flags any disagreement with recorded exits — deterministic defense
  against forged or wrong recorded results (integrity failures fail
  verification).
- **`aegis archive`**: preserve a finished mission directory and start a
  new one.
- **Doctor** now flags trivial evidence commands (`true`/`echo`) that
  verify nothing.
- **Benchmark v2**: second mission (M2 "taskapi": failing test, incomplete
  feature, hidden regression, SQL injection, doc/impl mismatch, unscored
  distraction), aggregate scorer (`score_all.py`), interruption modifier,
  and validated determinism (repeated scorer runs identical; unsolved
  fixtures score 0.0).

### Fixed
- Engine: checkpoint checksum covered the payload before the file field
  existed (restore mismatch); `--project` flag clobbered by subparser
  defaults; read-only state dirs crashed instead of reporting; manual
  evidence with null exit failed validation; keyword matching used record
  text instead of changed paths (false positives).

## [2.0.0] — 2026-08-25

### Added
- **Aegis Mission Engine** (`aegis-engine/`): a persistent execution layer
  for coding missions — versioned mission state (atomic + `.bak` recovery),
  evidence ledger with git-aware staleness invalidation, derived release
  gates that refuse unevidenced completion, self-contained checksummed
  checkpoints (survive total state loss), one-command resume briefs,
  deterministic next-action ranking, blocker classification, regression and
  decision memory, deploy tracking, and a doctor with repair path.
  23 tests including corruption, tamper, concurrency, unicode/space paths,
  symlink attacks, and migration.
- **Benchmark harness** (`benchmarks/`): deterministic broken-project
  fixture (5 planted defects), objective scorer, and an A/B protocol for
  measuring agent performance with vs without Aegis. Self-run validated:
  engine gates and independent scorer agree 5/5.
- Installer now ships the engine (`~/.agents/aegis`) with the same
  backup/upgrade/uninstall guarantees.

### Changed
- `verify.sh` includes the engine test suite.
- Site updated to describe the engine (claims match shipped behavior).

## [1.1.0] — 2026-08-25

### Added
- `install.sh`: safe, idempotent installer with `--target`, `--keep`,
  `--uninstall`, timestamped backups before any replacement, refusal to touch
  non-directory obstructions, and a post-install router smoke check.
  Verified from a clean environment including paths with spaces.
- `QUICKSTART.md`: first-success path from install to observable verification.
- `verify.sh`: one command that runs every check in the repository.
- Security hardening: `build_project_graph.py` now strips query strings and
  fragments from git remote URLs (delegated-token leak path), with regression
  tests; 13 new boundary/adversarial tests for `route_task.py` (empty and
  whitespace tasks, unicode, oversize tasks, malformed JSON, conflicting
  input modes, non-boolean flags, keyword inference, override precedence).
- Trust set: LICENSE (MIT), SECURITY.md with explicit threat model,
  CONTRIBUTING.md, this changelog, and git tags for releases.

### Changed
- Site: install instructions now match the tested installer; added
  host-directory hints; social share image and metadata; branded 404.

## [1.0.0] — 2026-08-25

### Added
- `aegis-ceo-skills`: autonomous end-to-end delivery skill with mission
  graph, worker activation gates, usage governor, and release gates.
- `usage-optimizer`: usage-minimizing skill with tested deterministic router.
- `second-brain-context`: Obsidian vault context skill with project-graph
  builder (credential-sanitizing, idempotent).
- `five-year-old`: plain-language end-to-end ownership skill.
- `aegis-ceo-office-site`: product site, live at
  https://abobaker288882-crypto.github.io/ (GitHub Pages), self-contained
  with self-hosted fonts and zero third-party origins.
